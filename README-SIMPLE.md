# BigQuery Agent with LangGraph

A simple AI agent that answers questions about BigQuery data using LangGraph and Google Gemini.

## Features

- **LangGraph-based agent** - Uses LangGraph for agent orchestration
- **BigQuery integration** - Queries the `thelook_ecommerce` public dataset
- **Gemini LLM** - Powered by Google's Gemini 1.5 Flash model
- **ADC Authentication** - Uses Application Default Credentials (no service account keys needed)

## Prerequisites

- Python 3.11+
- Google Cloud SDK installed and configured
- Access to Google Cloud BigQuery
- Gemini API key

## Setup

### 1. Install Google Cloud SDK

```bash
# Install gcloud CLI
# Visit: https://cloud.google.com/sdk/docs/install

# Authenticate with your Google account
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID
```

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-simple.txt
```

### 3. Configure Environment

Create a `.env` file:

```bash
cp .env.example.new .env
```

Edit `.env` and add:

```
GCP_PROJECT_ID=your-project-id
GOOGLE_API_KEY=your-gemini-api-key
```

**Get your Gemini API key:**
- Visit https://makersuite.google.com/app/apikey
- Create an API key
- Add it to your `.env` file

### 4. Run the Agent

```bash
python agent.py
```

## Usage

### Programmatic Usage

```python
from agent import run_agent

# Ask a question
response = run_agent("How many users are in the database?")
print(response)
```

### Example Queries

```python
# Count queries
run_agent("How many users are in the database?")
run_agent("How many products do we have?")

# Top N queries  
run_agent("What are the top 5 products by retail price?")
run_agent("Show me the top 10 countries by number of users")

# Recent data
run_agent("Show me 5 recent orders")
run_agent("What are the latest 10 products added?")

# Aggregations
run_agent("What is the average order value?")
run_agent("Which product category has the most items?")
```

## Architecture

The agent uses a simple LangGraph workflow:

```
User Query → Agent (with LLM) → Tool (BigQuery) → Agent → Response
```

**Components:**

1. **LangGraph StateGraph** - Manages the agent workflow
2. **Gemini 1.5 Flash** - LLM for understanding queries and generating SQL
3. **BigQuery Tool** - Executes SQL queries
4. **ADC** - Handles authentication automatically

## Dataset

The agent has access to the `bigquery-public-data.thelook_ecommerce` dataset:

- **users** - Customer information
- **products** - Product catalog  
- **orders** - Order records
- **order_items** - Order line items

## Troubleshooting

**"Could not automatically determine credentials"**
- Run `gcloud auth application-default login`
- Ensure you've set your project: `gcloud config set project YOUR_PROJECT_ID`

**"Permission denied on BigQuery"**
- Ensure your Google account has BigQuery access
- The public dataset should be accessible by default

**"Invalid API key"**
- Check your `GOOGLE_API_KEY` in `.env`
- Get a new key from https://makersuite.google.com/app/apikey

## Project Structure

```
opsfleet/
├── agent.py                 # Main agent implementation
├── requirements-simple.txt  # Dependencies
├── .env.example.new        # Environment template
└── README-SIMPLE.md        # This file
```

## License

MIT
