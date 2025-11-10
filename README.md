# LangGraph Data Analysis Agent

E-commerce data analysis agent powered by LangGraph, MCP, and Google Gemini.

## Overview

This project implements an intelligent data analysis agent that uses:
- **LangGraph** for workflow orchestration
- **MCP (Model Context Protocol)** for tool integration
- **BigQuery** for data access via MCP server
- **Context7** for up-to-date documentation
- **Google Gemini** as primary LLM (AWS Bedrock as fallback)
- **Weaviate** for vector memory storage

## Features

- 🤖 Multi-agent architecture with specialized roles
- 🔌 MCP-based tool integration (no direct database dependencies)
- 🧠 Semantic memory with Weaviate
- 📊 BigQuery e-commerce data analysis (direct integration)
- 🎯 Context-aware query planning
- ✅ Automated data validation
- 📝 Natural language insights generation
- 🔍 Customer segmentation and behavior analysis
- 📈 Product performance and sales trend analysis
- 🌍 Geographic sales pattern analysis
- 🤖 LLM-powered SQL generation with Gemini

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- Google Cloud account with BigQuery access
- Context7 API key
- Google Gemini API key

### Installation

1. Clone and navigate to project:
```bash
cd /Users/vlad/PycharmProjects/opsfleet
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Start Weaviate:
```bash
docker-compose up -d weaviate
```

5. Run the agent:
```bash
python build_multi_agent_system.py
```

## Project Structure

```
opsfleet/
├── config/              # Configuration files
├── src/                 # Source code
│   ├── agents/         # Agent implementations
│   ├── orchestration/  # LangGraph workflow
│   ├── memory/         # Memory systems
│   ├── prompts/        # Prompt templates
│   └── mcp_client.py   # MCP client wrapper
├── models/             # Data models
├── utils/              # Utilities
├── tests/              # Test suite
└── docs/               # Documentation
```

## Documentation

- [BigQuery Agent Quick Start](BIGQUERY_QUICKSTART.md) - Get started in 5 minutes
- [BigQuery Agent Guide](docs/BIGQUERY_AGENT_GUIDE.md) - Comprehensive documentation
- [Setup Guide](docs/guides/setup-guide.md)
- [Architecture](docs/architecture/component-breakdown.md)
- [API Reference](docs/api/)

## License

MIT
