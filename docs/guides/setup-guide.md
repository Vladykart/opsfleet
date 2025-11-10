# LangGraph Data Analysis Agent - Setup Guide

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose
- Google Cloud account with BigQuery access
- Context7 API key (free tier available)
- Google Gemini API key

## Step 1: Clone and Navigate

```bash
cd /Users/vlad/PycharmProjects/opsfleet
```

## Step 2: Install Python Dependencies

```bash
python -m venv venv
source venv/bin/activate  # On macOS/Linux
pip install -r requirements.txt
```

## Step 3: Set Up Google Cloud BigQuery

### Option A: Using Service Account (Recommended)

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing one
3. Enable BigQuery API
4. Create a service account:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Grant "BigQuery User" and "BigQuery Data Viewer" roles
5. Create and download JSON key
6. Save the key file in your project directory

### Option B: Using Application Default Credentials

```bash
gcloud auth application-default login
```

## Step 4: Install MCP Servers

### BigQuery MCP Server (Google Toolbox)

```bash
# For macOS (ARM)
curl -O https://storage.googleapis.com/genai-toolbox/v0.7.0/darwin/arm64/toolbox
chmod +x toolbox
mv toolbox /Users/vlad/PycharmProjects/opsfleet/

# For macOS (Intel)
curl -O https://storage.googleapis.com/genai-toolbox/v0.7.0/darwin/amd64/toolbox
chmod +x toolbox
mv toolbox /Users/vlad/PycharmProjects/opsfleet/

# For Linux
curl -O https://storage.googleapis.com/genai-toolbox/v0.7.0/linux/amd64/toolbox
chmod +x toolbox
mv toolbox /Users/vlad/PycharmProjects/opsfleet/
```

### Context7 MCP Server

```bash
npm install -g @upstash/context7-mcp
```

## Step 5: Get API Keys

### Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key

### Context7 API Key

1. Visit [Context7 Dashboard](https://context7.com/dashboard)
2. Sign up for free account
3. Copy your API key

### AWS Bedrock (Optional - Fallback LLM)

1. Create AWS account
2. Enable Bedrock service
3. Request access to Claude models
4. Get AWS credentials

## Step 6: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` file:

```bash
# Google Cloud
GCP_PROJECT_ID=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/Users/vlad/PycharmProjects/opsfleet/service-account-key.json

# Context7
CONTEXT7_API_KEY=your-context7-api-key

# Google Gemini
GOOGLE_API_KEY=your-gemini-api-key

# AWS Bedrock (Optional)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_REGION=us-east-1

# Weaviate
WEAVIATE_URL=http://localhost:8080

# Application
LOG_LEVEL=INFO
ENABLE_CACHING=true
MAX_RETRIES=3
```

## Step 7: Start Weaviate Vector Database

```bash
docker-compose up -d
```

Verify Weaviate is running:

```bash
curl http://localhost:8080/v1/meta
```

## Step 8: Test MCP Servers

### Test BigQuery MCP

```bash
python -c "
import asyncio
from src.mcp_client import get_mcp_client

async def test():
    client = await get_mcp_client()
    datasets = await client.call_tool('bigquery', 'list-datasets', {})
    print('Datasets:', datasets)

asyncio.run(test())
"
```

### Test Context7 MCP

```bash
python -c "
import asyncio
from src.mcp_client import get_mcp_client

async def test():
    client = await get_mcp_client()
    result = await client.call_tool('context7', 'resolve-library-id', {'libraryName': 'langgraph'})
    print('Library ID:', result)

asyncio.run(test())
"
```

## Step 9: Run the Agent

```bash
python build_multi_agent_system.py
```

## Step 10: Test with Sample Query

When the agent starts, try:

```
Your query: What are the top 10 products by revenue?
```

## Troubleshooting

### MCP Server Connection Issues

**Problem:** `Failed to connect to bigquery MCP server`

**Solution:**
- Verify `toolbox` binary is executable: `chmod +x toolbox`
- Check Google Cloud credentials are valid
- Ensure `GCP_PROJECT_ID` is set correctly

### Weaviate Connection Issues

**Problem:** `Connection refused to Weaviate`

**Solution:**
```bash
docker-compose down
docker-compose up -d
docker-compose logs weaviate
```

### Context7 API Issues

**Problem:** `Context7 API key invalid`

**Solution:**
- Verify API key is correct in `.env`
- Check Context7 dashboard for rate limits
- Ensure `npx` is available: `npm install -g npx`

### BigQuery Permission Issues

**Problem:** `Permission denied on BigQuery`

**Solution:**
- Verify service account has correct roles
- Check project ID matches
- Ensure BigQuery API is enabled

## Verification Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created and activated
- [ ] All dependencies installed from requirements.txt
- [ ] Google Cloud project created
- [ ] BigQuery API enabled
- [ ] Service account created with correct permissions
- [ ] Service account key downloaded
- [ ] `toolbox` binary downloaded and executable
- [ ] Context7 MCP installed via npm
- [ ] Google Gemini API key obtained
- [ ] Context7 API key obtained
- [ ] `.env` file configured with all keys
- [ ] Weaviate running via Docker
- [ ] MCP servers tested successfully
- [ ] Agent runs without errors

## Next Steps

- Read [Architecture Documentation](../architecture/component-breakdown.md)
- Explore sample queries in `tests/fixtures/sample_queries.json`
- Customize agent persona in `config/personas/default.yaml`
- Review logs in `logs/` directory

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review error messages carefully
- Verify all API keys are valid
- Ensure all services are running
