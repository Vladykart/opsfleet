# OpsFleet Agent - Minimal Edition

AI agent for BigQuery data analysis using LangGraph and Google Gemini.

## Features

- **LangGraph Agent** - Multi-stage agent orchestration
- **BigQuery Integration** - Query `thelook_ecommerce` public dataset
- **Gemini 2.5 Flash** - Fast, accurate SQL generation
- **Schema Analysis** - Automatic schema discovery and caching
- **Enhanced CLI** - Beautiful terminal interface with Rich

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

```bash
python cli_simple.py
```

## Usage

### CLI Commands

- `/help` - Show available commands
- `/schema [table]` - View database schema
- `/history` - Show query history
- `/stats` - Session statistics
- `/export` - Export session history
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

## Architecture

```
User Query → Agent (Gemini) → Tools (BigQuery, Schema) → Response
```

**Components:**
- `agent.py` - LangGraph agent with BigQuery tools
- `schema_analyzer.py` - Schema discovery and caching
- `cli_simple.py` - Enhanced CLI interface

## Dataset

BigQuery public dataset: `bigquery-public-data.thelook_ecommerce`

Tables:
- `users` - Customer information
- `products` - Product catalog
- `orders` - Order records
- `order_items` - Order line items

## Troubleshooting

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

## License

MIT
