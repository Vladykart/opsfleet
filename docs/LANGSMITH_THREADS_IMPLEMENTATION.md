# 🧵 LangSmith Threads - Complete Implementation Guide

## Overview

Based on official LangSmith documentation, this guide shows how to properly implement conversation threads for our BigQuery Data Analysis Agent.

## What Are Threads?

**Thread** = A sequence of traces representing a single conversation
- Each query/response is a separate trace
- All traces linked by the same thread ID
- Enables conversation history tracking
- Allows multi-turn conversations

## Implementation

### 1. Thread ID Generation

```python
import uuid

# Generate unique thread ID per session
THREAD_ID = f"thread-{uuid.uuid4()}"
# Example: "thread-f47ac10b-58cc-4372-a567-0e02b2c3d479"
```

### 2. Metadata Configuration

```python
langsmith_extra = {
    "project_name": "opsfleet-agent",
    "metadata": {
        "session_id": THREAD_ID  # Required key
    }
}
```

**Accepted metadata keys**:
- `session_id` ✅ (we use this)
- `thread_id`
- `conversation_id`

### 3. Get Thread History

```python
from langsmith import Client

langsmith_client = Client()

def get_thread_history(thread_id: str, project_name: str):
    """Retrieve conversation history for a thread"""
    
    # Filter runs by thread ID
    filter_string = f'and(in(metadata_key, ["session_id","conversation_id","thread_id"]), eq(metadata_value, "{thread_id}"))'
    
    # Get all LLM runs for this thread
    runs = [
        r for r in langsmith_client.list_runs(
            project_name=project_name,
            filter=filter_string,
            run_type="llm"
        )
    ]
    
    # Sort by start time (most recent first)
    runs = sorted(runs, key=lambda run: run.start_time, reverse=True)
    
    if not runs:
        return []
    
    # Reconstruct conversation from latest run
    latest_run = runs[0]
    return latest_run.inputs['messages'] + [latest_run.outputs['choices'][0]['message']]
```

### 4. Agent Integration

```python
@traceable(name="BigQuery Agent")
async def process_query(query: str, get_chat_history: bool = False):
    """Process query with optional conversation history"""
    
    # Build messages
    messages = [{"role": "user", "content": query}]
    
    if get_chat_history:
        # Get current run tree
        run_tree = ls.get_current_run_tree()
        
        # Retrieve conversation history
        history_messages = get_thread_history(
            run_tree.extra["metadata"]["session_id"],
            run_tree.session_name
        )
        
        # Append new message to history
        all_messages = history_messages + messages
    else:
        all_messages = messages
    
    # Process with agent
    result = await agent.process(all_messages)
    
    return result
```

### 5. CLI Integration

```python
class ChatInterface:
    def __init__(self):
        # Generate thread ID for session
        self.thread_id = f"thread-{uuid.uuid4()}"
        
        # Configure LangSmith metadata
        self.langsmith_extra = {
            "project_name": "opsfleet-agent",
            "metadata": {
                "session_id": self.thread_id
            }
        }
    
    async def process_query(self, query: str):
        # First query in session
        if self.query_count == 0:
            get_history = False
        else:
            get_history = True  # Continue conversation
        
        result = await agent.process(
            query,
            get_chat_history=get_history,
            langsmith_extra=self.langsmith_extra
        )
        
        return result
```

## Viewing Threads in LangSmith

### 1. Access Threads Tab

Navigate to: **Project → Threads**

### 2. Thread Overview

**Chatbot-like UI** showing:
- Input/output for each turn
- Conversation flow
- Timestamps

**Configure display**:
- Click "Configure" button
- Set JSON paths for inputs/outputs
- Example: `inputs.messages[-1].content` (last message)

### 3. Trace View

**Detailed view** showing:
- All runs for each turn
- Performance metrics
- Error traces

**Toggle views**:
- Use buttons at top
- Keyboard shortcut: `T`

### 4. Feedback

**Thread-level feedback**:
- Aggregated scores across all runs
- Average metrics
- Individual run feedback

### 5. Filters

**Save common filters**:
- Set filter criteria
- Click "Save filter"
- Reuse for future analysis

## Example Usage

### Session Start

```python
# Initialize
thread_id = "thread-f47ac10b-58cc-4372-a567-0e02b2c3d479"
langsmith_extra = {
    "project_name": "opsfleet-agent",
    "metadata": {"session_id": thread_id}
}

# First query
messages = [{"role": "user", "content": "Show orders from January"}]
result = chat_pipeline(messages, get_chat_history=False, langsmith_extra=langsmith_extra)
```

### Continue Conversation

```python
# Second query (with history)
messages = [{"role": "user", "content": "What about February?"}]
result = chat_pipeline(messages, get_chat_history=True, langsmith_extra=langsmith_extra)

# Third query (with full history)
messages = [{"role": "user", "content": "Compare them"}]
result = chat_pipeline(messages, get_chat_history=True, langsmith_extra=langsmith_extra)
```

## LangSmith UI

### Thread List View

```
Threads (sorted by recent activity)
├─ thread-abc123 (5 turns, 2 min ago)
├─ thread-def456 (3 turns, 10 min ago)
└─ thread-ghi789 (8 turns, 1 hour ago)
```

### Thread Detail View

```
Thread: thread-abc123
Session: 2025-11-11 03:00:00

Turn 1 (15s)
  User: Show orders from January
  Agent: Found 150 orders...

Turn 2 (12s)
  User: What about February?
  Agent: Found 180 orders... (+20% vs Jan)

Turn 3 (10s)
  User: Compare them
  Agent: February had higher sales...
```

## Benefits

### Conversation Tracking
✅ **Full history** - See entire conversation  
✅ **Context flow** - Track how context builds  
✅ **Multi-turn** - Support complex conversations  

### Debugging
✅ **Trace each turn** - Debug specific responses  
✅ **Performance** - See timing for each turn  
✅ **Errors** - Identify where conversations fail  

### Analytics
✅ **Conversation length** - Average turns per session  
✅ **Success rate** - Which conversations complete  
✅ **User patterns** - Common conversation flows  

### Testing
✅ **Replay sessions** - Test with real conversations  
✅ **Compare threads** - A/B test different approaches  
✅ **Evaluate quality** - Score entire conversations  

## Configuration Checklist

- [x] Generate unique thread_id per session
- [x] Pass metadata with session_id
- [x] Implement get_thread_history()
- [x] Use @traceable decorator
- [x] Pass langsmith_extra to all calls
- [x] Enable get_chat_history for follow-ups
- [x] Configure LangSmith project
- [x] Set environment variables

## Environment Variables

```bash
# Required
LANGSMITH_API_KEY=your_api_key
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=opsfleet-agent

# Optional
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_PROJECT=opsfleet-agent
```

## Summary

### What We Implemented
✅ Thread ID generation (UUID-based)  
✅ Metadata configuration (session_id)  
✅ Thread history retrieval  
✅ Conversation continuity  
✅ LangSmith integration  

### What You Get
🔍 **Full conversation tracking** in LangSmith  
📊 **Thread-level analytics** and metrics  
🧪 **Conversation testing** and replay  
📈 **Performance monitoring** per turn  

### Next Steps
1. Run the agent with `--verbose`
2. Make multiple queries in one session
3. Check LangSmith → Threads tab
4. View your conversation history
5. Analyze performance and quality

**Your agent now has full LangSmith thread support!** 🧵🎉
