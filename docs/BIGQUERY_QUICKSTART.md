# BigQuery Data Analysis Agent - Quick Start

## 🚀 Quick Setup (5 minutes)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

Create or update `.env` file:

```bash
# Required
GOOGLE_API_KEY=your-gemini-api-key
GCP_PROJECT_ID=your-gcp-project-id

# Optional (for service account)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
```

Get your Gemini API key: https://makersuite.google.com/app/apikey

### 3. Run Examples

```bash
# Run predefined analysis examples
python examples/bigquery_analysis_examples.py --mode examples

# Or use interactive mode
python examples/bigquery_analysis_examples.py --mode interactive
```

## 📊 Example Queries

Try these queries in interactive mode:

```
Segment customers by purchase frequency and total spend

What are the top 20 best-selling products by revenue?

Show monthly sales trends for the past 12 months

Analyze sales distribution by country and state

Find customers who made purchases in multiple categories
```

## 🏗️ Architecture

```
User Query
    ↓
LangGraph Workflow (State Management)
    ↓
DataAnalysisAgent (LLM-powered SQL generation)
    ↓
BigQueryRunner (Execute queries)
    ↓
Results + Insights
```

## 🎯 Key Features

- **Automatic SQL Generation**: LLM generates optimized BigQuery SQL
- **Multi-Domain Analysis**: Customer, product, sales, geographic
- **State Management**: LangGraph tracks workflow state
- **Memory Integration**: Learns from previous analyses
- **Cost Optimization**: Query estimation and limits

## 📁 Key Files

- `src/bigquery_runner.py` - BigQuery client wrapper
- `src/agents/data_analysis_agent.py` - Main analysis agent
- `src/orchestration/workflow.py` - LangGraph workflow
- `examples/bigquery_analysis_examples.py` - Example usage

## 🔧 Configuration

Edit `config/agent_config.json`:

```json
{
  "bigquery": {
    "dataset": "bigquery-public-data.thelook_ecommerce"
  },
  "llm": {
    "primary": {
      "provider": "google",
      "model": "gemini-1.5-pro"
    }
  }
}
```

## 📚 Full Documentation

See `docs/BIGQUERY_AGENT_GUIDE.md` for comprehensive documentation.

## ⚠️ Rate Limits

**Google Gemini Free Tier:**
- 15 requests/minute
- 1,500 requests/day

**BigQuery Free Tier:**
- 1 TB query processing/month
- 10 GB storage

## 🐛 Troubleshooting

**Authentication Error:**
```bash
gcloud auth application-default login
```

**API Key Error:**
Get key from https://makersuite.google.com/app/apikey

**Rate Limit:**
Wait 4 seconds between requests or use AWS Bedrock fallback

## 🎓 Next Steps

1. Run the examples to see the agent in action
2. Try your own queries in interactive mode
3. Integrate into your workflow using the full system
4. Customize analysis types for your use case

## 💡 Tips

- Start with simple queries to understand the system
- Use LIMIT clauses to control data volume
- Monitor BigQuery costs with `get_query_stats()`
- Leverage the memory system for context
