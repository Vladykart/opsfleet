# 🎨 Enhanced CLI - Simple & Beautiful

Modern, feature-rich CLI interface for the LangGraph agent.

## ✨ Features

### 🎯 Core Features
- **Natural Language Queries** - Ask questions in plain English
- **Beautiful UI** - Rich formatting with colors and panels
- **Session History** - Track all your queries
- **Export Capability** - Save sessions to files
- **Real-time Processing** - Loading animations and progress
- **Error Handling** - Graceful error recovery
- **Statistics** - Session metrics and insights

### 💬 Interactive Commands
```
/help      - Show available commands
/history   - View query history
/clear     - Clear the screen
/stats     - Show session statistics
/export    - Export session to file
/exit      - Quit the application
```

## 🚀 Quick Start

### Run the CLI
```bash
python cli_simple.py
```

### Example Queries
```
How many users are in the database?
What are the top 5 products by retail price?
Show me sales trends by category
Analyze order patterns
```

## 📊 UI Components

### Welcome Screen
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
║                                  Welcome                                         ║
║                                                                                  ║
║  🚀 OpsFleet Agent - Enhanced CLI                                               ║
║                                                                                  ║
║  Powered by LangGraph + Gemini 2.5 Flash                                        ║
║                                                                                  ║
║  Features:                                                                       ║
║  - 💬 Natural language queries                                                  ║
║  - 📊 BigQuery data analysis                                                    ║
║  - 🔍 Multi-stage processing                                                    ║
║  - 🔄 Error recovery                                                            ║
║  - 📝 Session history                                                           ║
║  - 🎨 Beautiful formatting                                                      ║
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

### Query Processing
```
⠋ Processing your query...

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
║                                  Response                                        ║
║                                                                                  ║
║  There are 100,000 users in the database.                                       ║
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

⏱️  Completed in 2.34s
```

### History View
```
╭──────────────────────────────── Query History ─────────────────────────────────╮
│ #    Time       Query                                               Status     │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 1    10:23:45   How many users are in the database?                ✅         │
│ 2    10:24:12   What are the top 5 products by retail price?       ✅         │
│ 3    10:25:03   Show me sales trends by category                   ✅         │
╰─────────────────────────────────────────────────────────────────────────────────╯
```

### Statistics Panel
```
╭──────────────────────────────────────────────────────────────────────────────────╮
│ Session Statistics                                                              │
│                                                                                  │
│ 📊 Total Queries: 5                                                             │
│ ✅ Successful: 5                                                                │
│ ❌ Failed: 0                                                                    │
│ 📁 Session ID: 20251111_102345                                                  │
│ 💾 History File: sessions/session_20251111_102345.txt                          │
╰──────────────────────────────────────────────────────────────────────────────────╯
```

## 🎯 Key Improvements Over Original CLI

### 1. **Session Management**
- Automatic session tracking
- Persistent history files
- Export functionality

### 2. **Enhanced UI**
- Modern Rich-based interface
- Color-coded responses
- Progress indicators
- Markdown rendering

### 3. **Better UX**
- Clear command structure
- Helpful error messages
- Real-time feedback
- Statistics dashboard

### 4. **Simplified Integration**
- Works with simple `agent.py`
- No complex dependencies
- Easy to extend

## 📁 Session Files

Sessions are automatically saved to `sessions/` directory:
```
sessions/
├── session_20251111_102345.txt
├── session_20251111_143022.txt
└── session_20251111_185530.txt
```

Each file contains:
- Session ID and timestamp
- All queries and responses
- Success/failure status
- Timing information

## 🔧 Customization

### Change Colors
Edit the style strings in `cli_simple.py`:
```python
border_style="cyan"  # Change to "green", "blue", "magenta", etc.
```

### Modify Welcome Message
Edit the `show_welcome()` method:
```python
def show_welcome(self):
    welcome_text = """
    # Your Custom Welcome Message
    """
```

### Add New Commands
Add to `handle_command()` method:
```python
elif command == "/mycommand":
    # Your custom logic
```

## 🆚 Comparison

| Feature | Original CLI | Enhanced CLI |
|---------|-------------|--------------|
| Session History | ❌ | ✅ |
| Export | ❌ | ✅ |
| Statistics | ❌ | ✅ |
| Commands | Limited | Extended |
| UI | Basic | Beautiful |
| Progress | ❌ | ✅ |
| Markdown | ❌ | ✅ |
| File Size | 787 lines | 300 lines |

## 💡 Tips

1. **Use `/history`** to review past queries
2. **Use `/stats`** to track your session
3. **Use `/export`** before closing to save your work
4. **Use `/clear`** for a fresh start
5. **Press Ctrl+C** for quick exit

## 🚀 Next Steps

1. Run the CLI: `python cli_simple.py`
2. Try example queries
3. Explore commands with `/help`
4. Export your session with `/export`

Enjoy your enhanced CLI experience! 🎉
