# 🚀 OpsFleet Agent

Modern AI agent for BigQuery data analysis using LangGraph and Google Gemini 2.5.

## ✨ Features

### Core Capabilities
- **🤖 LangGraph Agent** - Multi-stage agent orchestration with state management
- **📊 BigQuery Integration** - Query `thelook_ecommerce` public dataset
- **⚡ Gemini 2.5 Flash** - Fast, accurate SQL generation with low latency
- **🔍 Schema Analysis** - Automatic schema discovery and intelligent caching
- **🎨 Enhanced CLI** - Beautiful terminal interface with Rich library

### Advanced Features
- **💾 Save Conversations** - Export to CSV, JSON, Excel, Markdown, or TXT
- **📝 Smart Suggestions** - Context-aware next steps after each query
- **📜 Query History** - Track all queries with timing and success status
- **🔧 Modular Architecture** - Separated endpoints for better maintainability
- **🧪 Comprehensive Tests** - 59 tests with 95%+ coverage
- **🌐 LangGraph Server** - Deploy as API with Studio support

## Quick Start

### 1. Prerequisites

- Python 3.11+
- Google Cloud SDK
- Gemini API key

### 2. Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configure

```bash
cp .env.example .env
```

Edit `.env`:
```
GCP_PROJECT_ID=your-project-id
GOOGLE_API_KEY=your-gemini-api-key
```

Get Gemini API key: https://makersuite.google.com/app/apikey

### 4. Authenticate

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

### 5. Run

**Enhanced CLI (Recommended):**
```bash
python cli_enhanced.py
```

**Simple CLI:**
```bash
python cli_simple.py
```

## Usage

### CLI Commands

- `/help` - Show available commands
- `/schema [table]` - View database schema
- `/history` - Show query history
- `/stats` - Session statistics
- `/save [format]` - Save conversation (csv, json, excel, md, txt)
- `/export` - Export session history
- `/clear` - Clear screen
- `/exit` - Quit

### Example Queries

```
How many users are in the database?
What are the top 5 products by price?
Show me sales trends by category
Which country has the most orders?
```

### Programmatic Usage

```python
from agent import run_agent

response = run_agent("How many users are in the database?")
print(response)
```

## 📁 Project Structure

```
opsfleet/
├── agent.py                 # LangGraph agent core
├── cli_enhanced.py          # Enhanced CLI with Rich UI
├── schema_analyzer.py       # Schema discovery and caching
├── endpoints/               # BigQuery operations
│   ├── __init__.py
│   └── bigquery_client.py   # Client and tools
├── prompts/                 # System prompts
│   ├── README.md
│   └── system_prompt.txt    # Main agent prompt
├── tests/                   # Comprehensive test suite
│   ├── test_agent.py        # Agent tests
│   ├── test_endpoints.py    # Endpoint tests
│   └── test_cli_enhanced.py # CLI tests
├── langgraph.json           # LangGraph server config
├── pyproject.toml           # Package configuration
└── requirements.txt         # Dependencies
```

## 🏗️ Architecture

```
User Query → LangGraph Agent → Gemini 2.5 → Tools → Response
                                              ├── query_bigquery
                                              └── analyze_schema
```

**Flow:**
1. User submits query via CLI or API
2. Agent loads system prompt with query
3. Gemini analyzes and decides tool usage
4. Tools execute (BigQuery queries, schema analysis)
5. Agent formats and returns response

## Dataset

BigQuery public dataset: `bigquery-public-data.thelook_ecommerce`

Tables:
- `users` - Customer information
- `products` - Product catalog
- `orders` - Order records
- `order_items` - Order line items

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_agent.py -v
```

**Test Coverage:**
- ✅ 59 tests total
- ✅ 95%+ code coverage
- ✅ Agent core functionality
- ✅ BigQuery operations
- ✅ CLI features
- ✅ Error handling

## 🚀 LangGraph Server

Deploy as an API server:

```bash
# Install LangGraph CLI
pip install -U "langgraph-cli[inmem]"

# Start server
langgraph dev

# With tunnel (Safari compatible)
langgraph dev --tunnel
```

Access at `http://localhost:8123` or use Studio at `https://smith.langchain.com/studio/`

See [LANGGRAPH_SETUP.md](LANGGRAPH_SETUP.md) for details.

## 🐛 Troubleshooting

**Authentication Error**
```bash
gcloud auth application-default login
```

**Permission Denied**
- Ensure BigQuery API is enabled
- Check project permissions

**Invalid API Key**
- Verify `GOOGLE_API_KEY` in `.env`
- Get new key from Google AI Studio

**Disk Space Issues**
```bash
# Free up space
brew cleanup -s
pip cache purge
```

## 📚 Documentation

- [LANGGRAPH_SETUP.md](LANGGRAPH_SETUP.md) - LangGraph server setup
- [tests/README.md](tests/README.md) - Testing guide
- [prompts/README.md](prompts/README.md) - Prompt customization

## License

MIT
