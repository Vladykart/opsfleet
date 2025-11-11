# 🧠 Context Engineering Best Practices

Extended agent implementation using LangGraph best practices from Context7 documentation.

## 🎯 Key Improvements

### 1. **Extended State Management**
```python
class ExtendedAgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: str                    # User identification
    session_id: str                 # Session tracking
    query_history: list[str]        # Query tracking
    schema_cache: Dict[str, Any]    # Schema caching
    conversation_context: str       # Context preservation
    last_query_result: Optional[str] # Result caching
    error_count: int                # Error tracking
```

### 2. **Context-Aware Tools**
```python
@tool
def query_bigquery(sql: str, state: Annotated[ExtendedAgentState, InjectedState]) -> str:
    """Tool with access to agent state for context"""
    query_history = state.get("query_history", [])
    # Use context to enhance tool behavior
```

### 3. **Memory Persistence**
```python
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Invoke with thread_id for conversation continuity
config = {"configurable": {"thread_id": session_id}}
result = app.invoke(initial_state, config=config)
```

### 4. **Context-Aware Prompting**
```python
def create_context_aware_prompt(state: ExtendedAgentState) -> list[BaseMessage]:
    """Build prompts with conversation history and context"""
    query_history = state.get("query_history", [])
    last_result = state.get("last_query_result")
    
    # Inject context into system message
    system_prompt = f"""
    SESSION CONTEXT:
    - Recent queries: {recent_queries}
    - Last result: {last_result}
    
    Use this context to maintain conversation continuity...
    """
```

### 5. **Multi-Turn Conversations**
```python
def run_conversation(queries: list[str]) -> list[str]:
    """Maintain context across multiple turns"""
    session_id = str(uuid.uuid4())  # Same session for all queries
    
    for query in queries:
        response = run_agent_extended(
            query=query,
            session_id=session_id  # Context preserved!
        )
```

## 📊 Architecture

```
User Query
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Extended State                                             │
│  - messages, user_id, session_id                           │
│  - query_history, schema_cache                             │
│  - conversation_context, last_query_result                 │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Context-Aware Prompt                                       │
│  - Inject conversation history                             │
│  - Add recent queries context                              │
│  - Include last result summary                             │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Agent Node (with tools)                                    │
│  - Tools have access to state                              │
│  - Context-aware decision making                           │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Update Context Node                                        │
│  - Store query results                                     │
│  - Update conversation context                             │
│  - Maintain history                                        │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│  Memory Checkpointer                                        │
│  - Persist state across turns                              │
│  - Enable conversation resumption                          │
└─────────────────────────────────────────────────────────────┘
```

## 🔥 Best Practices Applied

### From LangGraph Documentation (Context7)

#### 1. **InjectedState Pattern**
```python
def tool_with_state(
    arg: str,
    state: Annotated[ExtendedAgentState, InjectedState]
) -> str:
    """Tools can access full agent state"""
    user_id = state["user_id"]
    history = state["query_history"]
    # Use context to enhance behavior
```

**Benefits:**
- Tools are context-aware
- Can reference previous interactions
- Maintain conversation coherence

#### 2. **Custom State Schema**
```python
class ExtendedAgentState(TypedDict):
    """Rich state beyond just messages"""
    messages: Annotated[Sequence[BaseMessage], add_messages]
    user_id: str
    session_id: str
    # ... additional context fields
```

**Benefits:**
- Track user identity
- Maintain session context
- Cache frequently used data
- Monitor errors and performance

#### 3. **Memory Checkpointing**
```python
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# Use thread_id for conversation continuity
config = {"configurable": {"thread_id": session_id}}
```

**Benefits:**
- Persist state across turns
- Resume conversations
- Handle interruptions gracefully
- Enable human-in-the-loop

#### 4. **Context-Aware Prompting**
```python
def create_context_aware_prompt(state):
    """Build prompts with full context"""
    context = build_context_from_state(state)
    system_prompt = f"Context: {context}\n\nTask: ..."
    return [SystemMessage(content=system_prompt)]
```

**Benefits:**
- Better multi-turn coherence
- Reference previous results
- Maintain conversation flow
- Reduce redundant queries

#### 5. **State Updates in Tools**
```python
def tool_that_updates_state(...) -> Command:
    """Tools can update state"""
    return Command(update={
        "query_history": [...],
        "last_query_result": result
    })
```

**Benefits:**
- Tools contribute to context
- State evolves naturally
- Better information flow

## 💡 Usage Examples

### Example 1: Single Query with Context
```python
response = run_agent_extended(
    query="How many users are in the database?",
    user_id="user_123",
    session_id="session_abc"
)
```

### Example 2: Multi-Turn Conversation
```python
queries = [
    "How many users are in the database?",
    "What about products?",  # Understands context!
    "Show me the top 5 by price"  # Knows we're talking about products!
]

responses = run_conversation(queries, user_id="user_123")
```

### Example 3: Resume Conversation
```python
# First session
session_id = "session_xyz"
run_agent_extended("Show me sales data", session_id=session_id)

# Later... resume with same session_id
run_agent_extended("What was the total?", session_id=session_id)
# Agent remembers the previous query!
```

## 🆚 Comparison

| Feature | Basic Agent | Extended Agent |
|---------|------------|----------------|
| State | Messages only | Rich context |
| Memory | None | Persistent |
| Context | Single turn | Multi-turn |
| Tool State | No access | Full access |
| User Tracking | No | Yes |
| Session Management | No | Yes |
| Query History | No | Yes |
| Schema Cache | No | Yes |
| Conversation Flow | Disconnected | Coherent |

## 🚀 Key Benefits

### 1. **Better Conversations**
- Maintains context across turns
- References previous queries
- Builds on past results
- Natural conversation flow

### 2. **Improved Performance**
- Schema caching reduces lookups
- Query history prevents redundancy
- Context reduces token usage
- Faster response times

### 3. **Enhanced UX**
- Users don't repeat context
- Follow-up questions work naturally
- Conversation feels intelligent
- Better error recovery

### 4. **Production Ready**
- User identification
- Session management
- Error tracking
- Audit trail

## 📝 Implementation Notes

### Memory Management
```python
# MemorySaver stores state in memory
# For production, use:
# - RedisSaver for distributed systems
# - PostgresSaver for persistence
# - Custom checkpointer for specific needs
```

### Context Window Management
```python
# Keep last N queries to manage context size
recent_queries = query_history[-3:]  # Last 3 queries

# Summarize old results instead of full text
last_result_summary = last_result[:200] + "..."
```

### State Updates
```python
# Update state after tool execution
def update_context(state):
    return {
        **state,
        "last_query_result": extract_result(state),
        "conversation_context": build_context(state)
    }
```

## 🎯 Best Practices Summary

1. ✅ **Use Extended State** - Track more than just messages
2. ✅ **Inject State into Tools** - Make tools context-aware
3. ✅ **Implement Memory** - Persist state across turns
4. ✅ **Build Context-Aware Prompts** - Use conversation history
5. ✅ **Manage Context Window** - Keep recent, summarize old
6. ✅ **Track Sessions** - Enable conversation resumption
7. ✅ **Cache Frequently Used Data** - Reduce redundant lookups
8. ✅ **Update State in Tools** - Let tools contribute to context

## 📚 References

- LangGraph Documentation (via Context7 MCP)
- State Management Best Practices
- Memory and Persistence Patterns
- Context Engineering Techniques

---

**This implementation follows official LangGraph best practices for production-ready, context-aware agents!** 🚀
