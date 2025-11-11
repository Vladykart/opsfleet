# Setup Checklist

Use this checklist to ensure your LangGraph Data Analysis Agent is properly configured.

## ✅ Pre-Setup

- [ ] Python 3.11+ installed
- [ ] Docker Desktop installed and running
- [ ] Node.js and npm installed
- [ ] Git installed
- [ ] GitHub account created

## 🔑 API Keys Obtained

- [ ] Google Gemini API key from https://makersuite.google.com/app/apikey
- [ ] Context7 API key from https://context7.com/dashboard
- [ ] Google Cloud project created
- [ ] BigQuery API enabled in GCP project
- [ ] (Optional) AWS Bedrock access configured

## 📦 Installation Steps

### 1. Clone/Navigate to Project

- [ ] Project directory: `/Users/vlad/PycharmProjects/opsfleet`

### 2. Python Environment

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

- [ ] Virtual environment created
- [ ] Dependencies installed

### 3. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your API keys
```

- [ ] `.env` file created
- [ ] `GOOGLE_API_KEY` configured
- [ ] `CONTEXT7_API_KEY` configured
- [ ] `GCP_PROJECT_ID` configured
- [ ] `WEAVIATE_URL` set (default: http://localhost:8080)

### 4. MCP Servers

**BigQuery MCP (toolbox):**

```bash
# For macOS ARM (M1/M2/M3)
curl -O https://storage.googleapis.com/genai-toolbox/v0.7.0/darwin/arm64/toolbox
chmod +x toolbox

# For macOS Intel
curl -O https://storage.googleapis.com/genai-toolbox/v0.7.0/darwin/amd64/toolbox
chmod +x toolbox
```

- [ ] `toolbox` binary downloaded
- [ ] `toolbox` is executable (`chmod +x toolbox`)
- [ ] `toolbox` in project root directory

**Context7 MCP:**

```bash
npm install -g @upstash/context7-mcp
```

- [ ] Context7 MCP installed globally

### 5. Weaviate Vector Database

```bash
docker-compose up -d
```

- [ ] Docker Compose started
- [ ] Weaviate running (verify: `curl http://localhost:8080/v1/meta`)

### 6. Verify Setup

```bash
python verify_setup.py
```

- [ ] All verification checks passed

## 🧪 Testing

### Test MCP Connections

**Test BigQuery MCP:**

```bash
python -c "
import asyncio
from src.mcp_client import get_mcp_client

async def test():
    client = await get_mcp_client()
    tools = await client.list_tools('bigquery')
    print('BigQuery tools:', [t.get('name') for t in tools])

asyncio.run(test())
"
```

- [ ] BigQuery MCP connection successful

**Test Context7 MCP:**

```bash
python -c "
import asyncio
from src.mcp_client import get_mcp_client

async def test():
    client = await get_mcp_client()
    result = await client.call_tool('context7', 'resolve-library-id', {'libraryName': 'langgraph'})
    print('Context7 result:', result)

asyncio.run(test())
"
```

- [ ] Context7 MCP connection successful

### Run the Agent

```bash
python build_multi_agent_system.py
```

- [ ] Agent starts without errors
- [ ] MCP servers connect successfully
- [ ] Can process test query

## 🐙 GitHub Setup (Optional)

### Initialize Repository

```bash
./init_github_repo.sh
```

OR manually:

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git push -u origin main
```

- [ ] Git repository initialized
- [ ] Initial commit created
- [ ] Private GitHub repository created
- [ ] Code pushed to GitHub

### Repository Configuration

- [ ] Repository set to Private
- [ ] Branch protection rules configured
- [ ] Repository secrets added (if using CI/CD)
- [ ] Collaborators invited

## 📊 Final Verification

Run through this quick test:

1. **Start the agent:**
   ```bash
   python build_multi_agent_system.py
   ```

2. **Test query:**
   ```
   What are the top 5 products by revenue?
   ```

3. **Expected output:**
   - Agent retrieves memory context
   - Plans analysis
   - Generates SQL
   - Executes query via BigQuery
   - Analyzes results
   - Generates report

- [ ] Agent processes query successfully
- [ ] Report generated
- [ ] No errors in logs

## 🎯 Success Criteria

All items checked = Ready for production use! 🎉

## 📝 Notes

**Common Issues:**

1. **"toolbox not found"**
   - Ensure `toolbox` is in project root
   - Run `chmod +x toolbox`

2. **"Weaviate connection refused"**
   - Run `docker-compose up -d`
   - Wait 10 seconds for startup
   - Verify: `curl http://localhost:8080/v1/meta`

3. **"Context7 API key invalid"**
   - Check `.env` file has correct key
   - No extra spaces or quotes
   - Key starts with `ctx7sk-`

4. **"BigQuery permission denied"**
   - Run `gcloud auth application-default login`
   - Verify `GCP_PROJECT_ID` is correct
   - Ensure BigQuery API is enabled

## 📚 Documentation Reference

- **QUICKSTART.md** - 5-minute setup
- **docs/guides/setup-guide.md** - Detailed setup
- **PROJECT_SUMMARY.md** - Project overview
- **GITHUB_SETUP.md** - GitHub repository setup

## 🆘 Getting Help

If you encounter issues:

1. Check logs in `logs/` directory
2. Run `python verify_setup.py`
3. Review error messages carefully
4. Consult documentation
5. Open an issue on GitHub (if repository is set up)

---

**Last Updated:** 2025-11-10
