# Demo Commands - Enhanced CLI

Quick reference for demonstrating the enhanced CLI features.

## Basic Demo Flow

### 1. Start the CLI
```bash
source venv/bin/activate
python3 cli_enhanced.py
```

### 2. Show Help
```
/help
```
**Shows:** Beautiful command table with all available commands

### 3. Ask Questions
```
How many users are in the database?
```
```
What are the top 5 products by retail price?
```
```
Show me recent orders
```

### 4. View History
```
/history
```
**Shows:** Last 10 queries with status indicators (✅/❌)

### 5. Check Stats
```
/stats
```
**Shows:** Session statistics (total queries, success rate, avg time)

### 6. View Schema
```
/schema
```
**Shows:** All tables with row counts, columns, sizes

```
/schema users
```
**Shows:** Detailed schema for users table with columns and relationships

### 7. Save Conversation

**CSV Format (Excel-compatible):**
```
/save csv
```

**JSON Format (for APIs):**
```
/save json
```

**Excel Format (native .xlsx):**
```
/save excel
```

**Markdown Format (for docs):**
```
/save md
```

**Plain Text:**
```
/save txt
```

### 8. Export Session
```
/export
```
**Creates:** `sessions/session_YYYYMMDD_HHMMSS.txt`

### 9. Clear Screen
```
/clear
```
**Refreshes:** Screen and shows banner again

### 10. Exit
```
/exit
```
or press `Ctrl+C`

## Demo Script

### Quick 2-Minute Demo
```bash
# 1. Start CLI
python3 cli_enhanced.py

# 2. Show help
/help

# 3. Ask a question
How many users are in the database?

# 4. View history
/history

# 5. Save as CSV
/save csv

# 6. Exit
/exit
```

### Full 5-Minute Demo
```bash
# Start
python3 cli_enhanced.py

# Commands
/help
/schema
/schema users

# Questions
How many users are in the database?
What are the top 5 products by price?
Show me recent orders

# Review
/history
/stats

# Save in multiple formats
/save csv
/save json
/save excel

# Export
/export

# Exit
/exit
```

## Sample Questions

### Easy Questions
- How many users are in the database?
- How many products do we have?
- Show me 5 recent orders

### Medium Questions
- What are the top 5 products by retail price?
- Which country has the most users?
- What is the average order value?

### Complex Questions
- Show me sales trends by category for the last month
- Which products have the highest profit margin?
- What is the customer retention rate?

## Features to Highlight

### 1. Beautiful UI
- ASCII art banner
- Rich panels with borders
- Color-coded output
- Icons and emojis

### 2. Keyboard Navigation
- Arrow keys for history
- Ctrl+C to exit
- Enter to send
- Shift+Enter for multiline (via prompt_toolkit)

### 3. Data Export
- Multiple formats (CSV, JSON, Excel, Markdown, Text)
- Pandas-powered
- Automatic timestamps
- File size reporting

### 4. Session Management
- Auto-save history
- Session files
- Query tracking
- Success/failure status

### 5. Schema Awareness
- View all tables
- Detailed column info
- Relationships
- Statistics

## Tips for Demo

1. **Start with /help** - Shows all features at once
2. **Ask simple questions first** - Build confidence
3. **Show /history** - Demonstrates tracking
4. **Save in different formats** - Highlight flexibility
5. **View saved files** - Show actual output
6. **End with /stats** - Summary of session

## Common Issues

### Schema Warnings
```
Key 'title' is not supported in schema, ignoring
```
**Solution:** These are harmless warnings from LangChain, ignore them

### LangSmith Tracing
```
✅ LangSmith tracing enabled
```
**Info:** Optional tracing for debugging, can be disabled in .env

## File Locations

### Session Files
```
sessions/session_YYYYMMDD_HHMMSS.txt
```

### Conversation Exports
```
sessions/conversation_YYYYMMDD_HHMMSS.csv
sessions/conversation_YYYYMMDD_HHMMSS.json
sessions/conversation_YYYYMMDD_HHMMSS.xlsx
sessions/conversation_YYYYMMDD_HHMMSS.md
sessions/conversation_YYYYMMDD_HHMMSS.txt
```

### Command History
```
.opsfleet_history
```

## Keyboard Shortcuts

- **Enter** - Send query
- **Shift+Enter** - Multiline input
- **Ctrl+C** - Exit
- **Ctrl+D** - Alternative exit
- **↑/↓** - Navigate command history

## Color Coding

- **Cyan** - Prompts, commands, info
- **Green** - Success, responses
- **Yellow** - Warnings, tips
- **Red** - Errors
- **Magenta** - Highlights
- **Dim** - Secondary info

## Next Steps

After demo:
1. Check `sessions/` directory for saved files
2. Open CSV in Excel
3. View JSON in text editor
4. Read Markdown in GitHub
5. Review test results: `pytest test_cli_enhanced.py -v`
