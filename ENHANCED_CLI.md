# Enhanced CLI - Rich Chat Style

Beautiful, modern CLI interface inspired by [rich-chat](https://github.com/qnixsynapse/rich-chat).

## Features

### 🎨 Visual Enhancements
- **Beautiful Banner** - ASCII art banner with centered layout
- **Rich Panels** - Bordered panels for all outputs
- **Color Coding** - Semantic colors (cyan for prompts, green for success, red for errors)
- **Progress Indicators** - Spinners and progress bars for long operations
- **Markdown Rendering** - Full markdown support in responses

### ⌨️ Keyboard Navigation
- **Ctrl+C** - Exit application
- **Ctrl+D** - Alternative exit
- **Enter** - Send query
- **Shift+Enter** - Multiline input (via prompt_toolkit)
- **Arrow Keys** - Navigate command history

### 📋 Commands
- `/help` - Show command menu with descriptions
- `/history` - View last 10 queries with status
- `/schema [table]` - Show database schema (all tables or specific)
- `/stats` - Session statistics (queries, success rate, avg time)
- `/save [format]` - Save conversation (txt, csv, json, excel, md)
- `/export` - Export session history to file
- `/clear` - Clear screen and show banner
- `/exit` or `/quit` - Exit application

### 💾 Session Management & Data Export
- **Auto-save History** - All queries saved to `.opsfleet_history`
- **Session Files** - Each session exported to `sessions/session_YYYYMMDD_HHMMSS.txt`
- **Query Tracking** - Track success/failure, timing, and responses
- **Pandas Export** - Save conversations in multiple formats:
  - `txt` - Plain text format
  - `csv` - Comma-separated values (opens in Excel)
  - `json` - JSON format for APIs
  - `excel` - Native Excel format (.xlsx)
  - `md` - Markdown format for documentation

## Usage

### Quick Start
```bash
# Activate virtual environment
source venv/bin/activate

# Run enhanced CLI
python3 cli_enhanced.py

# Or use demo script
./demo_cli.sh
```

### Example Session
```
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║              🚀 OpsFleet Agent - BigQuery AI              ║
║                                                           ║
║              Powered by LangGraph + Gemini 2.5            ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝

──────────────────────────────────────────────────────────────
💬 You › How many users are in the database?

⠋ Processing your query...

┌─ 🤖 Assistant ────────────────────────────────────────────┐
│                                                            │
│  There are 100,000 users in the database.                 │
│                                                            │
└────────────────────────────────────────────────────────────┘

⏱️  Completed in 2.34s

──────────────────────────────────────────────────────────────
💬 You › /help
```

## Architecture

### Components
1. **RichChatCLI** - Main CLI class
2. **PromptSession** - Keyboard input handling with history
3. **Rich Console** - Beautiful terminal output
4. **Agent Integration** - Seamless connection to LangGraph agent

### Key Libraries
- `rich` - Terminal formatting and panels
- `prompt_toolkit` - Advanced input with keyboard bindings
- `pandas` - Data export and manipulation
- `openpyxl` - Excel file support
- `langgraph` - Agent orchestration
- `google-cloud-bigquery` - Database queries

## Comparison

| Feature | cli_simple.py | cli_enhanced.py |
|---------|---------------|-----------------|
| Banner | Basic | ASCII art with centering |
| Input | rich.Prompt | prompt_toolkit with history |
| Keyboard | Basic | Full keyboard navigation |
| History | In-memory | Persistent file history |
| Commands | Text-based | Menu with descriptions |
| Panels | Simple | Rich panels with icons |
| Progress | Spinner | Spinner + progress bars |
| Export | Basic | Formatted with metadata |

## Tips

1. **Multiline Queries** - Use Shift+Enter for complex questions
2. **Command History** - Use arrow keys to recall previous queries
3. **Quick Schema** - Type `/schema` to see all tables at once
4. **Save Conversations** - Use `/save csv` or `/save excel` to export data
5. **Export Sessions** - Use `/export` before exiting to save your work
6. **Clear Screen** - Type `/clear` to reset the view

### Save Format Examples
```bash
/save txt       # Plain text format
/save csv       # CSV for Excel/analysis
/save json      # JSON for APIs/scripts
/save excel     # Native Excel format
/save md        # Markdown for docs
```

## Future Enhancements

- [ ] Syntax highlighting for SQL queries
- [ ] Query suggestions/autocomplete
- [ ] Real-time streaming responses
- [ ] Custom themes/color schemes
- [ ] Query templates
- [ ] Favorite queries bookmarking
- [ ] Multi-session management
- [ ] Export to different formats (JSON, CSV)

## Credits

Inspired by [rich-chat](https://github.com/qnixsynapse/rich-chat) by qnixsynapse.
