"""BigQuery Agent using LangGraph and Gemini.

Modern Python implementation with type hints, match-case statements,
and best practices for maintainability and readability.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import TypedDict, Annotated, Sequence, Any
from dataclasses import dataclass

from langgraph.graph import StateGraph, END, START
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, BaseMessage
from langgraph.graph.message import add_messages
from dotenv import load_dotenv

from endpoints import query_bigquery, analyze_schema, save_conversation


@dataclass(frozen=True)
class Config:
    """Application configuration."""
    langsmith_enabled: bool
    langsmith_project: str

    @classmethod
    def from_env(cls) -> Config:
        """Load configuration from environment variables."""
        load_dotenv()
        
        return cls(
            langsmith_enabled=os.getenv("LANGCHAIN_TRACING_V2") == "true",
            langsmith_project=os.getenv("LANGCHAIN_PROJECT", "opsfleet-agent")
        )


# Initialize configuration
config = Config.from_env()

# Enable LangSmith tracing if configured
if config.langsmith_enabled:
    os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
    os.environ["LANGCHAIN_PROJECT"] = config.langsmith_project
    print("✅ LangSmith tracing enabled")


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
tools = [query_bigquery, analyze_schema, save_conversation]
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
    """Load the system prompt from file and format with query.
    
    Args:
        query: User's question to inject into prompt
        
    Returns:
        Formatted prompt string
    """
    prompt_path = Path(__file__).parent / "prompts" / "system_prompt.txt"
    return prompt_path.read_text(encoding="utf-8").format(query=query)


def _extract_content(content: str | list[dict[str, Any]]) -> str:
    """Extract text content from AI message.
    
    Args:
        content: Message content (string or list of content blocks)
        
    Returns:
        Extracted text string
    """
    match content:
        case str() as text:
            return text
        case list() as blocks:
            text_parts = [
                item.get("text", item) if isinstance(item, dict) else str(item)
                for item in blocks
            ]
            return "\n".join(text_parts) if text_parts else "No response generated"
        case _:
            return "No response generated"


def run_agent(query: str) -> str:
    """Run the agent with a query.
    
    Args:
        query: The user's question
        
    Returns:
        The agent's response
    """
    prompt = load_prompt(query)
    initial_state = {"messages": [HumanMessage(content=prompt)]}
    result = app.invoke(initial_state)
    
    # Find the last AI message
    for message in reversed(result["messages"]):
        if isinstance(message, AIMessage):
            return _extract_content(message.content)
    
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
