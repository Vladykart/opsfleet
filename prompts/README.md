# Prompts Directory

This directory contains all system prompts used by the OpsFleet Agent.

## Files

### system_prompt.txt
Main system prompt for the BigQuery agent. Defines:
- Agent role and expertise
- Dataset information
- Schema structure
- SQL generation rules
- Task instructions

## Usage

The prompt is loaded dynamically by `agent.py`:

```python
from agent import load_prompt

prompt = load_prompt("How many users are there?")
```

## Customization

To modify the agent's behavior:

1. Edit `system_prompt.txt`
2. The changes will be automatically picked up on next query
3. No code changes needed

## Template Variables

- `{query}` - User's question (required)

## Best Practices

1. **Keep prompts focused** - One clear role per prompt
2. **Include examples** - Show expected SQL patterns
3. **Define constraints** - Specify what NOT to do
4. **Version control** - Track prompt changes in git
5. **Test thoroughly** - Validate with various queries

## Future Prompts

Additional prompts can be added for:
- Different data sources
- Specialized analysis types
- Multi-language support
- Custom personas
