# Ensemble Mode & LangSmith Integration

## Overview

The system now supports **Ensemble Mode** where both Ollama and Gemini models work together, plus **LangSmith** integration for monitoring and debugging.

## Features

### 🤝 Ensemble Mode
- Calls **both** Ollama and Gemini simultaneously
- Uses the better result (longer, more detailed)
- Automatic fallback if one fails
- Parallel execution for speed

### 📊 LangSmith Integration
- Traces all LLM calls
- Monitors performance
- Debug prompts and responses
- View in LangSmith Studio

## Configuration

### Enable Ensemble Mode

Edit `config/agent_config.json`:

```json
{
  "llm": {
    "use_ensemble": true,
    "primary": {
      "provider": "ollama",
      "model": "llama3.2"
    },
    "secondary": {
      "provider": "google",
      "model": "gemini-2.5-flash"
    }
  }
}
```

### Environment Variables

Add to `.env`:

```bash
# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Gemini
GOOGLE_API_KEY=your-gemini-api-key

# LangSmith (optional but recommended)
LANGSMITH_API_KEY=your-langsmith-api-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=bigquery-data-analysis
```

## How Ensemble Mode Works

### 1. Parallel Execution

```python
# Both models called simultaneously
ollama_task = self._call_ollama(prompt, temperature, max_tokens)
gemini_task = self._call_gemini(prompt, temperature, max_tokens)

results = await asyncio.gather(ollama_task, gemini_task, return_exceptions=True)
```

### 2. Result Selection

```python
if ollama_result and gemini_result:
    # Use the longer, more detailed result
    if len(ollama_result) > len(gemini_result):
        return ollama_result
    else:
        return gemini_result
elif ollama_result:
    # Only Ollama succeeded
    return ollama_result
elif gemini_result:
    # Only Gemini succeeded (e.g., Ollama down)
    return gemini_result
```

### 3. Benefits

✅ **Best of Both Worlds**
- Ollama: Fast, local, no safety filters
- Gemini: High quality, cloud-based

✅ **Reliability**
- If Ollama fails → use Gemini
- If Gemini fails → use Ollama
- If both succeed → use better result

✅ **Speed**
- Parallel execution
- No sequential fallback delay
- ~Same time as single model

## LangSmith Setup

### 1. Get API Key

1. Go to [LangSmith](https://smith.langchain.com/)
2. Sign up / Log in
3. Create API key in Settings

### 2. Install LangSmith CLI

```bash
pip install langsmith

# Or with the project
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
export LANGSMITH_API_KEY=your-api-key
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_PROJECT=bigquery-data-analysis
```

### 4. View Traces

Visit: https://smith.langchain.com/

You'll see:
- All LLM calls
- Prompts sent
- Responses received
- Execution time
- Success/failure status
- Ensemble decisions

## LangSmith Studio

### What is LangSmith Studio?

Interactive environment for:
- Testing prompts
- Debugging traces
- Analyzing performance
- Comparing models
- Optimizing workflows

### Access Studio

```bash
# Open LangSmith Studio
langsmith studio
```

Or visit: https://studio.langchain.com/

### Features

1. **Prompt Playground**
   - Test prompts interactively
   - Compare model outputs
   - Adjust parameters

2. **Trace Viewer**
   - See full execution flow
   - Inspect each step
   - Debug failures

3. **Performance Analytics**
   - Response times
   - Token usage
   - Cost tracking
   - Success rates

4. **Dataset Management**
   - Create test datasets
   - Run evaluations
   - Track improvements

## Usage Examples

### Example 1: Ensemble Mode

```python
from src.agents.data_analysis_agent import DataAnalysisAgent
import json

# Load config with ensemble enabled
with open("config/agent_config.json") as f:
    config = json.load(f)

agent = DataAnalysisAgent(config)
await agent.initialize()

# This will use both Ollama and Gemini
result = await agent.analyze_product_performance(
    "What are the top 10 products by revenue?"
)

# Check logs to see which model was used
# INFO:BaseAgent:Using ensemble mode: Ollama + Gemini
# INFO:BaseAgent:Ensemble: Using Gemini result (longer)
```

### Example 2: Monitor with LangSmith

```python
import os
os.environ["LANGSMITH_API_KEY"] = "your-key"
os.environ["LANGCHAIN_TRACING_V2"] = "true"

# All calls are now traced
result = await agent.analyze_customer_segmentation(
    "Segment customers by order frequency"
)

# View trace at: https://smith.langchain.com/
```

### Example 3: Disable Ensemble (Use Primary Only)

```json
{
  "llm": {
    "use_ensemble": false,
    "primary": {
      "provider": "ollama",
      "model": "llama3.2"
    }
  }
}
```

## Testing Ensemble Mode

```bash
# Run test with ensemble mode
python test_ensemble.py
```

Create `test_ensemble.py`:

```python
import asyncio
from src.agents.data_analysis_agent import DataAnalysisAgent
import json

async def test_ensemble():
    with open("config/agent_config.json") as f:
        config = json.load(f)
    
    # Ensure ensemble is enabled
    config["llm"]["use_ensemble"] = True
    
    agent = DataAnalysisAgent(config)
    await agent.initialize()
    
    print("Testing ensemble mode...")
    result = await agent.analyze_product_performance(
        "Show top 5 products by revenue"
    )
    
    print(f"✓ Generated SQL ({len(result['sql'])} chars)")
    print(f"✓ Returned {result['row_count']} rows")
    print(f"✓ Generated {len(result['insights'])} insights")

if __name__ == "__main__":
    asyncio.run(test_ensemble())
```

## Performance Comparison

| Mode | Speed | Quality | Reliability | Cost |
|------|-------|---------|-------------|------|
| **Ollama Only** | ⚡ Fast | ✅ Good | ⚠️ Local only | 💰 Free |
| **Gemini Only** | 🌐 Medium | ✅ Excellent | ⚠️ API limits | 💰 Free tier |
| **Ensemble** | ⚡ Fast | ✅ Best | ✅ High | 💰 Free tier |

### Ensemble Advantages

1. **Quality**: Gets best result from both models
2. **Reliability**: Automatic fallback
3. **Speed**: Parallel execution
4. **Flexibility**: Works even if one model fails

## Troubleshooting

### Ensemble Not Working

```bash
# Check logs
INFO:BaseAgent:Ollama configured: http://localhost:11434 with model llama3.2
INFO:BaseAgent:Gemini configured: gemini-2.5-flash
INFO:BaseAgent:Using ensemble mode: Ollama + Gemini
```

If you don't see "Using ensemble mode":
- Check `use_ensemble: true` in config
- Verify both Ollama and Gemini are configured
- Check environment variables

### LangSmith Not Tracing

```bash
# Verify environment
echo $LANGSMITH_API_KEY
echo $LANGCHAIN_TRACING_V2

# Should see in logs
INFO:BaseAgent:LangSmith tracing enabled
```

If not tracing:
- Check API key is valid
- Verify `LANGCHAIN_TRACING_V2=true`
- Check network connection

### One Model Failing

```bash
# Ensemble handles this gracefully
ERROR:BaseAgent:Ollama call failed: Connection refused
INFO:BaseAgent:Ensemble: Only Gemini succeeded
```

This is normal! Ensemble mode continues with the working model.

## Best Practices

### 1. Use Ensemble for Production

```json
{
  "llm": {
    "use_ensemble": true
  }
}
```

Benefits:
- Maximum reliability
- Best quality results
- Automatic failover

### 2. Enable LangSmith Monitoring

```bash
export LANGSMITH_API_KEY=your-key
export LANGCHAIN_TRACING_V2=true
```

Benefits:
- Track performance
- Debug issues
- Optimize prompts

### 3. Monitor Both Models

Check LangSmith to see:
- Which model is used more often
- Which produces better results
- Response time differences
- Failure patterns

### 4. Optimize Based on Data

Use LangSmith analytics to:
- Identify slow queries
- Find failing prompts
- Compare model performance
- Reduce costs

## CLI Commands

### LangSmith CLI

```bash
# Install
pip install langsmith

# Login
langsmith login

# List projects
langsmith projects list

# View traces
langsmith traces list --project bigquery-data-analysis

# Export data
langsmith traces export --project bigquery-data-analysis --output traces.json

# Run evaluations
langsmith eval run --dataset my-dataset
```

### Useful Commands

```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Test ensemble mode
python test_ensemble.py

# View LangSmith traces
open https://smith.langchain.com/

# Monitor in real-time
langsmith traces tail --project bigquery-data-analysis
```

## Resources

### Documentation

- **LangSmith Docs**: https://docs.langchain.com/langsmith
- **LangSmith CLI**: https://docs.langchain.com/langsmith/cli
- **LangSmith Studio**: https://docs.langchain.com/langsmith/studio
- **Ollama Docs**: https://ollama.ai/docs
- **Gemini API**: https://ai.google.dev/docs

### Tutorials

1. **Getting Started with LangSmith**
   https://docs.langchain.com/langsmith/getting-started

2. **Tracing LLM Calls**
   https://docs.langchain.com/langsmith/tracing

3. **Using LangSmith Studio**
   https://docs.langchain.com/langsmith/studio/quickstart

4. **Evaluating LLM Applications**
   https://docs.langchain.com/langsmith/evaluation

## Summary

✅ **Ensemble Mode Enabled**
- Both Ollama and Gemini work together
- Automatic selection of best result
- Parallel execution for speed

✅ **LangSmith Integrated**
- All LLM calls traced
- Performance monitoring
- Debug capabilities
- Studio access

✅ **Production Ready**
- High reliability
- Best quality
- Full observability
- Easy debugging

---

**Next Steps:**
1. Enable ensemble mode in config
2. Set up LangSmith API key
3. Run test to verify
4. Monitor traces in LangSmith
5. Optimize based on data
