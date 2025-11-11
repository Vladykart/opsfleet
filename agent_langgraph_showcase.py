"""
LangGraph Showcase: Multi-Stage Agent with Conditional Routing
Demonstrates LangGraph's power: state management, conditional edges, cycles, and error recovery
"""
import os
from typing import TypedDict, Annotated, Sequence, Literal
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

if os.getenv("LANGCHAIN_TRACING_V2") == "true":
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "opsfleet-langgraph-showcase")
    print("✅ LangSmith tracing enabled")

project_id = os.getenv("GCP_PROJECT_ID")
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if credentials_path and os.path.exists(credentials_path):
    from google.oauth2 import service_account
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    bq_client = bigquery.Client(project=project_id, credentials=credentials)
else:
    bq_client = bigquery.Client(project=project_id)


@tool
def query_bigquery(sql: str) -> str:
    """Execute a BigQuery SQL query and return results."""
    try:
        query_job = bq_client.query(sql)
        rows = [dict(row) for row in query_job.result()]
        if not rows:
            return "Query executed successfully but returned no results."
        return str(rows[:10])
    except Exception as e:
        return f"Error executing query: {str(e)}"


class AgentState(TypedDict):
    """State with rich metadata for multi-stage processing"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    stage: str
    retry_count: int
    needs_clarification: bool
    plan: dict
    error: str


llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.1,
    max_tokens=2048
)
tools = [query_bigquery]
llm_with_tools = llm.bind_tools(tools)


def understanding_node(state: AgentState) -> AgentState:
    """Stage 1: Understanding - Analyze query intent and complexity"""
    messages = state["messages"]
    last_message = messages[-1].content if messages else ""
    
    prompt = f"""Analyze this query and determine:
1. Is it a data query or conversation?
2. Does it need clarification?
3. What's the complexity (simple/medium/complex)?

Query: {last_message}

Respond with: UNDERSTOOD | CLARIFY | INVALID"""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    needs_clarification = "CLARIFY" in response.content
    
    return {
        **state,
        "stage": "understanding",
        "needs_clarification": needs_clarification,
        "messages": [response]
    }


def planning_node(state: AgentState) -> AgentState:
    """Stage 2: Planning - Strategic analysis and decomposition"""
    messages = state["messages"]
    original_query = messages[0].content if messages else ""
    
    prompt = f"""Create a strategic plan for this query:

Query: {original_query}

DATASET: bigquery-public-data.thelook_ecommerce
- users (id, first_name, last_name, email, country, city, created_at)
- products (id, name, category, brand, retail_price, cost)
- orders (order_id, user_id, status, created_at, shipped_at, delivered_at)
- order_items (id, order_id, user_id, product_id, sale_price, created_at)

Create a plan with steps. Be specific about SQL queries needed."""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        **state,
        "stage": "planning",
        "plan": {"steps": response.content},
        "messages": [response]
    }


def execution_node(state: AgentState) -> AgentState:
    """Stage 3: Execution - ReAct pattern with tool calling"""
    messages = state["messages"]
    plan = state.get("plan", {})
    
    prompt = f"""Execute this plan using the query_bigquery tool:

Plan: {plan.get('steps', 'No plan')}

CRITICAL SQL RULES:
1. TIMESTAMP: Use CAST(timestamp_col AS DATE) >= DATE('YYYY-MM-DD')
2. Column Names: products.id (NOT product_id), users.id (NOT user_id)
3. GROUP BY + ORDER BY: ORDER BY columns MUST be in GROUP BY or aggregated
4. Optimization: Use LIMIT, avoid SELECT *, add WHERE before JOINs

Generate and execute the SQL query."""
    
    response = llm_with_tools.invoke([HumanMessage(content=prompt)])
    
    return {
        **state,
        "stage": "execution",
        "messages": [response]
    }


def validation_node(state: AgentState) -> AgentState:
    """Stage 4: Validation - Check result quality"""
    messages = state["messages"]
    
    last_message = messages[-1]
    if isinstance(last_message, AIMessage) and "Error" in str(last_message.content):
        return {
            **state,
            "stage": "validation",
            "error": "Query execution failed",
            "retry_count": state.get("retry_count", 0) + 1
        }
    
    return {
        **state,
        "stage": "validation",
        "error": ""
    }


def synthesis_node(state: AgentState) -> AgentState:
    """Stage 5: Synthesis - Generate insights and format response"""
    messages = state["messages"]
    original_query = messages[0].content if messages else ""
    
    tool_results = [m for m in messages if hasattr(m, 'content') and 'Error' not in str(m.content)]
    
    prompt = f"""Synthesize a professional response:

Original Query: {original_query}
Results: {tool_results[-1].content if tool_results else 'No results'}

Provide:
1. Clear answer
2. Key insights
3. Professional formatting"""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    return {
        **state,
        "stage": "synthesis",
        "messages": [response]
    }


def error_recovery_node(state: AgentState) -> AgentState:
    """Error Recovery - Self-healing with retry logic"""
    messages = state["messages"]
    error = state.get("error", "")
    retry_count = state.get("retry_count", 0)
    
    prompt = f"""Fix this error:

Error: {error}
Previous attempt: {messages[-1].content if messages else ''}

Analyze the error and generate a corrected SQL query.
Common fixes:
- Add CAST for TIMESTAMP comparisons
- Fix column names (id vs product_id)
- Add aggregation for ORDER BY with GROUP BY"""
    
    response = llm_with_tools.invoke([HumanMessage(content=prompt)])
    
    return {
        **state,
        "stage": "error_recovery",
        "error": "",
        "messages": [response]
    }


def route_after_understanding(state: AgentState) -> Literal["planning", "__end__"]:
    """Conditional routing: clarification needed or proceed"""
    if state.get("needs_clarification"):
        return "__end__"
    return "planning"


def route_after_execution(state: AgentState) -> Literal["tools", "validation"]:
    """Conditional routing: tool calls or validation"""
    last_message = state["messages"][-1]
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return "validation"


def route_after_validation(state: AgentState) -> Literal["synthesis", "error_recovery", "__end__"]:
    """Conditional routing: success, retry, or fail"""
    error = state.get("error", "")
    retry_count = state.get("retry_count", 0)
    
    if error and retry_count < 3:
        return "error_recovery"
    elif error:
        return "__end__"
    return "synthesis"


def should_continue_after_tools(state: AgentState) -> Literal["execution", "validation"]:
    """After tool execution, go back to execution or validate"""
    return "validation"


# Build the graph - THIS IS WHERE LANGGRAPH SHINES!
workflow = StateGraph(AgentState)

# Add all nodes
workflow.add_node("understanding", understanding_node)
workflow.add_node("planning", planning_node)
workflow.add_node("execution", execution_node)
workflow.add_node("tools", ToolNode(tools))
workflow.add_node("validation", validation_node)
workflow.add_node("synthesis", synthesis_node)
workflow.add_node("error_recovery", error_recovery_node)

# Define the flow with conditional routing
workflow.add_edge(START, "understanding")
workflow.add_conditional_edges("understanding", route_after_understanding)
workflow.add_edge("planning", "execution")
workflow.add_conditional_edges("execution", route_after_execution)
workflow.add_conditional_edges("tools", should_continue_after_tools)
workflow.add_conditional_edges("validation", route_after_validation)
workflow.add_edge("error_recovery", "execution")  # Retry loop!
workflow.add_edge("synthesis", END)

# Compile the graph
app = workflow.compile()


def run_agent(query: str) -> str:
    """Run the multi-stage agent"""
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "stage": "start",
        "retry_count": 0,
        "needs_clarification": False,
        "plan": {},
        "error": ""
    }
    
    result = app.invoke(initial_state)
    
    for message in reversed(result["messages"]):
        if isinstance(message, AIMessage):
            return message.content
    
    return "No response generated"


if __name__ == "__main__":
    print("🚀 LangGraph Multi-Stage Agent Showcase\n")
    print("="*60)
    
    queries = [
        "How many users are in the database?",
        "What are the top 5 products by retail price?",
        "Show me sales trends by category"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-"*60)
        response = run_agent(query)
        print(f"Response: {response}\n")
        print("="*60)
