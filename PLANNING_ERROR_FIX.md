# 🔧 Planning Stage Error Fix

## Problem

**Error**: `'steps'`
```
⠋ Understanding: Analyzing intent...
✓ Understanding: data analysis
⠋ Planning: Creating plan...
ERROR:ProfessionalReActAgent:Processing failed: 'steps'
```

## Root Cause

The `_extract_json` method was failing to properly extract JSON from LLM response, returning a dictionary without the required `'steps'` key. This caused a KeyError when trying to access `plan['steps']`.

## Solution

Added robust validation and fallback logic:

### Before
```python
plan = self._extract_json(response, default_plan)
self.logger.info(f"Plan created: {len(plan['steps'])} steps")
return plan
```

### After
```python
plan = self._extract_json(response, default_plan)

# Ensure plan has steps key
if 'steps' not in plan or not isinstance(plan['steps'], list) or len(plan['steps']) == 0:
    self.logger.warning("Invalid plan structure, using default")
    plan = default_plan

self.logger.info(f"Plan created: {len(plan['steps'])} steps")
return plan
```

## Changes Made

✅ **Validation Check**: Verifies `'steps'` key exists  
✅ **Type Check**: Ensures `steps` is a list  
✅ **Length Check**: Confirms list is not empty  
✅ **Fallback Logic**: Uses default plan if invalid  
✅ **Warning Log**: Logs when fallback is used  

## Default Plan

If LLM returns invalid JSON, uses this safe default:
```python
{
    "steps": [
        {
            "id": 1,
            "action": "bigquery",
            "description": "Execute query",
            "expected_output": "data results",
            "critical": True
        }
    ],
    "estimated_time": "1-2 minutes",
    "risk_level": "low"
}
```

## Benefits

✅ **No More Crashes**: Agent continues even if LLM returns bad JSON  
✅ **Graceful Degradation**: Falls back to simple single-step plan  
✅ **Better Logging**: Warns when using fallback  
✅ **Robust**: Handles edge cases (empty lists, wrong types, etc.)  

## Testing

```bash
cd /Users/vlad/PycharmProjects/opsfleet
source venv/bin/activate
python cli_chat.py --verbose
```

**Try**:
```
You: What are the top 10 products by revenue?
```

Should now work without errors!

## Error Handling Flow

```
LLM Response
    ↓
_extract_json()
    ↓
Validation Check
    ├─ Valid? → Use plan
    └─ Invalid? → Use default plan
         ↓
    Log warning
         ↓
    Continue execution
```

## Summary

✅ **Fixed**: Planning stage no longer crashes on invalid JSON  
✅ **Robust**: Multiple validation checks  
✅ **Safe**: Always has valid default fallback  
✅ **Transparent**: Logs when using fallback  

**The agent is now more robust and handles LLM errors gracefully!** 🎉
