#!/bin/bash

set -e

echo "🚀 Initializing GitHub Repository for LangGraph Data Analysis Agent"
echo "=================================================================="
echo ""

if [ -d ".git" ]; then
    echo "⚠️  Git repository already exists. Skipping initialization."
else
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git initialized"
fi

echo ""
echo "📝 Creating initial commit..."

git add .

git commit -m "Initial commit: LangGraph Data Analysis Agent with MCP integration

- Multi-agent system with LangGraph orchestration
- MCP integration for BigQuery and Context7
- Weaviate vector store for semantic memory
- Google Gemini + AWS Bedrock LLM support
- Comprehensive documentation and setup guides
- Docker configuration for Weaviate
- CI/CD pipeline with GitHub Actions"

echo "✅ Initial commit created"
echo ""

read -p "Enter your GitHub username: " GITHUB_USERNAME
read -p "Enter repository name (default: langgraph-data-agent): " REPO_NAME
REPO_NAME=${REPO_NAME:-langgraph-data-agent}

echo ""
echo "📡 Creating private GitHub repository..."
echo ""
echo "Please run the following commands manually:"
echo ""
echo "1. Create a private repository on GitHub:"
echo "   gh repo create $GITHUB_USERNAME/$REPO_NAME --private --source=. --remote=origin"
echo ""
echo "   OR visit: https://github.com/new"
echo "   - Repository name: $REPO_NAME"
echo "   - Visibility: Private"
echo "   - Do NOT initialize with README, .gitignore, or license"
echo ""
echo "2. Push to GitHub:"
echo "   git branch -M main"
echo "   git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
echo "   git push -u origin main"
echo ""
echo "=================================================================="
echo ""

read -p "Do you have GitHub CLI (gh) installed? (y/n): " HAS_GH_CLI

if [ "$HAS_GH_CLI" = "y" ] || [ "$HAS_GH_CLI" = "Y" ]; then
    echo ""
    read -p "Create repository now with GitHub CLI? (y/n): " CREATE_NOW
    
    if [ "$CREATE_NOW" = "y" ] || [ "$CREATE_NOW" = "Y" ]; then
        echo ""
        echo "🔧 Creating private repository with GitHub CLI..."
        
        gh repo create "$GITHUB_USERNAME/$REPO_NAME" \
            --private \
            --source=. \
            --remote=origin \
            --description="LangGraph-based data analysis agent with MCP integration for BigQuery and Context7"
        
        echo ""
        echo "📤 Pushing to GitHub..."
        git branch -M main
        git push -u origin main
        
        echo ""
        echo "✅ Repository created and pushed successfully!"
        echo ""
        echo "🔗 Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
        echo ""
        echo "Next steps:"
        echo "1. Add repository secrets for CI/CD (if needed)"
        echo "2. Configure branch protection rules"
        echo "3. Invite collaborators"
    else
        echo ""
        echo "ℹ️  Repository not created. Run the manual commands above when ready."
    fi
else
    echo ""
    echo "ℹ️  Install GitHub CLI for easier setup: https://cli.github.com/"
    echo ""
    echo "📋 Manual setup instructions:"
    echo "1. Go to https://github.com/new"
    echo "2. Create a private repository named: $REPO_NAME"
    echo "3. Run these commands:"
    echo ""
    echo "   git branch -M main"
    echo "   git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo "   git push -u origin main"
fi

echo ""
echo "🎉 Setup complete!"
