# BigQuery Data Analysis Agent Guide

## Overview

This guide covers the LangGraph-based BigQuery data analysis agent that performs complex analytics on the `thelook_ecommerce` public dataset.

## Architecture

### Components

1. **BigQueryRunner** (`src/bigquery_runner.py`)
   - Direct BigQuery client wrapper
   - Executes SQL queries and returns DataFrames
   - Retrieves table schemas
   - Provides query cost estimation

2. **DataAnalysisAgent** (`src/agents/data_analysis_agent.py`)
   - Specialized agent for data analysis tasks
   - Generates SQL queries using LLM
   - Performs analysis across multiple domains:
     - Customer segmentation
     - Product performance
     - Sales trends
     - Geographic patterns
     - Custom queries

3. **LangGraph Workflow** (`src/orchestration/workflow.py`)
   - State-based orchestration
   - Conditional routing based on query type
   - Memory integration for context
   - Validation and retry logic

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Google Cloud

#### Option A: Service Account (Recommended for Production)

1. Create a service account in Google Cloud Console
2. Download the JSON key file
3. Set environment variable:

```bash
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"
export GCP_PROJECT_ID="your-project-id"
```

#### Option B: User Credentials (Development)

```bash
gcloud auth application-default login
export GCP_PROJECT_ID="your-project-id"
```

### 3. Set API Keys

```bash
export GOOGLE_API_KEY="your-gemini-api-key"  # Get from https://makersuite.google.com/app/apikey
```

### 4. Update Configuration

Edit `config/agent_config.json`:

```json
{
  "bigquery": {
    "dataset": "bigquery-public-data.thelook_ecommerce",
    "project_id": "your-project-id"
  },
  "llm": {
    "primary": {
      "provider": "google",
      "model": "gemini-1.5-pro"
    }
  }
}
```

## Usage

### Running Examples

```bash
# Run predefined examples
python examples/bigquery_analysis_examples.py --mode examples

# Interactive mode
python examples/bigquery_analysis_examples.py --mode interactive
```

### Using the Full Workflow

```bash
python build_multi_agent_system.py
```

Example queries:
- "Segment customers by purchase frequency and total spend"
- "What are the top 20 best-selling products by revenue?"
- "Show monthly sales trends for the past 12 months"
- "Analyze sales distribution by country"

### Programmatic Usage

```python
import asyncio
from src.agents.data_analysis_agent import DataAnalysisAgent
import json

async def analyze():
    with open("config/agent_config.json") as f:
        config = json.load(f)
    
    agent = DataAnalysisAgent(config)
    await agent.initialize()
    
    result = await agent.analyze_customer_segmentation(
        "Find high-value customer segments"
    )
    
    print(f"SQL: {result['sql']}")
    print(f"Insights: {result['insights']}")
    print(f"Data shape: {result['data'].shape}")

asyncio.run(analyze())
```

## Available Tables

The `thelook_ecommerce` dataset includes:

- **users**: Customer demographics and registration data
- **orders**: Order transactions and status
- **order_items**: Individual items in orders
- **products**: Product catalog with categories and pricing
- **inventory_items**: Inventory tracking
- **distribution_centers**: Warehouse locations
- **events**: User behavior events

## Analysis Capabilities

### 1. Customer Segmentation

Analyzes customer behavior patterns:
- RFM (Recency, Frequency, Monetary) analysis
- Purchase frequency segmentation
- Customer lifetime value
- Cohort analysis

**Example Query:**
```
"Segment customers by purchase frequency and average order value"
```

### 2. Product Performance

Evaluates product and category performance:
- Top products by revenue/units
- Category trends
- Profit margin analysis
- Product recommendations

**Example Query:**
```
"What are the top 20 products by revenue in the last 6 months?"
```

### 3. Sales Trends

Identifies temporal patterns:
- Time series analysis (daily/weekly/monthly)
- Seasonality detection
- Growth rate calculations
- Peak period identification

**Example Query:**
```
"Show monthly sales trends with year-over-year growth rates"
```

### 4. Geographic Analysis

Examines spatial distribution:
- Sales by region/country/state
- Market penetration metrics
- Regional performance comparison
- Geographic customer distribution

**Example Query:**
```
"Analyze sales performance by country and identify top markets"
```

### 5. Custom Analysis

Handles complex, multi-dimensional queries:
- Cross-category analysis
- Custom metric calculations
- Advanced filtering and aggregations

**Example Query:**
```
"Find customers who purchased in multiple categories and calculate their retention rate"
```

## LangGraph Workflow

### State Management

The workflow uses `AgentState` (TypedDict) to track:
- User query and context
- Analysis plan and type
- Generated SQL queries
- Query results (DataFrames)
- Insights and metrics
- Validation status
- Report and recommendations

### Workflow Nodes

1. **retrieve_memory**: Fetch relevant historical context
2. **plan_analysis**: Determine analysis type and required tables
3. **execute_bigquery_analysis**: Direct BigQuery analysis (fast path)
4. **generate_sql**: Custom SQL generation (alternative path)
5. **execute_query**: Run SQL queries
6. **validate_results**: Check data quality
7. **analyze_data**: Extract insights
8. **generate_report**: Create formatted report
9. **store_memory**: Save results for future context

### Conditional Routing

The workflow automatically routes queries:
- **BigQuery path**: For standard analysis types (customer, product, sales, geographic)
- **Custom path**: For complex or non-standard queries

## Best Practices

### 1. Query Optimization

- Use `LIMIT` clauses to control data volume
- Leverage CTEs for complex queries
- Avoid `SELECT *` in production
- Use partitioned tables when available

### 2. Cost Management

The BigQuery free tier includes:
- 1 TB of query processing per month
- 10 GB of storage

Monitor costs:
```python
stats = bq_runner.get_query_stats(sql_query)
print(f"Estimated cost: ${stats['estimated_cost_usd']:.4f}")
```

### 3. Error Handling

The agent includes:
- Automatic retry logic (up to 2 retries)
- Validation checks
- Graceful degradation
- Detailed error logging

### 4. Rate Limits

Google Gemini free tier:
- 15 requests per minute
- 1 million tokens per minute
- 1,500 requests per day

Implement delays if hitting limits:
```python
import time
time.sleep(4)  # 4 seconds between requests
```

## Advanced Features

### Schema Inspection

```python
schema = bq_runner.get_table_schema("orders")
for field in schema:
    print(f"{field['name']}: {field['type']}")
```

### Query Statistics

```python
df = bq_runner.execute_query(sql)
stats = bq_runner.get_query_stats(sql)
print(f"Bytes processed: {stats['total_bytes_processed']:,}")
```

### Custom Analysis Types

Extend `DataAnalysisAgent` with new methods:

```python
async def analyze_churn_prediction(self, query: str) -> Dict[str, Any]:
    # Custom churn analysis logic
    pass
```

## Troubleshooting

### Authentication Issues

```
Error: Could not automatically determine credentials
```

**Solution**: Set `GOOGLE_APPLICATION_CREDENTIALS` or run `gcloud auth application-default login`

### API Key Issues

```
Error: GOOGLE_API_KEY not set
```

**Solution**: Get API key from https://makersuite.google.com/app/apikey and set environment variable

### Rate Limit Errors

```
Error: Resource exhausted (quota)
```

**Solution**: 
- Wait before retrying
- Use AWS Bedrock as fallback
- Implement exponential backoff

### Query Errors

```
Error: Syntax error in SQL
```

**Solution**: 
- Check generated SQL
- Verify table names and dataset
- Ensure BigQuery Standard SQL syntax

## Performance Tips

1. **Use specific columns**: Avoid `SELECT *`
2. **Filter early**: Apply WHERE clauses before joins
3. **Limit results**: Use LIMIT for exploratory queries
4. **Cache results**: Store frequently accessed data
5. **Batch queries**: Combine multiple analyses when possible

## Security Considerations

1. **Service Account Permissions**: Grant minimal required permissions
2. **API Key Protection**: Never commit keys to version control
3. **Data Access**: Ensure compliance with data privacy regulations
4. **Query Validation**: Sanitize user inputs to prevent injection

## Next Steps

1. Explore the example queries in `examples/bigquery_analysis_examples.py`
2. Customize the agent for your specific use cases
3. Integrate with your existing data pipelines
4. Add custom visualization layers
5. Implement caching for frequently run queries

## Resources

- [BigQuery Documentation](https://cloud.google.com/bigquery/docs)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Google Gemini API](https://ai.google.dev/)
- [thelook_ecommerce Dataset](https://console.cloud.google.com/marketplace/product/bigquery-public-data/thelook-ecommerce)
