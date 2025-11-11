# ✅ Enhanced CLI - Inspired by rich-chat

## What Was Enhanced

Based on the excellent [rich-chat](https://github.com/qnixsynapse/rich-chat) project, I've enhanced our CLI with professional features:

### New Features ✅

1. **Command-Line Arguments** - Like rich-chat
2. **Enhanced Welcome Screen** - Better layout and design
3. **Customizable Colors** - Frame color options
4. **Version Information** - --version flag
5. **Better Error Handling** - Graceful error messages

## CLI Arguments

```bash
python cli_chat.py [options]
```

### Available Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--temperature` | float | 0.3 | Controls randomness (0.0-1.0) |
| `--model` | string | llama3.2 | LLM model to use |
| `--frame-color` | string | cyan | Panel frame color |
| `--max-tokens` | int | 2048 | Maximum response tokens |
| `--memory-size` | int | 50 | Conversation history size |
| `--no-tracing` | flag | false | Disable LangSmith tracing |
| `--version` | flag | - | Show version and exit |
| `--help` | flag | - | Show help message |

### Examples

```bash
# Default settings
python cli_chat.py

# Custom temperature
python cli_chat.py --temperature 0.7

# Green frames with larger memory
python cli_chat.py --frame-color green --memory-size 100

# Disable tracing
python cli_chat.py --no-tracing

# Show version
python cli_chat.py --version

# Show help
python cli_chat.py --help
```

## Enhanced Welcome Screen

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

        🚀 BigQuery Data Analysis Agent

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

╭─ Features ─────────────────────────────────────────────╮
│                                                        │
│  🧠  Multi-stage ReAct reasoning with long-term memory │
│  📊  BigQuery integration for powerful data analysis   │
│  🔍  Intelligent planning and execution                │
│  📈  Automated insights generation                     │
│  💾  Conversation memory for context-aware responses   │
│  🎨  Beautiful interface with rich formatting          │
│                                                        │
╰────────────────────────────────────────────────────────╯

╭─ Commands ─────────────────────────────────────────────╮
│                                                        │
│  help         Show help message                        │
│  history      View conversation history                │
│  stats        Session statistics                       │
│  clear        Clear the screen                         │
│  exit/quit    Exit application                         │
│                                                        │
╰────────────────────────────────────────────────────────╯

    Powered by Ollama + Gemini ensemble with LangSmith tracing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## Color Options

Choose from 7 frame colors:

- **red** - Bold and attention-grabbing
- **green** - Fresh and positive
- **yellow** - Warm and friendly
- **blue** - Professional and calm
- **magenta** - Creative and vibrant
- **cyan** - Modern and tech (default)
- **white** - Clean and minimal

```bash
# Try different colors
python cli_chat.py --frame-color red
python cli_chat.py --frame-color green
python cli_chat.py --frame-color magenta
```

## Comparison with rich-chat

| Feature | rich-chat | Our CLI |
|---------|-----------|---------|
| **CLI Arguments** | ✅ | ✅ |
| **Color Customization** | ✅ | ✅ |
| **Rich Formatting** | ✅ | ✅ |
| **Multi-stage Processing** | ❌ | ✅ |
| **Long-term Memory** | ❌ | ✅ |
| **BigQuery Integration** | ❌ | ✅ |
| **LangSmith Tracing** | ❌ | ✅ |
| **ReAct Pattern** | ❌ | ✅ |
| **Conversation History** | ❌ | ✅ |

## Advanced Usage

### Custom Configuration

```bash
# High creativity, large memory
python cli_chat.py \
  --temperature 0.8 \
  --memory-size 100 \
  --max-tokens 4096 \
  --frame-color magenta

# Production mode (low temperature, tracing)
python cli_chat.py \
  --temperature 0.1 \
  --max-tokens 2048

# Development mode (no tracing)
python cli_chat.py \
  --no-tracing \
  --frame-color yellow
```

### Environment Variables

You can also set defaults via environment:

```bash
export CLI_TEMPERATURE=0.5
export CLI_FRAME_COLOR=green
export CLI_MEMORY_SIZE=75

python cli_chat.py
```

## Help Output

```bash
$ python cli_chat.py --help

usage: cli_chat.py [-h] [--temperature TEMPERATURE] [--model MODEL]
                   [--frame-color {red,green,yellow,blue,magenta,cyan,white}]
                   [--max-tokens MAX_TOKENS] [--memory-size MEMORY_SIZE]
                   [--no-tracing] [--version]

BigQuery Data Analysis Agent - Professional CLI Chat Interface

options:
  -h, --help            show this help message and exit
  --temperature TEMPERATURE
                        Controls randomness of text generation (default: 0.3)
  --model MODEL         LLM model to use (default: llama3.2)
  --frame-color {red,green,yellow,blue,magenta,cyan,white}
                        Frame color for panels (default: cyan)
  --max-tokens MAX_TOKENS
                        Maximum tokens for LLM response (default: 2048)
  --memory-size MEMORY_SIZE
                        Maximum conversation history size (default: 50)
  --no-tracing          Disable LangSmith tracing
  --version             show program's version number and exit

Examples:
  python cli_chat.py
  python cli_chat.py --temperature 0.7
  python cli_chat.py --model llama3.2 --frame-color green

For more information, visit: https://github.com/your-repo
```

## Version Output

```bash
$ python cli_chat.py --version
BigQuery Data Analysis Agent v1.0.0
```

## What Makes Our CLI Better

### 1. Professional Multi-Stage Processing

Unlike simple chat interfaces, our CLI uses a 5-stage pipeline:
- Understanding → Planning → Execution → Validation → Synthesis

### 2. Long-Term Memory

Remembers up to 50 conversations with automatic consolidation.

### 3. BigQuery Integration

Direct integration with BigQuery for real data analysis.

### 4. ReAct Pattern

Think-Act-Observe reasoning for better results.

### 5. Full Observability

LangSmith tracing for debugging and optimization.

## Quick Start

```bash
# Install
pip install rich

# Run with defaults
python cli_chat.py

# Run with custom settings
python cli_chat.py --temperature 0.7 --frame-color green
```

## Tips

### Best Temperature Settings

- **0.1-0.3**: Precise, factual responses (recommended for data analysis)
- **0.4-0.6**: Balanced creativity and accuracy
- **0.7-0.9**: Creative, varied responses

### Frame Color Recommendations

- **cyan**: Default, professional (data analysis)
- **green**: Success, positive feedback
- **blue**: Calm, trustworthy (reports)
- **yellow**: Warnings, important info
- **magenta**: Creative tasks
- **red**: Errors, critical info

### Memory Size Guidelines

- **20-30**: Short sessions, limited context
- **50**: Default, good balance (recommended)
- **75-100**: Long sessions, deep context
- **100+**: Research, extensive analysis

## Summary

✅ **Enhanced CLI Features**
- Command-line arguments
- Customizable colors
- Version information
- Better error handling

✅ **Inspired by rich-chat**
- Professional design
- Rich formatting
- User-friendly interface

✅ **Beyond rich-chat**
- Multi-stage processing
- Long-term memory
- BigQuery integration
- ReAct reasoning
- LangSmith tracing

**Experience a professional CLI that's both beautiful and powerful!** 🚀

---

**Inspired by**: [rich-chat](https://github.com/qnixsynapse/rich-chat)  
**Enhanced with**: Multi-stage ReAct, Long-term memory, BigQuery integration  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
