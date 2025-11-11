# 🚀 Start Here - Quick Reference

## What You Have

A complete **LangGraph Data Analysis Agent** with:
- Multi-agent system for e-commerce data analysis
- MCP integration (BigQuery + Context7)
- Weaviate vector memory
- Google Gemini LLM
- Full documentation

## Your Current Status

Based on your `.env` file:
- ✅ Context7 API key configured
- ⚠️ Google Gemini API key needed
- ⚠️ GCP Project ID needed
- ⚠️ BigQuery MCP server (toolbox) needed

## Next 3 Steps

### 1. Complete Environment Setup (5 min)

Edit `/Users/vlad/PycharmProjects/opsfleet/.env`:

```bash
# Get Gemini key: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your-actual-gemini-key

# Your GCP project
GCP_PROJECT_ID=your-gcp-project-id
```

### 2. Install MCP Servers (2 min)

**BigQuery MCP:**
```bash
cd /Users/vlad/PycharmProjects/opsfleet
curl -O https://storage.googleapis.com/genai-toolbox/v0.7.0/darwin/arm64/toolbox
chmod +x toolbox
```

**Context7 MCP:**
```bash
npm install -g @upstash/context7-mcp
```

### 3. Start Services & Run (3 min)

```bash
# Start Weaviate
docker-compose up -d

# Verify setup
python verify_setup.py

# Run the agent
python build_multi_agent_system.py
```

## Test Query

Once running, try:
```
What are the top 10 products by revenue in the thelook_ecommerce dataset?
```

## Documentation Map

- **QUICKSTART.md** → 5-minute setup guide
- **SETUP_CHECKLIST.md** → Complete setup checklist
- **docs/guides/setup-guide.md** → Detailed setup instructions
- **PROJECT_SUMMARY.md** → Full project overview
- **GITHUB_SETUP.md** → Push to GitHub (optional)

## Need Help?

1. Run verification: `python verify_setup.py`
2. Check logs: `logs/`
3. Review: `SETUP_CHECKLIST.md`

## GitHub Repository (Optional)

To create a private GitHub repo:
```bash
./init_github_repo.sh
```

---

**You're almost there!** Complete steps 1-3 above and you'll be running queries in minutes. 🎉
