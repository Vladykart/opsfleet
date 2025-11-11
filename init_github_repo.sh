#!/usr/bin/env bash

set -euo pipefail
IFS=$'\n\t'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}" >&2; }

cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        log_error "Script failed with exit code $exit_code"
    fi
    exit $exit_code
}

trap cleanup EXIT ERR

echo "🚀 Initializing GitHub Repository for OpsFleet Data Analysis Agent"
echo "=================================================================="
echo ""

if [ -d ".git" ]; then
    log_warning "Git repository already exists. Skipping initialization."
else
    log_info "Initializing Git repository..."
    git init
    log_success "Git initialized"
fi

echo ""
if git diff-index --quiet HEAD -- 2>/dev/null; then
    log_warning "No changes to commit. Repository is up to date."
else
    log_info "Creating initial commit..."
    
    git add .
    
    git commit -m "Initial commit: OpsFleet Professional ReAct Agent

- Professional ReAct agent with genius-level planning
- Multi-phase strategic planning with data sampling
- BigQuery integration with smart SQL generation
- LangSmith tracing and thread support
- Conversation history and caching
- Step-by-step execution with progress tracking
- Comprehensive error handling and validation
- CLI interface with beautiful formatting"
    
    log_success "Initial commit created"
fi
echo ""

read -p "Enter your GitHub username: " GITHUB_USERNAME
if [ -z "$GITHUB_USERNAME" ]; then
    log_error "GitHub username is required"
    exit 1
fi

read -p "Enter repository name (default: opsfleet): " REPO_NAME
REPO_NAME=${REPO_NAME:-opsfleet}

if ! [[ "$REPO_NAME" =~ ^[a-zA-Z0-9_-]+$ ]]; then
    log_error "Invalid repository name. Use only letters, numbers, hyphens, and underscores."
    exit 1
fi

echo ""
log_info "Preparing to create GitHub repository..."
echo ""

if command -v gh &> /dev/null; then
    log_success "GitHub CLI detected"
    echo ""
    read -p "Create repository now with GitHub CLI? (y/n): " CREATE_NOW
    
    if [ "$CREATE_NOW" = "y" ] || [ "$CREATE_NOW" = "Y" ]; then
        echo ""
        log_info "Checking GitHub authentication..."
        
        if ! gh auth status &> /dev/null; then
            log_error "Not authenticated with GitHub CLI. Run: gh auth login"
            exit 1
        fi
        
        log_info "Creating private repository with GitHub CLI..."
        
        if gh repo create "$GITHUB_USERNAME/$REPO_NAME" \
            --private \
            --source=. \
            --remote=origin \
            --description="Professional ReAct agent with genius planning, BigQuery integration, and LangSmith tracing" 2>&1; then
            
            echo ""
            log_info "Pushing to GitHub..."
            git branch -M main
            
            if git push -u origin main; then
                echo ""
                log_success "Repository created and pushed successfully!"
                echo ""
                echo "🔗 Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
                echo ""
                echo "📋 Next steps:"
                echo "   1. Add repository secrets: gh secret set LANGSMITH_API_KEY"
                echo "   2. Configure branch protection: gh repo edit --enable-auto-merge=false"
                echo "   3. Add collaborators: gh repo add-collaborator USERNAME"
                echo "   4. Create first issue: gh issue create"
            else
                log_error "Failed to push to GitHub"
                exit 1
            fi
        else
            log_error "Failed to create repository. It may already exist."
            exit 1
        fi
    else
        echo ""
        log_info "Skipping automatic repository creation"
        echo ""
        echo "📋 Manual commands:"
        echo "   gh repo create $GITHUB_USERNAME/$REPO_NAME --private --source=. --remote=origin"
        echo "   git branch -M main"
        echo "   git push -u origin main"
    fi
else
    log_warning "GitHub CLI not found"
    echo ""
    echo "📥 Install GitHub CLI: https://cli.github.com/"
    echo ""
    echo "📋 Manual setup:"
    echo "   1. Visit: https://github.com/new"
    echo "   2. Repository name: $REPO_NAME"
    echo "   3. Visibility: Private"
    echo "   4. Do NOT initialize with README"
    echo ""
    echo "   Then run:"
    echo "   git branch -M main"
    echo "   git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo "   git push -u origin main"
fi

echo ""
log_success "Setup complete!"
echo ""
log_info "Repository: $GITHUB_USERNAME/$REPO_NAME"
log_info "Branch: main"
log_info "Status: $(git status --short | wc -l | tr -d ' ') uncommitted changes"
