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
from schema_analyzer import schema_analyzer, get_schema_info, get_relationships

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
    Run the agent with a query.
    
    Args:
        query: The user's question
        
    Returns:
        The agent's response
    """
    prompt = f"""You are an expert BigQuery SQL engineer and data analyst for e-commerce analytics.

DATASET: bigquery-public-data.thelook_ecommerce

SCHEMA:
- users (id, first_name, last_name, email, country, city, created_at)
- products (id, name, category, brand, retail_price, cost)
- orders (order_id, user_id, status, created_at, shipped_at, delivered_at)
- order_items (id, order_id, user_id, product_id, sale_price, created_at)

CRITICAL SQL RULES:
1. TIMESTAMP Handling:
   - ALWAYS use: CAST(timestamp_col AS DATE) >= DATE('YYYY-MM-DD')
   - NEVER compare TIMESTAMP directly with string dates

2. Column Names:
   - products table: use "id" NOT "product_id"
   - users table: use "id" NOT "user_id"
   - orders table: "order_id", "user_id", "created_at"

3. GROUP BY + ORDER BY:
   - ORDER BY columns MUST be in GROUP BY OR aggregated
   - Use MAX(col), MIN(col), etc. for ORDER BY with GROUP BY

4. Optimization:
   - Use LIMIT for top-N queries
   - Avoid SELECT * when possible
   - Use appropriate JOINs (INNER vs LEFT)
   - Add WHERE filters before JOINs

TASK:
1. Analyze the user's question
2. Generate precise, optimized SQL query if needed
3. Execute using query_bigquery tool
4. Provide clear, professional answer

USER QUERY: {query}"""
    
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
