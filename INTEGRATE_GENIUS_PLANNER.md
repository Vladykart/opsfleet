# 🔧 Integrate Genius Planner - Quick Guide

## Integration Steps

### Step 1: Import the Genius Planner

In `/Users/vlad/PycharmProjects/opsfleet/src/agents/professional_react_agent.py`:

```python
# Add at top of file
from src.agents.genius_planner import GeniusPlanner
```

### Step 2: Initialize in __init__

In `ProfessionalReActAgent.__init__` method, add:

```python
# After initializing tools and llm
self.genius_planner = GeniusPlanner(
    llm=self.llm,
    tools=self.tools,
    logger=self.logger
)
```

### Step 3: Replace _stage_2_planning

Replace the entire `_stage_2_planning` method with:

```python
@traceable(name="stage_2_planning")
async def _stage_2_planning(
    self,
    query: str,
    understanding: Dict[str, Any]
) -> Dict[str, Any]:
    """Stage 2: Strategic planning using Genius Planner"""
    
    plan = await self.genius_planner.create_genius_plan(
        query=query,
        understanding=understanding,
        progress_callback=self.progress_callback
    )
    
    self.logger.info(f"Plan created: {len(plan['steps'])} steps")
    return plan
```

## That's It!

The Genius Planner is now integrated. Your agent will use 4-phase strategic planning automatically.

## What You'll See

### Before
```
⠋ Planning: Creating plan...
✓ Planning: 1 step(s)
```

### After
```
⠋ Planning: Strategic analysis...
⠋ Planning: Decomposing problem...
⠋ Planning: Optimizing execution...
⠋ Planning: Validating plan...
✓ Planning: 3 step(s) - confidence: 0.95
```

## Test It

```bash
python cli_chat.py --verbose
```

Try complex queries:
```
You: Compare Q1 vs Q2 sales by category
You: Show top 10 products by revenue with growth trends
You: Analyze customer segments by purchase frequency
```

You'll see the genius planner in action with:
- Strategic thinking
- Optimal decomposition
- Performance optimization
- Risk assessment

## Benefits

✅ **Smarter plans** - Strategic thinking  
✅ **Better performance** - Optimized execution  
✅ **Higher confidence** - Risk assessment  
✅ **More reliable** - Validated plans  

**Your agent is now genius-level!** 🧠🚀
