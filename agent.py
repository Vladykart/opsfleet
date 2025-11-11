"""
Simple BigQuery Agent using LangGraph and Gemini.
Uses Application Default Credentials (ADC) or service account for authentication.
"""
import os
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from google.cloud import bigquery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable LangSmith tracing if configured
if os.getenv("LANGCHAIN_TRACING_V2") == "true":
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "opsfleet-agent")
    print("✅ LangSmith tracing enabled")

# Initialize BigQuery client
# Will use GOOGLE_APPLICATION_CREDENTIALS if set, otherwise ADC
project_id = os.getenv("GCP_PROJECT_ID")

# Check if credentials file is specified
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if credentials_path and os.path.exists(credentials_path):
    from google.oauth2 import service_account
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    bq_client = bigquery.Client(project=project_id, credentials=credentials)
else:
    # Use ADC
    bq_client = bigquery.Client(project=project_id)


@tool
def query_bigquery(sql: str) -> str:
    """
    Execute a BigQuery SQL query and return results.
    
    Args:
        sql: The SQL query to execute
        
    Returns:
        Query results as a formatted string
    """
    try:
        query_job = bq_client.query(sql)
        results = query_job.result()
        
        # Format results
        rows = []
        for row in results:
            rows.append(dict(row))
        
        if not rows:
            return "Query executed successfully but returned no results."
        
        # Return first 10 rows
        return str(rows[:10])
    except Exception as e:
        return f"Error executing query: {str(e)}"


# Define the agent state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# Initialize the LLM with tools
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3
)
tools = [query_bigquery]
llm_with_tools = llm.bind_tools(tools)


def should_continue(state: AgentState) -> str:
    """Determine if we should continue or end."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If there are no tool calls, we're done
    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return "end"
    return "continue"


def call_model(state: AgentState) -> dict:
    """Call the LLM with the current state."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# Build the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

# Set entry point
workflow.add_edge(START, "agent")

# Add conditional edges
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "end": END
    }
)

# Add edge from tools back to agent
workflow.add_edge("tools", "agent")

# Compile the graph
app = workflow.compile()


def run_agent(query: str) -> str:
    """
    Run the agent with a user query.
    
    Args:
        query: The user's question
        
    Returns:
        The agent's response
    """
    # Create a prompt with context
    prompt = f"""You are a BigQuery data analyst. You have access to bigquery-public-data.thelook_ecommerce dataset.

Tables:
- users (id, first_name, last_name, email, country, city, created_at)
- products (id, name, category, brand, retail_price, cost)
- orders (order_id, user_id, status, created_at, shipped_at, delivered_at)
- order_items (id, order_id, user_id, product_id, sale_price, created_at)

Use fully qualified table names with backticks. Limit to 10 rows.

User question: {query}"""

    initial_state = {
        "messages": [HumanMessage(content=prompt)]
    }
    
    # Run the graph
    result = app.invoke(initial_state)
    
    # Get the final AI message
    for message in reversed(result["messages"]):
        if isinstance(message, AIMessage):
            return message.content
    
    return "No response generated"


if __name__ == "__main__":
    # Test queries
    test_queries = [
        "How many users are in the database?",
        "What are the top 5 products by retail price?",
        "Show me 5 recent orders"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        response = run_agent(query)
        print(f"Response: {response}\n")
