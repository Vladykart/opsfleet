# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Install Dependencies (1 min)

```bash
cd /Users/vlad/PycharmProjects/opsfleet
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Set Up Environment (2 min)

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```bash
GOOGLE_API_KEY=your-gemini-key-here
CONTEXT7_API_KEY=your-context7-key-here
GCP_PROJECT_ID=your-gcp-project-id
```

### Step 3: Download BigQuery MCP Server (1 min)

**For macOS (ARM/M1/M2):**
```bash
curl -O https://storage.googleapis.com/genai-toolbox/v0.7.0/darwin/arm64/toolbox
chmod +x toolbox
```

**For macOS (Intel):**
```bash
curl -O https://storage.googleapis.com/genai-toolbox/v0.7.0/darwin/amd64/toolbox
chmod +x toolbox
```

### Step 4: Install Context7 MCP (30 sec)

```bash
npm install -g @upstash/context7-mcp
```

### Step 5: Start Weaviate (30 sec)

```bash
docker-compose up -d
```

Wait ~10 seconds for Weaviate to start, then verify:

```bash
curl http://localhost:8080/v1/meta
```

### Step 6: Run the Agent! (30 sec)

```bash
python build_multi_agent_system.py
```

## 🎯 Try Your First Query

When the agent starts, try:

```
Your query: What are the top 5 products by revenue in the thelook_ecommerce dataset?
```

## 📋 Checklist

Before running, make sure you have:

- [ ] Python 3.11+ installed
- [ ] Docker running
- [ ] Google Gemini API key
- [ ] Context7 API key
- [ ] Google Cloud project with BigQuery enabled
- [ ] `toolbox` binary downloaded and executable
- [ ] Context7 MCP installed via npm

## 🔑 Getting API Keys

### Google Gemini (Free)
1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy and paste into `.env`

### Context7 (Free)
1. Go to https://context7.com/dashboard
2. Sign up
3. Copy API key to `.env`

### Google Cloud BigQuery
1. Go to https://console.cloud.google.com
2. Create a project
3. Enable BigQuery API
4. Use Application Default Credentials:
   ```bash
   gcloud auth application-default login
   ```

## ❌ Troubleshooting

### "Failed to connect to MCP server"
- Make sure `toolbox` is executable: `chmod +x toolbox`
- Verify it's in the project directory: `ls -la toolbox`

### "Weaviate connection refused"
```bash
docker-compose down
docker-compose up -d
sleep 10
curl http://localhost:8080/v1/meta
```

### "Context7 not found"
```bash
npm install -g @upstash/context7-mcp
which npx  # Should show a path
```

### "BigQuery permission denied"
```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

## 📚 Next Steps

Once running:
1. Try different queries (see examples below)
2. Check logs in `logs/` directory
3. Customize persona in `config/personas/default.yaml`
4. Read full setup guide: `docs/guides/setup-guide.md`

## 💡 Example Queries

```
What are the top 10 customers by total spend?
Show me revenue trends by month for 2023
Which products have the highest profit margins?
Analyze customer demographics by country
What is the average order value by product category?
```

## 🎉 You're Ready!

The agent is now analyzing e-commerce data using:
- ✅ LangGraph for workflow orchestration
- ✅ MCP for tool integration
- ✅ Google Gemini for AI
- ✅ BigQuery for data
- ✅ Weaviate for memory

Happy analyzing! 🚀
