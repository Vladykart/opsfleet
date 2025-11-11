# 🧵 LangSmith Threads Implementation

## Overview

LangSmith threads enable proper conversation tracking and grouping of related traces.

## What Are Threads?

**Thread** = A conversation session with multiple queries and responses

**Benefits**:
- Group related traces together
- Track conversation flow
- Analyze multi-turn interactions
- Debug conversation context issues

## Implementation

### 1. Thread ID Generation

```python
# CLI generates unique thread_id per session
thread_id = f"thread-{session_id}-{uuid}"

# Example: thread-20251111_030000-a1b2c3d4
```

### 2. Metadata Attachment

```python
session_metadata = {
    "session_id": thread_id,
    "thread_id": thread_id,
    "conversation_id": thread_id
}

# Attached to every LangSmith trace
```

### 3. Agent Integration

```python
async def process(self, query):
    # Set metadata on run tree
    run_tree = ls.get_current_run_tree()
    run_tree.extra["metadata"] = self.session_metadata
    
    # Process query...
```

## How It Works

### Session Flow

```
Session Start
    ↓
Generate thread_id: thread-20251111-a1b2c3d4
    ↓
Query 1: "Show orders"
    └─ Trace 1 (metadata: thread-20251111-a1b2c3d4)
    ↓
Query 2: "What about February?"
    └─ Trace 2 (metadata: thread-20251111-a1b2c3d4)
    ↓
Query 3: "Compare with March"
    └─ Trace 3 (metadata: thread-20251111-a1b2c3d4)
    ↓
Session End
```

### LangSmith View

All traces grouped under same thread:
```
Thread: thread-20251111-a1b2c3d4
├─ Trace 1: Show orders
├─ Trace 2: What about February?
└─ Trace 3: Compare with March
```

## Benefits

### Debugging
✅ **See full conversation** - All queries in one thread  
✅ **Track context** - How context flows between queries  
✅ **Identify issues** - Where conversation breaks down  

### Analytics
✅ **Conversation length** - How many turns per session  
✅ **Success rate** - Which conversations succeed  
✅ **User patterns** - Common conversation flows  

### Development
✅ **Test conversations** - Replay full sessions  
✅ **Compare threads** - Different conversation paths  
✅ **Monitor quality** - Track conversation coherence  

## Viewing Threads in LangSmith

### 1. Filter by Thread

```
Filter: metadata.session_id = "thread-20251111-a1b2c3d4"
```

### 2. View Thread Timeline

```
Thread Timeline:
10:00:00 - Query: Show orders
10:00:15 - Query: What about February?
10:00:30 - Query: Compare with March
```

### 3. Analyze Thread

```
Thread Metrics:
- Duration: 45 seconds
- Queries: 3
- Success Rate: 100%
- Avg Response Time: 15s
```

## Example Session

### CLI Output
```bash
$ python cli_chat.py --verbose

Session: 20251111_030000
Thread: thread-20251111_030000-a1b2c3d4

You: Show orders from January
Agent: [Executes, shows results]

You: What about February?
Agent: [Uses context, shows February]

You: Compare them
Agent: [Compares Jan vs Feb]
```

### LangSmith View
```
Project: opsfleet-agent
Thread: thread-20251111_030000-a1b2c3d4

Traces:
1. professional_react_agent (15.2s)
   └─ Query: Show orders from January
   
2. professional_react_agent (12.8s)
   └─ Query: What about February?
   
3. professional_react_agent (14.5s)
   └─ Query: Compare them
```

## Configuration

### Environment Variables
```bash
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=opsfleet-agent
LANGSMITH_API_KEY=your_key
```

### Agent Config
```python
config = {
    "thread_id": "thread-20251111-a1b2c3d4"
}

agent = ProfessionalReActAgent(
    tools=tools,
    llm_client=llm,
    config=config
)
```

## Summary

### Features
✅ **Unique thread per session**  
✅ **Metadata on all traces**  
✅ **Conversation grouping**  
✅ **LangSmith integration**  

### Benefits
🔍 **Better debugging** - See full conversations  
📊 **Better analytics** - Track conversation patterns  
🧪 **Better testing** - Replay sessions  
📈 **Better monitoring** - Conversation quality  

**All traces are now grouped by conversation thread in LangSmith!** 🧵🎉
