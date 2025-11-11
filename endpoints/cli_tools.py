"""CLI tools for agent interaction.

Tools that allow the agent to interact with the CLI,
such as saving conversations.
"""
from __future__ import annotations

from langchain_core.tools import tool


@tool
def save_conversation(format_type: str = "csv") -> str:
    """Save the current conversation to a file. ALWAYS use this tool when user asks to save/export/download.
    
    Args:
        format_type: Format to save in. Options: csv, json, excel, md, txt
        
    Returns:
        Special marker that triggers the save operation
        
    Examples:
        - "save this as json" -> save_conversation(format_type="json")
        - "export to excel" -> save_conversation(format_type="excel")
        - "download as csv" -> save_conversation(format_type="csv")
    """
    valid_formats = ["csv", "json", "excel", "md", "txt"]
    
    if format_type.lower() not in valid_formats:
        return f"Invalid format '{format_type}'. Valid formats: {', '.join(valid_formats)}"
    
    # Return a special marker that the CLI will intercept
    return f"__SAVE_CONVERSATION__{format_type.lower()}__"
