# Professional CLI Chat Interface

## Overview

A beautiful, professional command-line interface for interacting with the BigQuery Data Analysis Agent featuring:

- 🎨 **Beautiful UI** with Rich library
- 🧠 **Multi-stage ReAct reasoning** (5 stages)
- 💾 **Long-term conversation memory**
- 📊 **Real-time progress indicators**
- 🎯 **Professional output formatting**

## Features

### Multi-Stage Processing

The agent processes queries through 5 professional stages:

1. **Understanding** - Analyzes user intent and context
2. **Planning** - Creates detailed execution plan
3. **Execution** - Executes plan using ReAct loop (Think-Act-Observe)
4. **Validation** - Validates results for quality
5. **Synthesis** - Generates professional response

### Long-Term Memory

- **Short-term memory**: Last 10 interactions
- **Long-term memory**: Up to 50 historical interactions
- **Context-aware**: Uses conversation history for better responses
- **Automatic consolidation**: Moves old interactions to long-term storage

### Beautiful Interface

- **Colored panels** for different stages
- **Progress indicators** for long operations
- **Formatted tables** for structured data
- **Markdown rendering** for rich responses
- **Syntax highlighting** for code/SQL

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or install rich separately
pip install rich
```

## Usage

### Start the CLI

```bash
# Make executable
chmod +x cli_chat.py

# Run
python cli_chat.py
```

### Commands

| Command | Description |
|---------|-------------|
| `<your question>` | Ask anything about the data |
| `help` | Show help message |
| `history` | View conversation history |
| `stats` | Show session statistics |
| `clear` | Clear the screen |
| `exit` or `quit` | Exit the application |

### Example Session

```
🚀 BigQuery Data Analysis Agent

You: What are the top 10 products by revenue?

┌─ Understanding ─────────────────────────────────┐
│ Intent: Analyze product revenue                │
│ Complexity: simple                              │
│ Output Format: table                            │
└─────────────────────────────────────────────────┘

┌─ Execution Plan ────────────────────────────────┐
│ Step │ Action    │ Description                  │
├──────┼───────────┼──────────────────────────────┤
│ 1    │ bigquery  │ Query product revenue data   │
│ 2    │ analyze   │ Calculate top performers     │
└──────┴───────────┴──────────────────────────────┘

┌─ Response ──────────────────────────────────────┐
│ ## Top 10 Products by Revenue                   │
│                                                  │
│ ### Executive Summary                           │
│ Analysis of 10,000+ products reveals...         │
│                                                  │
│ ### Key Findings                                │
│ • Product A leads with $15,351 revenue          │
│ • Top 10 products account for 23% of revenue    │
│ • Average revenue per product: $12,241          │
└──────────────────────────────────────────────────┘
```

## Architecture

### ProfessionalReActAgent

```python
class ProfessionalReActAgent:
    """
    Professional multi-stage ReAct agent
    
    Stages:
    1. Understanding - Intent analysis
    2. Planning - Execution planning
    3. Execution - ReAct loop
    4. Validation - Quality check
    5. Synthesis - Response generation
    """
```

### ConversationMemory

```python
class ConversationMemory:
    """
    Long-term conversation memory
    
    Features:
    - Short-term: Last 10 interactions
    - Long-term: Up to 50 interactions
    - Auto-consolidation
    - Context retrieval
    """
```

### BeautifulCLI

```python
class BeautifulCLI:
    """
    Beautiful CLI interface
    
    Features:
    - Rich formatting
    - Progress indicators
    - Interactive prompts
    - Command handling
    """
```

## Stage Details

### Stage 1: Understanding

**Purpose**: Analyze user intent and context

**Output**:
```json
{
    "intent": "primary goal",
    "required_info": ["data needed"],
    "complexity": "simple/medium/complex",
    "output_format": "table/chart/report",
    "clarifications_needed": []
}
```

**Example**:
```
Intent: Analyze product revenue
Complexity: simple
Output Format: table
```

### Stage 2: Planning

**Purpose**: Create detailed execution plan

**Output**:
```json
{
    "steps": [
        {
            "id": 1,
            "action": "bigquery",
            "description": "Query revenue data",
            "expected_output": "product revenue table",
            "critical": true
        }
    ],
    "estimated_time": "2-3 minutes",
    "risk_level": "low"
}
```

**Display**:
```
┌─ Execution Plan ────────────────┐
│ Step │ Action   │ Description    │
├──────┼──────────┼────────────────┤
│ 1    │ bigquery │ Query data     │
│ 2    │ analyze  │ Calculate      │
└──────┴──────────┴────────────────┘
```

### Stage 3: Execution (ReAct Loop)

**Purpose**: Execute plan with reasoning

**ReAct Steps**:
1. **Think**: Reason about current step
2. **Act**: Execute tool/action
3. **Observe**: Record result
4. **Repeat**: Until plan complete

**Example**:
```
Thought: I need to query BigQuery for product revenue
Action: bigquery
Input: SELECT name, SUM(revenue) FROM products...
Observation: Retrieved 10 rows of data
```

### Stage 4: Validation

**Purpose**: Validate execution results

**Output**:
```json
{
    "valid": true,
    "confidence": 0.95,
    "issues": [],
    "recommendations": []
}
```

**Display**:
```
┌─ Validation ─────────────────┐
│ ✓ Valid                      │
│ Confidence: 95.0%            │
└──────────────────────────────┘
```

### Stage 5: Synthesis

**Purpose**: Generate professional response

**Format**:
- Executive summary
- Key findings (bullet points)
- Detailed analysis
- Recommendations

**Example**:
```markdown
## Top 10 Products by Revenue

### Executive Summary
Analysis of product revenue data reveals...

### Key Findings
• Product A leads with $15,351 revenue
• Top 10 account for 23% of total revenue
• Average revenue: $12,241

### Detailed Analysis
The data shows a clear concentration...

### Recommendations
1. Focus marketing on top performers
2. Investigate low-performing products
```

## Memory System

### How It Works

```python
# Short-term memory (last 10 interactions)
memory.short_term = [
    {"query": "...", "result": "...", "timestamp": "..."},
    ...
]

# Long-term memory (up to 50 interactions)
memory.long_term = [
    {"query": "...", "result": "...", "timestamp": "..."},
    ...
]

# Context summary
memory.context_summary = "User has been analyzing product data..."
```

### Context Retrieval

```python
context = memory.get_context()
# Returns:
# "Previous context: User analyzed products
#  Recent interactions:
#  - User: What are top products?
#    Result: Product A leads with..."
```

### Auto-Consolidation

When short-term memory exceeds 10 items:
1. Move oldest 5 to long-term
2. Keep recent 5 in short-term
3. Trim long-term to 50 items

## Customization

### Change Colors

Edit `cli_chat.py`:

```python
stage_colors = {
    "understanding": "yellow",  # Change to your color
    "planning": "blue",
    "execution": "green",
    "validation": "magenta",
    "synthesis": "cyan"
}
```

### Adjust Memory Size

```python
memory = ConversationMemory(max_history=100)  # Increase to 100
```

### Modify Stages

Add custom stage in `ProfessionalReActAgent`:

```python
async def _stage_6_custom(self, data):
    """Custom stage"""
    # Your logic here
    pass
```

## Troubleshooting

### CLI Not Starting

```bash
# Check dependencies
pip install rich

# Check Python version
python --version  # Should be 3.8+

# Run with verbose output
python cli_chat.py --verbose
```

### Memory Issues

```bash
# Clear memory
# In CLI: type 'clear'

# Or reduce memory size
memory = ConversationMemory(max_history=20)
```

### Display Issues

```bash
# Check terminal supports colors
echo $TERM

# Use simpler display
export TERM=xterm-256color
```

## Advanced Usage

### Programmatic Access

```python
from src.agents.professional_react_agent import ProfessionalReActAgent

# Initialize
agent = ProfessionalReActAgent(tools, llm, config)

# Process query
result = await agent.process("Your question")

# Access stages
print(result['understanding'])
print(result['plan'])
print(result['execution'])
print(result['validation'])
print(result['response'])
```

### Custom Tools

```python
from src.orchestration.tools import BaseTool

class CustomTool(BaseTool):
    def __init__(self):
        super().__init__(
            name="custom",
            description="Custom tool description"
        )
    
    async def execute(self, input_data: str):
        # Your logic
        return {"result": "..."}

# Add to agent
tools.append(CustomTool())
```

## Performance

### Metrics

| Metric | Value |
|--------|-------|
| Stage 1 (Understanding) | 1-2s |
| Stage 2 (Planning) | 2-3s |
| Stage 3 (Execution) | 5-10s |
| Stage 4 (Validation) | 1-2s |
| Stage 5 (Synthesis) | 2-3s |
| **Total** | **11-20s** |

### Optimization

1. **Cache results** - Store frequent queries
2. **Parallel execution** - Run independent steps together
3. **Reduce stages** - Skip validation for simple queries
4. **Smaller models** - Use faster LLMs for simple tasks

## Summary

✅ **Professional multi-stage agent**
- 5-stage processing pipeline
- ReAct reasoning pattern
- Long-term memory

✅ **Beautiful CLI interface**
- Rich formatting
- Progress indicators
- Interactive commands

✅ **Production ready**
- Error handling
- Session management
- LangSmith tracing

**Experience professional AI-powered data analysis with a beautiful interface!** 🚀
