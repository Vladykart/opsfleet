# 🚀 Quick Start: Professional CLI Chat

## Installation (30 seconds)

```bash
# 1. Install dependencies
pip install rich

# 2. Make CLI executable
chmod +x cli_chat.py

# 3. Run!
python cli_chat.py
```

## First Run

```bash
python cli_chat.py
```

You'll see:

```
🚀 BigQuery Data Analysis Agent

Welcome to your professional AI-powered data analysis assistant!

✓ Ready! Type your question or 'help' for commands.

You: _
```

## Try These Queries

### Simple Query
```
You: What are the top 10 products by revenue?
```

### Complex Analysis
```
You: Analyze customer segments by purchase frequency and show trends
```

### Follow-up (uses memory!)
```
You: Compare those segments with last year
```

## Commands

| Command | What It Does |
|---------|--------------|
| `help` | Show all commands |
| `history` | View past queries |
| `stats` | Session statistics |
| `clear` | Clear screen |
| `exit` | Quit |

## What You'll See

### Stage Indicators
```
● UNDERSTANDING Analyzing query...
● PLANNING Creating execution plan...
● EXECUTION Executing 3 steps...
● VALIDATION Checking results...
● SYNTHESIS Generating response...
```

### Beautiful Output
```
┌─ Understanding ─────────────────────────┐
│ Intent: Analyze product revenue         │
│ Complexity: simple                      │
└─────────────────────────────────────────┘

┌─ Response ──────────────────────────────┐
│ ## Top 10 Products                      │
│                                         │
│ ### Key Findings                        │
│ • Product A: $15,351                    │
│ • Product B: $14,250                    │
│ • Top 10 = 23% of revenue               │
└─────────────────────────────────────────┘
```

## Features

✅ **5-Stage Processing** - Professional analysis pipeline  
✅ **Long-Term Memory** - Remembers conversation  
✅ **Beautiful Interface** - Rich formatting  
✅ **Context-Aware** - Builds on previous queries  
✅ **LangSmith Tracing** - Full observability  

## Tips

### Get Better Results

1. **Be specific**: "Top 10 products by revenue in Q1 2024"
2. **Ask follow-ups**: "Now compare with Q1 2023"
3. **Request formats**: "Show as a table" or "Generate a report"

### Use Memory

The agent remembers your conversation:

```
You: What are top products?
Agent: [Shows top products]

You: Now analyze their trends
Agent: [Uses previous product list automatically]
```

### View History

```
You: history

┌─ Conversation History ──────────────────┐
│ # │ Query              │ Time            │
├───┼────────────────────┼─────────────────┤
│ 1 │ What are top 5...  │ 23:50:15        │
│ 2 │ Analyze trends...  │ 23:51:30        │
└───┴────────────────────┴─────────────────┘
```

## Troubleshooting

### "Module not found: rich"
```bash
pip install rich
```

### "Permission denied"
```bash
chmod +x cli_chat.py
```

### "Connection error"
```bash
# Check Ollama is running
ollama serve

# Check BigQuery credentials
echo $GOOGLE_APPLICATION_CREDENTIALS
```

## Next Steps

1. ✅ Run the CLI
2. ✅ Try example queries
3. ✅ Explore commands
4. 📊 View traces at https://smith.langchain.com/
5. 📖 Read full docs: `docs/PROFESSIONAL_CLI.md`

## Summary

```bash
# Start chatting in 3 commands:
pip install rich
chmod +x cli_chat.py
python cli_chat.py
```

**Enjoy your professional AI assistant!** 🎉
