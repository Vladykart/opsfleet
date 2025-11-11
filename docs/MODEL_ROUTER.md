# Model Router Documentation

## Overview

The `ModelRouter` provides intelligent model selection for different tasks, supporting multiple LLM providers:
- **OpenAI** (GPT-4, GPT-3.5-turbo, etc.)
- **Ollama** (Llama 3.2, custom models)
- **Google Gemini** (via existing BaseAgent)
- **AWS Bedrock** (via existing BaseAgent)

## Installation

### 1. Install Dependencies

```bash
pip install langchain-openai langchain-ollama
```

### 2. Configure Environment

Add to your `.env` file:

```bash
# OpenAI (optional)
OPENAI_API_KEY=your-openai-api-key

# Ollama (optional, default: http://localhost:11434)
OLLAMA_BASE_URL=http://localhost:11434
```

### 3. Install Ollama (Optional)

For local models:

```bash
# macOS
brew install ollama

# Start Ollama
ollama serve

# Pull models
ollama pull llama3.2
ollama pull gpt-oss:120b-cloud
```

## Usage

### Basic Usage

```python
from src.model_router import ModelRouter

router = ModelRouter()

# Get LLM for specific task
llm = router.get_llm_for_task("generation", temperature=0.8)

# Get specific model
gpt4 = router.get_llm("gpt-4", temperature=0.7, max_tokens=1000)
llama = router.get_llm("llama3.2", temperature=0.5)
```

### Task-Based Selection

The router automatically selects optimal models for different tasks:

```python
router = ModelRouter()

# Generation tasks → gpt-oss:120b-cloud
generation_llm = router.get_llm_for_task("generation")

# Validation tasks → llama3.2
validation_llm = router.get_llm_for_task("validation")

# Analysis tasks → llama3.2
analysis_llm = router.get_llm_for_task("analysis")

# Routing tasks → llama3.2
routing_llm = router.get_llm_for_task("routing")
```

### Custom Task Mapping

Modify task-to-model mapping:

```python
class CustomModelRouter(ModelRouter):
    def select_model_for_task(self, task: str) -> str:
        task_models = {
            "generation": "gpt-4",
            "validation": "gpt-3.5-turbo",
            "analysis": "llama3.2",
            "routing": "llama3.2",
            "summarization": "gpt-4",
            "translation": "gpt-3.5-turbo"
        }
        return task_models.get(task, "llama3.2")
```

### Integration with Agents

```python
from src.agents.enhanced_base_agent import EnhancedBaseAgent

class MyAgent(EnhancedBaseAgent):
    async def process(self, state):
        # Use task-based selection
        llm = self.get_llm_for_task("generation", temperature=0.8)
        
        # Or use specific model
        llm = self.get_llm("gpt-4", temperature=0.7)
        
        response = await llm.ainvoke("Your prompt here")
        return {"result": response.content}
```

## Supported Models

### OpenAI Models

- `gpt-4` - Most capable, best for complex tasks
- `gpt-4-turbo` - Faster GPT-4
- `gpt-3.5-turbo` - Fast and cost-effective

### Ollama Models

- `llama3.2` - Meta's Llama 3.2
- `gpt-oss:120b-cloud` - Large open-source model
- `mistral` - Mistral AI model
- `codellama` - Code-specialized model
- Any custom Ollama model

## Configuration

### Default Task Mapping

```python
{
    "generation": "gpt-oss:120b-cloud",
    "validation": "llama3.2",
    "analysis": "llama3.2",
    "routing": "llama3.2"
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | None |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |

## Examples

### Example 1: Multi-Model Analysis

```python
router = ModelRouter()

# Use GPT-4 for complex generation
generation_llm = router.get_llm("gpt-4", temperature=0.8)
report = await generation_llm.ainvoke("Generate analysis report...")

# Use Llama for validation
validation_llm = router.get_llm("llama3.2", temperature=0.3)
is_valid = await validation_llm.ainvoke("Validate this data...")
```

### Example 2: Cost Optimization

```python
router = ModelRouter()

# Use local Ollama for most tasks (free)
cheap_llm = router.get_llm("llama3.2")

# Use GPT-4 only for critical tasks
premium_llm = router.get_llm("gpt-4")
```

### Example 3: Streaming Responses

```python
router = ModelRouter()
llm = router.get_llm("gpt-4")

async for chunk in llm.astream("Tell me a story..."):
    print(chunk.content, end="", flush=True)
```

## Troubleshooting

### Ollama Connection Issues

**Problem:** `Connection refused to Ollama`

**Solution:**
```bash
# Start Ollama server
ollama serve

# Verify it's running
curl http://localhost:11434/api/tags
```

### OpenAI API Key Issues

**Problem:** `Invalid API key`

**Solution:**
- Check `.env` file has correct key
- Verify key at https://platform.openai.com/api-keys
- Ensure no extra spaces or quotes

### Model Not Found

**Problem:** `Model 'llama3.2' not found`

**Solution:**
```bash
# Pull the model
ollama pull llama3.2

# List available models
ollama list
```

## Performance Considerations

### Model Selection Guidelines

| Task Type | Recommended Model | Reason |
|-----------|------------------|---------|
| Complex reasoning | GPT-4 | Best accuracy |
| Fast generation | GPT-3.5-turbo | Speed + cost |
| Local/private | Llama 3.2 | Privacy + free |
| Code generation | CodeLlama | Specialized |
| Validation | Llama 3.2 | Fast + accurate |

### Cost Optimization

1. **Use Ollama for development** - Free local models
2. **Use GPT-3.5 for production** - Good balance
3. **Use GPT-4 for critical tasks** - Best quality
4. **Cache responses** - Reduce API calls

## Integration with Existing System

The ModelRouter works alongside the existing BaseAgent:

```python
# Option 1: Use existing BaseAgent (Gemini/Bedrock)
from src.agents.base_agent import BaseAgent

# Option 2: Use EnhancedBaseAgent (OpenAI/Ollama)
from src.agents.enhanced_base_agent import EnhancedBaseAgent

# Option 3: Mix both
class HybridAgent(BaseAgent):
    def __init__(self, config):
        super().__init__(config)
        self.model_router = ModelRouter()
    
    async def process(self, state):
        # Use Gemini for main task
        gemini_response = await self.llm_client.generate_content(...)
        
        # Use Ollama for validation
        validator = self.model_router.get_llm("llama3.2")
        validation = await validator.ainvoke(...)
```

## API Reference

### ModelRouter

#### `__init__()`
Initialize the router with environment variables.

#### `get_llm(model_name: str, temperature: float = 0.7, max_tokens: Optional[int] = None) -> BaseChatModel`
Get LLM instance by name.

**Parameters:**
- `model_name`: Model identifier (e.g., "gpt-4", "llama3.2")
- `temperature`: Sampling temperature (0.0-1.0)
- `max_tokens`: Maximum tokens to generate

**Returns:** LangChain chat model instance

#### `select_model_for_task(task: str) -> str`
Select optimal model for task type.

**Parameters:**
- `task`: Task type ("generation", "validation", "analysis", "routing")

**Returns:** Model name string

#### `get_llm_for_task(task: str, temperature: float = 0.7) -> BaseChatModel`
Get LLM configured for specific task.

**Parameters:**
- `task`: Task type
- `temperature`: Sampling temperature

**Returns:** LangChain chat model instance

## See Also

- [LangChain OpenAI Documentation](https://python.langchain.com/docs/integrations/chat/openai)
- [LangChain Ollama Documentation](https://python.langchain.com/docs/integrations/chat/ollama)
- [Ollama Model Library](https://ollama.ai/library)
