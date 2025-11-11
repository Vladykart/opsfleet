# 🚀 LangGraph Server Setup

Run OpsFleet Agent as a LangGraph server for API access and deployment.

## Quick Start

### 1. Install LangGraph CLI
```bash
pip install -U "langgraph-cli[inmem]"
```

### 2. Install Package
```bash
pip install -e .
```

### 3. Start Development Server
```bash
langgraph dev
```

The server will start at `http://localhost:8123`

## Configuration

### langgraph.json
```json
{
  "dependencies": ["."],
  "graphs": {
    "opsfleet_agent": "./agent.py:graph"
  },
  "env": ".env"
}
```

### pyproject.toml
Defines the package structure and dependencies for LangGraph deployment.

## API Endpoints

Once running, access the agent via HTTP:

### POST /runs/stream
Stream agent responses:
```bash
curl -X POST http://localhost:8123/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "opsfleet_agent",
    "input": {
      "messages": [{"role": "user", "content": "How many users?"}]
    }
  }'
```

### GET /threads
List conversation threads

### POST /threads
Create new thread

### GET /threads/{thread_id}/runs
Get run history for a thread

## Environment Variables

Required in `.env`:
```bash
# Google Cloud
GCP_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Gemini API
GOOGLE_API_KEY=your-gemini-key

# LangSmith (optional)
LANGSMITH_API_KEY=your-langsmith-key
LANGSMITH_TRACING_V2=true
LANGSMITH_PROJECT=opsfleet-agent
```

## Features

### 1. HTTP API
- RESTful endpoints for agent interaction
- Streaming responses
- Thread management
- Run history

### 2. Development Mode
- Hot reload on code changes
- Built-in debugging
- Request logging
- Error tracking

### 3. Production Ready
- Scalable architecture
- State persistence
- Checkpoint management
- Error handling

## Usage Examples

### Python Client
```python
import httpx

async def query_agent(question: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8123/runs/stream",
            json={
                "assistant_id": "opsfleet_agent",
                "input": {
                    "messages": [{"role": "user", "content": question}]
                }
            }
        )
        async for line in response.aiter_lines():
            print(line)

# Usage
await query_agent("How many users are in the database?")
```

### JavaScript/TypeScript
```typescript
const response = await fetch('http://localhost:8123/runs/stream', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    assistant_id: 'opsfleet_agent',
    input: {
      messages: [{ role: 'user', content: 'How many users?' }]
    }
  })
});

const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  console.log(new TextDecoder().decode(value));
}
```

### cURL
```bash
# Simple query
curl -X POST http://localhost:8123/runs/stream \
  -H "Content-Type: application/json" \
  -d '{
    "assistant_id": "opsfleet_agent",
    "input": {
      "messages": [{"role": "user", "content": "Show top 10 products"}]
    }
  }'
```

## Deployment

### LangGraph Cloud
```bash
# Deploy to LangGraph Cloud
langgraph deploy
```

### Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -e .
RUN pip install "langgraph-cli[inmem]"

EXPOSE 8123

CMD ["langgraph", "dev", "--host", "0.0.0.0"]
```

Build and run:
```bash
docker build -t opsfleet-agent .
docker run -p 8123:8123 --env-file .env opsfleet-agent
```

## Monitoring

### LangSmith Integration
Automatic tracing when `LANGSMITH_TRACING_V2=true`:
- View all runs in LangSmith dashboard
- Debug agent behavior
- Monitor performance
- Analyze token usage

### Health Check
```bash
curl http://localhost:8123/health
```

## Development Workflow

### 1. Local Development
```bash
# Start dev server with hot reload
langgraph dev

# Test changes immediately
curl -X POST http://localhost:8123/runs/stream \
  -H "Content-Type: application/json" \
  -d '{"assistant_id": "opsfleet_agent", "input": {"messages": [{"role": "user", "content": "test"}]}}'
```

### 2. Testing
```bash
# Run tests
pytest test_cli_enhanced.py -v

# Test agent directly
python -c "from agent import run_agent; print(run_agent('How many users?'))"
```

### 3. Debugging
- Check logs in terminal
- Use LangSmith for trace debugging
- Enable verbose logging in `.env`

## Troubleshooting

### Port Already in Use
```bash
# Change port
langgraph dev --port 8124
```

### Module Not Found
```bash
# Reinstall package
pip install -e .
```

### Environment Variables Not Loaded
```bash
# Check .env file exists
ls -la .env

# Verify variables
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('GCP_PROJECT_ID'))"
```

## Architecture

```
┌─────────────────┐
│   HTTP Client   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  LangGraph API  │
│   (Port 8123)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Agent Graph    │
│  (agent.py)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   BigQuery      │
│   + Gemini      │
└─────────────────┘
```

## Next Steps

1. **Start Server:** `langgraph dev`
2. **Test API:** Use curl or Postman
3. **Integrate:** Connect your frontend
4. **Deploy:** Push to LangGraph Cloud
5. **Monitor:** Check LangSmith dashboard

## Resources

- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangGraph Cloud](https://langchain-ai.github.io/langgraph/cloud/)
- [API Reference](https://langchain-ai.github.io/langgraph/cloud/reference/api/)
- [Examples](https://github.com/langchain-ai/langgraph/tree/main/examples)
