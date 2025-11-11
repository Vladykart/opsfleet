# 💡 Next Steps Suggestions Feature

The agent now intelligently suggests 3 contextual next steps after each successful query.

## How It Works

After the agent responds to your query, it analyzes the question type and suggests relevant follow-up actions.

## Example Flow

### 1. Count Query
**User:** "How many users are in the database?"

**Agent Response:** "There are 100,000 users in the database."

**Next Steps Suggested:**
```
┌─ 💡 What would you like to do next? ─────────────────────┐
│ [1]     Show me the top 10 by a specific metric          │
│ [2]     Break down the data by category or region        │
│ [3]     Compare with historical data or trends           │
└───────────────────────────────────────────────────────────┘
💬 Type your choice or ask a new question
```

### 2. Top/Best Query
**User:** "What are the top 5 products by price?"

**Agent Response:** [Shows top 5 products]

**Next Steps Suggested:**
```
┌─ 💡 What would you like to do next? ─────────────────────┐
│ [1]     Show me the bottom/worst performers               │
│ [2]     Analyze the trend over time                       │
│ [3]     Get detailed information about the top item       │
└───────────────────────────────────────────────────────────┘
```

### 3. Recent Data Query
**User:** "Show me recent orders"

**Agent Response:** [Shows recent orders]

**Next Steps Suggested:**
```
┌─ 💡 What would you like to do next? ─────────────────────┐
│ [1]     Compare with older data                           │
│ [2]     Show trends over a longer period                  │
│ [3]     Filter by specific criteria                       │
└───────────────────────────────────────────────────────────┘
```

## Query Types & Suggestions

### Count Queries
**Triggers:** "how many", "count"

**Suggestions:**
1. Show me the top 10 by a specific metric
2. Break down the data by category or region
3. Compare with historical data or trends

### Top/Best Queries
**Triggers:** "top", "best", "highest"

**Suggestions:**
1. Show me the bottom/worst performers
2. Analyze the trend over time
3. Get detailed information about the top item

### Recent/Latest Queries
**Triggers:** "recent", "latest"

**Suggestions:**
1. Compare with older data
2. Show trends over a longer period
3. Filter by specific criteria

### Average Queries
**Triggers:** "average", "mean"

**Suggestions:**
1. Show the distribution or breakdown
2. Compare with median or other metrics
3. Identify outliers or anomalies

### Schema Queries
**Triggers:** "schema", "table"

**Suggestions:**
1. Query data from this table
2. See relationships with other tables
3. Get sample data from the table

### General Queries
**Default suggestions:**
1. Dive deeper into specific details
2. Compare with other metrics or categories
3. Save this conversation for later

## Usage

### Option 1: Type the Suggestion
Simply type what you want:
```
You › Show me the top 10 by price
```

### Option 2: Reference by Number
You can reference suggestions by number:
```
You › 1
```
(Feature coming soon)

### Option 3: Ask New Question
Ignore suggestions and ask anything:
```
You › What about product categories?
```

## Benefits

### 1. **Guided Exploration**
- Helps users discover what questions to ask next
- Reduces "what should I ask?" moments
- Encourages deeper data exploration

### 2. **Context-Aware**
- Suggestions match the query type
- Relevant to the data just shown
- Logical progression of analysis

### 3. **Learning Tool**
- Shows users what's possible
- Teaches data analysis patterns
- Builds query sophistication

### 4. **Faster Workflow**
- Quick access to common follow-ups
- No need to think of next question
- Smooth conversation flow

## Implementation Details

### Context Detection
```python
def _generate_suggestions(self, query: str, response: str) -> List[str]:
    query_lower = query.lower()
    
    if "how many" in query_lower or "count" in query_lower:
        return [...]  # Count-specific suggestions
    elif "top" in query_lower or "best" in query_lower:
        return [...]  # Top-specific suggestions
    # ... more patterns
```

### Display Format
- Beautiful table with rounded borders
- Numbered options [1], [2], [3]
- Cyan color scheme
- Clear call-to-action

### When Suggestions Appear
- ✅ After successful queries
- ❌ Not shown after errors
- ❌ Not shown for commands (/help, /history, etc.)

## Customization

### Adding New Patterns
To add new suggestion patterns, edit `_generate_suggestions()`:

```python
elif "your_pattern" in query_lower:
    return [
        "First suggestion",
        "Second suggestion",
        "Third suggestion"
    ]
```

### Disabling Suggestions
To disable, comment out in `process_query()`:

```python
# if success:
#     self.suggest_next_steps(query, response)
```

## Future Enhancements

- [ ] Number-based selection (type "1" to select option 1)
- [ ] AI-generated suggestions based on response content
- [ ] User preference learning
- [ ] Suggestion history
- [ ] Custom suggestion templates
- [ ] Multi-language support

## Examples in Action

### Data Exploration Flow
```
1. "How many users?" 
   → Suggests: breakdown by region
   
2. "Break down users by country"
   → Suggests: top countries, trends, comparisons
   
3. "Show top 10 countries"
   → Suggests: bottom countries, trends, details
   
4. "Analyze trend over time"
   → Suggests: predictions, patterns, export data
```

### Analysis Flow
```
1. "What's the average order value?"
   → Suggests: distribution, median, outliers
   
2. "Show the distribution"
   → Suggests: by category, by time, by region
   
3. "Break down by category"
   → Suggests: top categories, trends, comparisons
```

## Tips

1. **Follow the Flow** - Suggestions guide natural analysis progression
2. **Mix and Match** - Use suggestions + custom questions
3. **Explore Freely** - Suggestions are optional, not mandatory
4. **Learn Patterns** - Notice what questions lead where
5. **Save Insights** - Use `/save` when you find something interesting

## Technical Notes

- Suggestions are generated client-side (instant)
- No additional API calls required
- Pattern matching is case-insensitive
- Fallback suggestions always available
- Works with all query types

## Feedback

The suggestion system learns from common data analysis patterns. If you have ideas for better suggestions, they can be easily added to the pattern matching logic.
