"""
Simple BigQuery Agent using LangGraph and Gemini.
Uses Application Default Credentials (ADC) or service account for authentication.
"""
import os
from typing import TypedDict, Annotated, Sequence
from langgraph.graph import StateGraph, END, START
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from langchain_core.tools import tool
from langgraph.graph.message import add_messages
from google.cloud import bigquery
from dotenv import load_dotenv
from schema_analyzer import schema_analyzer, get_schema_info, get_relationships
import json

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
        Query results as string
    """
    try:
        query_job = bq_client.query(sql)
        rows = [dict(row) for row in query_job.result()]
        
        if not rows:
            return "Query executed successfully but returned no results."
        
        # Return first 10 rows
        return str(rows[:10])
    except Exception as e:
        return f"Error executing query: {str(e)}"


@tool
def analyze_schema(table_name: str = None) -> str:
    """
    Analyze database schema and return detailed information.
    
    Args:
        table_name: Optional table name to analyze. If None, returns summary of all tables.
        
    Returns:
        Schema analysis as formatted string
    """
    try:
        if table_name:
            # Analyze specific table
            analysis = get_schema_info(table_name)
            
            result = f"""
📋 Table: {analysis['table_name']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Statistics:
  • Rows: {analysis['row_count']:,}
  • Size: {analysis['size_mb']} MB
  • Columns: {analysis['column_count']}

📝 Columns:
"""
            for col in analysis['columns']:
                result += f"  • {col['name']} ({col['type']}) - {col['description']}\n"
            
            # Add relationships
            relationships = get_relationships()
            if table_name in relationships:
                result += "\n🔗 Relationships:\n"
                for rel in relationships[table_name]:
                    result += f"  → {rel}\n"
            
            return result
        else:
            # Return summary
            summary = get_schema_info()
            result = f"""
📊 Database Summary: {summary['dataset']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • Tables: {summary['table_count']}
  • Total Rows: {summary['total_rows']:,}
  • Total Size: {summary['total_size_mb']} MB

📋 Tables:
"""
            for table, info in summary['tables'].items():
                result += f"  • {table}: {info['rows']:,} rows, {info['columns']} columns, {info['size_mb']} MB\n"
            
            return result
            
    except Exception as e:
        return f"Error analyzing schema: {str(e)}"


# Define the agent state
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


# Initialize the LLM with tools
# Using best practices from config/personas/default.yaml
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.1,  # Low temperature for precise SQL generation
    max_tokens=2048
)
tools = [query_bigquery, analyze_schema]
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


def call_tools(state: AgentState) -> dict:
    """Execute tool calls from the last message."""
    messages = state["messages"]
    last_message = messages[-1]
    
    tool_messages = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        
        # Find and execute the tool
        tool_map = {t.name: t for t in tools}
        if tool_name in tool_map:
            result = tool_map[tool_name].invoke(tool_args)
            tool_messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=tool_call["id"]
                )
            )
    
    return {"messages": tool_messages}


# Build the graph manually
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", call_tools)

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
graph = app  # Export for LangGraph server


def load_prompt(query: str) -> str:
    """Load the system prompt from file and format with query."""
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", "system_prompt.txt")
    with open(prompt_path, "r") as f:
        template = f.read()
    return template.format(query=query)


def run_agent(query: str) -> str:
    """
    Run the agent with a query.
    
    Args:
        query: The user's question
        
    Returns:
        The agent's response
    """
    prompt = load_prompt(query)
    initial_state = {"messages": [HumanMessage(content=prompt)]}
    result = app.invoke(initial_state)
    
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
