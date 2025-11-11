"""
Simple BigQuery Agent using LangGraph and Gemini.
Uses Application Default Credentials (ADC) for authentication.
"""
import os
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from google.cloud import bigquery


# Initialize BigQuery client with ADC
bq_client = bigquery.Client()


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
    messages: Annotated[list, "The messages in the conversation"]


# Initialize the LLM with tools
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
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
workflow.set_entry_point("agent")

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
    # Add system message with BigQuery context
    system_msg = """You are a helpful BigQuery data analyst assistant.
    
You have access to the BigQuery public dataset: bigquery-public-data.thelook_ecommerce

Available tables:
- users: Customer information (id, first_name, last_name, email, country, city, created_at)
- products: Product catalog (id, name, category, brand, retail_price, cost)
- orders: Order records (order_id, user_id, status, created_at, shipped_at, delivered_at)
- order_items: Order line items (id, order_id, user_id, product_id, sale_price, created_at)

When writing SQL queries:
1. Always use fully qualified table names: `bigquery-public-data.thelook_ecommerce.table_name`
2. Use backticks around table names
3. Limit results to 10 rows for readability
4. Be specific and accurate with column names

Answer the user's question by querying the database when needed."""

    initial_state = {
        "messages": [
            HumanMessage(content=system_msg),
            HumanMessage(content=query)
        ]
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
