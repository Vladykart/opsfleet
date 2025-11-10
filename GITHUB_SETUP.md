# GitHub Repository Setup Guide

## 🚀 Quick Setup (Automated)

Run the initialization script:

```bash
chmod +x init_github_repo.sh
./init_github_repo.sh
```

This script will:
- Initialize Git repository
- Create initial commit
- Guide you through creating a private GitHub repository
- Push code to GitHub

## 📋 Manual Setup (Step-by-Step)

### Step 1: Initialize Git Repository

```bash
cd /Users/vlad/PycharmProjects/opsfleet
git init
```

### Step 2: Add All Files

```bash
git add .
```

### Step 3: Create Initial Commit

```bash
git commit -m "Initial commit: LangGraph Data Analysis Agent with MCP integration

- Multi-agent system with LangGraph orchestration
- MCP integration for BigQuery and Context7
- Weaviate vector store for semantic memory
- Google Gemini + AWS Bedrock LLM support
- Comprehensive documentation and setup guides
- Docker configuration for Weaviate
- CI/CD pipeline with GitHub Actions"
```

### Step 4: Create Private Repository on GitHub

**Option A: Using GitHub CLI (Recommended)**

```bash
gh repo create YOUR_USERNAME/langgraph-data-agent \
  --private \
  --source=. \
  --remote=origin \
  --description="LangGraph-based data analysis agent with MCP integration"
```

**Option B: Using GitHub Web Interface**

1. Go to https://github.com/new
2. Fill in repository details:
   - **Repository name**: `langgraph-data-agent` (or your preferred name)
   - **Description**: "LangGraph-based data analysis agent with MCP integration for BigQuery and Context7"
   - **Visibility**: ✅ Private
   - **Do NOT** initialize with README, .gitignore, or license (we already have these)
3. Click "Create repository"

### Step 5: Add Remote and Push

```bash
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/langgraph-data-agent.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## 🔐 Repository Settings

After creating the repository, configure these settings:

### 1. Branch Protection Rules

Go to: Settings → Branches → Add rule

- Branch name pattern: `main`
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging
- ✅ Require branches to be up to date before merging
- ✅ Include administrators

### 2. Repository Secrets (for CI/CD)

Go to: Settings → Secrets and variables → Actions

Add these secrets if you want CI/CD to run tests:

- `GOOGLE_API_KEY`: Your Gemini API key
- `CONTEXT7_API_KEY`: Your Context7 API key
- `GCP_PROJECT_ID`: Your Google Cloud project ID

### 3. Collaborators

Go to: Settings → Collaborators

Add team members who should have access to the private repository.

## 📊 Repository Features

### Enabled Features

- ✅ Issues
- ✅ Pull Requests
- ✅ GitHub Actions (CI/CD)
- ✅ Projects (optional)
- ✅ Wiki (optional)

### Issue Templates

The repository includes:
- Bug report template
- Feature request template

### GitHub Actions

CI pipeline (`.github/workflows/ci.yml`) runs on:
- Push to `main` or `develop` branches
- Pull requests to `main` or `develop`

Pipeline includes:
- Python linting (flake8)
- Code formatting check (black)
- Unit tests (pytest)
- Code coverage reporting

## 🏷️ Recommended Labels

Create these labels for better issue management:

- `bug` - Something isn't working (red)
- `enhancement` - New feature or request (blue)
- `documentation` - Documentation improvements (green)
- `good first issue` - Good for newcomers (purple)
- `help wanted` - Extra attention needed (yellow)
- `priority: high` - High priority (orange)
- `priority: low` - Low priority (gray)
- `wontfix` - This will not be worked on (white)

## 📝 Post-Setup Checklist

After pushing to GitHub:

- [ ] Repository is set to Private
- [ ] README.md displays correctly
- [ ] Branch protection rules configured
- [ ] Repository secrets added (if using CI/CD)
- [ ] Collaborators invited
- [ ] Issue templates working
- [ ] GitHub Actions CI passing
- [ ] License file present (MIT)
- [ ] .gitignore working (no sensitive files committed)

## 🔍 Verify Setup

Check that these files are in your repository:

```bash
git ls-files | grep -E "(README|LICENSE|.gitignore|requirements.txt|docker-compose.yml)"
```

Should show:
- README.md
- LICENSE
- .gitignore
- requirements.txt
- docker-compose.yml
- And all other project files

## ⚠️ Security Checklist

Before pushing, ensure:

- [ ] No API keys in code
- [ ] No service account credentials
- [ ] `.env` file is gitignored
- [ ] `toolbox` binary is gitignored (if present)
- [ ] No sensitive logs committed
- [ ] `.env.example` contains only placeholders

## 🔗 Repository URLs

After setup, your repository will be available at:

- **Repository**: `https://github.com/YOUR_USERNAME/langgraph-data-agent`
- **Clone URL**: `https://github.com/YOUR_USERNAME/langgraph-data-agent.git`
- **Issues**: `https://github.com/YOUR_USERNAME/langgraph-data-agent/issues`
- **Actions**: `https://github.com/YOUR_USERNAME/langgraph-data-agent/actions`

## 🤝 Inviting Collaborators

To invite collaborators to your private repository:

1. Go to repository Settings → Collaborators
2. Click "Add people"
3. Enter GitHub username or email
4. Select permission level:
   - **Read**: Can view and clone
   - **Write**: Can push to repository
   - **Admin**: Full access
5. Send invitation

## 📦 Cloning the Repository

Team members can clone with:

```bash
git clone https://github.com/YOUR_USERNAME/langgraph-data-agent.git
cd langgraph-data-agent
```

Then follow the setup guide in `QUICKSTART.md`.

## 🎉 Done!

Your private GitHub repository is now set up and ready for collaboration!

Next steps:
1. Share repository URL with team members
2. Set up project board (optional)
3. Create first milestone
4. Start development!
