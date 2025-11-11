# LangSmith Tracing Setup

LangSmith provides powerful tracing and debugging for your LangGraph agent.

## Quick Setup

### 1. Get LangSmith API Key

1. Go to [LangSmith](https://smith.langchain.com/)
2. Sign up or log in
3. Navigate to Settings → API Keys
4. Create a new API key

### 2. Configure Environment

Add to your `.env` file:

```bash
# Enable LangSmith tracing
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_PROJECT=opsfleet-agent
```

### 3. Run Agent

```bash
python agent.py
```

You'll see: `✅ LangSmith tracing enabled`

## What You Get

### 🔍 Trace Every Run
- See each step of the agent execution
- View LLM calls and responses
- Monitor tool executions
- Track message flow

### 📊 Performance Metrics
- Latency per step
- Token usage
- Cost tracking
- Error rates

### 🐛 Debugging
- Inspect intermediate states
- View tool inputs/outputs
- See LLM reasoning
- Identify bottlenecks

## View Traces

1. Go to [LangSmith Projects](https://smith.langchain.com/)
2. Select your project: `opsfleet-agent`
3. Click on any trace to see details

## Example Trace View

```
Run: "How many users are in the database?"
├─ Agent Node
│  ├─ LLM Call (Gemini 2.5 Flash)
│  │  Input: "How many users..."
│  │  Output: Tool call to query_bigquery
│  └─ Duration: 1.2s
├─ Tools Node
│  ├─ query_bigquery
│  │  Input: "SELECT COUNT(*) FROM..."
│  │  Output: "100000"
│  └─ Duration: 0.8s
└─ Agent Node
   ├─ LLM Call (Gemini 2.5 Flash)
   │  Input: Tool result + context
   │  Output: "There are 100,000 users..."
   └─ Duration: 0.9s

Total: 2.9s | Tokens: 450 | Cost: $0.002
```

## Disable Tracing

Comment out or remove from `.env`:

```bash
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_API_KEY=your-langsmith-api-key
# LANGCHAIN_PROJECT=opsfleet-agent
```

## Benefits

- **Debug faster** - See exactly what's happening
- **Optimize performance** - Identify slow steps
- **Monitor production** - Track usage and errors
- **Improve prompts** - See LLM reasoning
- **Share traces** - Collaborate with team

## Resources

- [LangSmith Docs](https://docs.smith.langchain.com/)
- [LangGraph Tracing](https://langchain-ai.github.io/langgraph/how-tos/tracing/)
- [API Reference](https://api.smith.langchain.com/docs)
