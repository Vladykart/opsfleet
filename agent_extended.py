"""
Extended BigQuery Agent with Context Engineering Best Practices
Uses LangGraph with memory, custom state, and context management
"""
import os
import uuid
from typing import TypedDict, Annotated, Sequence, Optional, Dict, Any
from datetime import datetime
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage, SystemMessage
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langgraph.graph.message import add_messages
from langgraph.prebuilt import InjectedState
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

if os.getenv("LANGCHAIN_TRACING_V2") == "true":
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "opsfleet-extended")
    print("✅ LangSmith tracing enabled")

project_id = os.getenv("GCP_PROJECT_ID")
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if credentials_path and os.path.exists(credentials_path):
    from google.oauth2 import service_account
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    bq_client = bigquery.Client(project=project_id, credentials=credentials)
else:
    bq_client = bigquery.Client(project=project_id)


# Extended State with Context Management
class ExtendedAgentState(TypedDict):
    """Extended state with rich context management"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: str
    session_id: str
    query_history: list[str]
    schema_cache: Dict[str, Any]
    conversation_context: str
    last_query_result: Optional[str]
    error_count: int


@tool
def query_bigquery(sql: str, state: Annotated[ExtendedAgentState, InjectedState]) -> str:
    """
    Execute a BigQuery SQL query with context awareness.
    
    Args:
        sql: The SQL query to execute
        state: Injected agent state for context
    """
    try:
        # Add query to history
        query_history = state.get("query_history", [])
        query_history.append(sql)
        
        # Execute query
        query_job = bq_client.query(sql)
        rows = [dict(row) for row in query_job.result()]
        
        if not rows:
            return "Query executed successfully but returned no results."
        
        result = str(rows[:10])
        
        # Store result in state for context
        return result
        
    except Exception as e:
        error_msg = f"Error executing query: {str(e)}"
        return error_msg


@tool
def get_schema_info(table_name: str, state: Annotated[ExtendedAgentState, InjectedState]) -> str:
    """
    Get cached schema information for a table.
    
    Args:
        table_name: Name of the table
        state: Injected agent state with schema cache
    """
    schema_cache = state.get("schema_cache", {})
    
    if table_name in schema_cache:
        return f"Cached schema for {table_name}: {schema_cache[table_name]}"
    
    # Schema info from our dataset
    schemas = {
        "users": "id, first_name, last_name, email, country, city, created_at",
        "products": "id, name, category, brand, retail_price, cost",
        "orders": "order_id, user_id, status, created_at, shipped_at, delivered_at",
        "order_items": "id, order_id, user_id, product_id, sale_price, created_at"
    }
    
    return schemas.get(table_name, f"Unknown table: {table_name}")


# Initialize LLM with context-aware configuration
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.1,
    max_tokens=2048
)

tools = [query_bigquery, get_schema_info]
llm_with_tools = llm.bind_tools(tools)


def create_context_aware_prompt(state: ExtendedAgentState) -> list[BaseMessage]:
    """
    Create a context-aware prompt using conversation history and state.
    
    Best Practice: Use conversation context to maintain coherent multi-turn interactions
    """
    user_id = state.get("user_id", "unknown")
    session_id = state.get("session_id", "unknown")
    query_history = state.get("query_history", [])
    last_result = state.get("last_query_result")
    
    # Build context from history
    context_parts = []
    
    if query_history:
        recent_queries = query_history[-3:]  # Last 3 queries
        context_parts.append(f"Recent queries: {', '.join(recent_queries)}")
    
    if last_result:
        context_parts.append(f"Last result summary: {last_result[:200]}...")
    
    conversation_context = "\n".join(context_parts) if context_parts else "No previous context"
    
    system_prompt = f"""You are an expert BigQuery SQL engineer and data analyst for e-commerce analytics.

SESSION CONTEXT:
- User ID: {user_id}
- Session ID: {session_id}
- {conversation_context}

DATASET: bigquery-public-data.thelook_ecommerce

SCHEMA (cached):
- users (id, first_name, last_name, email, country, city, created_at)
- products (id, name, category, brand, retail_price, cost)
- orders (order_id, user_id, status, created_at, shipped_at, delivered_at)
- order_items (id, order_id, user_id, product_id, sale_price, created_at)

CRITICAL SQL RULES:
1. TIMESTAMP: Use CAST(timestamp_col AS DATE) >= DATE('YYYY-MM-DD')
2. Column Names: products.id (NOT product_id), users.id (NOT user_id)
3. GROUP BY + ORDER BY: ORDER BY columns MUST be in GROUP BY or aggregated
4. Optimization: Use LIMIT, avoid SELECT *, add WHERE before JOINs

CONTEXT AWARENESS:
- Reference previous queries when relevant
- Build on previous results
- Maintain conversation continuity
- Use schema cache for efficiency

Generate precise, optimized SQL queries and provide clear, professional answers."""
    
    return [SystemMessage(content=system_prompt)]


def call_model(state: ExtendedAgentState) -> ExtendedAgentState:
    """
    Call model with context-aware prompting.
    
    Best Practice: Inject context from state into system message
    """
    # Create context-aware system message
    system_messages = create_context_aware_prompt(state)
    
    # Combine with conversation messages
    messages = system_messages + list(state["messages"])
    
    response = llm_with_tools.invoke(messages)
    
    return {
        **state,
        "messages": [response]
    }


def should_continue(state: ExtendedAgentState) -> str:
    """Determine if we should continue or end."""
    messages = state["messages"]
    last_message = messages[-1]
    
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"
    return END


def update_context(state: ExtendedAgentState) -> ExtendedAgentState:
    """
    Update conversation context after tool execution.
    
    Best Practice: Maintain context across turns for better coherence
    """
    messages = state["messages"]
    
    # Extract last result if available
    last_result = None
    for msg in reversed(messages):
        if hasattr(msg, 'content') and msg.content:
            last_result = str(msg.content)
            break
    
    return {
        **state,
        "last_query_result": last_result,
        "conversation_context": f"Updated at {datetime.now().isoformat()}"
    }


# Build the graph with memory
workflow = StateGraph(ExtendedAgentState)

# Add nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))
workflow.add_node("update_context", update_context)

# Define flow
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "update_context")
workflow.add_edge("update_context", "agent")

# Compile with memory checkpointer
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)


def run_agent_extended(
    query: str,
    user_id: str = "default_user",
    session_id: Optional[str] = None,
    config: Optional[RunnableConfig] = None
) -> str:
    """
    Run the extended agent with context management.
    
    Args:
        query: User's question
        user_id: User identifier for context
        session_id: Session identifier for conversation continuity
        config: Optional runnable config
        
    Returns:
        Agent's response
    """
    if session_id is None:
        session_id = str(uuid.uuid4())
    
    # Create config with thread_id for memory
    if config is None:
        config = {"configurable": {"thread_id": session_id}}
    
    # Initial state with context
    initial_state = {
        "messages": [HumanMessage(content=query)],
        "user_id": user_id,
        "session_id": session_id,
        "query_history": [],
        "schema_cache": {},
        "conversation_context": "",
        "last_query_result": None,
        "error_count": 0
    }
    
    # Invoke with memory
    result = app.invoke(initial_state, config=config)
    
    # Extract response
    for message in reversed(result["messages"]):
        if isinstance(message, AIMessage):
            return message.content
    
    return "No response generated"


def run_conversation(queries: list[str], user_id: str = "default_user") -> list[str]:
    """
    Run a multi-turn conversation with context preservation.
    
    Best Practice: Use same session_id to maintain context across turns
    """
    session_id = str(uuid.uuid4())
    responses = []
    
    for query in queries:
        print(f"\n{'='*60}")
        print(f"Query: {query}")
        print(f"{'='*60}")
        
        response = run_agent_extended(
            query=query,
            user_id=user_id,
            session_id=session_id
        )
        
        print(f"Response: {response}\n")
        responses.append(response)
    
    return responses


if __name__ == "__main__":
    print("🚀 Extended Agent with Context Engineering\n")
    
    # Example 1: Single query
    print("Example 1: Single Query")
    print("-" * 60)
    response = run_agent_extended("How many users are in the database?")
    print(f"Response: {response}\n")
    
    # Example 2: Multi-turn conversation with context
    print("\nExample 2: Multi-turn Conversation with Context")
    print("-" * 60)
    conversation_queries = [
        "How many users are in the database?",
        "What about products?",  # Context: refers to previous count question
        "Show me the top 5 by price"  # Context: refers to products
    ]
    
    run_conversation(conversation_queries)
    
    print("\n✅ Context-aware conversation complete!")
