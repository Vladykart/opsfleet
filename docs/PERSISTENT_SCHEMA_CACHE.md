# 💾 Persistent Schema Cache

## Problem

**Before**: Schema explored on every query
```
Query #1: ⠋ Db_Exploration: Exploring schema...
Query #2: ⠋ Db_Exploration: Exploring schema...  ❌ Redundant
Query #3: ⠋ Db_Exploration: Exploring schema...  ❌ Redundant
```

**Issue**: Wasted time exploring the same database repeatedly

## Solution

**After**: Schema cached in memory, explored only once
```
Query #1: ⠋ Db_Exploration: Exploring schema...
          ✓ Db_Exploration: Cached 4 tables

Query #2: ✓ Db_Exploration: Using cached schema (4 tables)  ✅ Instant
Query #3: ✓ Db_Exploration: Using cached schema (4 tables)  ✅ Instant
```

## Implementation

### Class-Level Cache

**Added shared cache**:
```python
class ProfessionalReActAgent:
    # Class-level schema cache (shared across all instances)
    _shared_schema_cache = None
    
    def __init__(self, ...):
        # Use class-level cache if available
        self.db_schema_cache = ProfessionalReActAgent._shared_schema_cache
        
        if self.db_schema_cache:
            self.logger.info(f"Using cached schema with {len(self.db_schema_cache.get('tables', []))} tables")
```

### Cache Persistence

**Save to class-level**:
```python
async def _stage_0_db_exploration(self):
    # ... explore database ...
    
    # Save to both instance and class-level cache
    self.db_schema_cache = schema_info
    ProfessionalReActAgent._shared_schema_cache = schema_info
    self.logger.info(f"Schema cached: {len(schema_info['tables'])} tables (persisted)")
```

### Smart Skip

**Skip if cached**:
```python
if self.enable_db_exploration and not self.db_schema_cache:
    # Explore database
    stage_0 = await self._stage_0_db_exploration()
elif self.db_schema_cache and self.progress_callback:
    # Use cached schema
    self.progress_callback("db_exploration", "complete", 
                          f"Using cached schema ({len(self.db_schema_cache['tables'])} tables)")
```

## Cached Schema Structure

```python
{
    "tables": [
        {
            "name": "products",
            "full_name": "`bigquery-public-data.thelook_ecommerce.products`",
            "columns": ["id", "name", "category", "cost", "retail_price", "brand", "department"],
            "primary_key": "id",
            "description": "Product catalog with pricing and categorization"
        },
        {
            "name": "orders",
            "full_name": "`bigquery-public-data.thelook_ecommerce.orders`",
            "columns": ["order_id", "user_id", "status", "created_at", "num_of_item"],
            "primary_key": "order_id",
            "foreign_keys": [{"column": "user_id", "references": "users.id"}],
            "description": "Customer orders with status and timestamps"
        },
        # ... more tables
    ],
    "relationships": [
        "orders.user_id → users.id",
        "order_items.order_id → orders.order_id",
        "order_items.product_id → products.id",
        "order_items.user_id → users.id"
    ],
    "common_queries": [
        "Product revenue analysis",
        "Customer segmentation",
        "Sales trends over time",
        "Geographic analysis"
    ]
}
```

## Benefits

### Performance
⚡ **Instant access** after first query  
🚀 **No delay** on subsequent queries  
💾 **Memory efficient** (single cache)  

### User Experience
✅ **Faster responses** (no exploration delay)  
📊 **Consistent behavior** across queries  
🔄 **Persists** for entire session  

### Development
🐛 **Easier debugging** (cache state visible)  
📝 **Better logging** (shows cache usage)  
🎯 **Predictable** behavior  

## Behavior

### First Query
```
⠋ Db_Exploration: Exploring schema...
  - Fetches table information
  - Identifies relationships
  - Caches common query patterns
✓ Db_Exploration: Cached 4 tables (persisted)
```

**Time**: ~0.01 seconds (hardcoded schema)

### Subsequent Queries
```
✓ Db_Exploration: Using cached schema (4 tables)
```

**Time**: Instant (no exploration)

## Cache Lifetime

**Persists**:
- ✅ Across multiple queries in same session
- ✅ Across multiple agent instances
- ✅ Until application restart

**Resets**:
- ❌ On application restart
- ❌ On process termination

## Example Session

```bash
$ python cli_chat.py --verbose

# Query 1
You: What are the top 10 products by revenue?
⠋ Db_Exploration: Exploring schema...
✓ Db_Exploration: Cached 4 tables (persisted)
⠋ Understanding: Analyzing intent...
...

# Query 2
You: Show sales by country
✓ Db_Exploration: Using cached schema (4 tables)  ⚡ Instant!
⠋ Understanding: Analyzing intent...
...

# Query 3
You: Top products per season
✓ Db_Exploration: Using cached schema (4 tables)  ⚡ Instant!
⠋ Understanding: Analyzing intent...
...
```

## Logging

### First Query (Cache Miss)
```
INFO:ProfessionalReActAgent:Exploring database schema...
INFO:ProfessionalReActAgent:Schema cached: 4 tables (persisted)
```

### Subsequent Queries (Cache Hit)
```
INFO:ProfessionalReActAgent:Using cached schema with 4 tables
```

## Testing

```bash
cd /Users/vlad/PycharmProjects/opsfleet
source venv/bin/activate
python cli_chat.py --verbose
```

**Test**:
```
You: What are the top 10 products by revenue?
# Wait for response

You: Show sales by country
# Should show "Using cached schema" instantly

You: Top products per season
# Should show "Using cached schema" instantly
```

## Advanced: Manual Cache Clear

If you need to refresh the cache:

```python
# In Python REPL or code
from src.agents.professional_react_agent import ProfessionalReActAgent

# Clear cache
ProfessionalReActAgent._shared_schema_cache = None

# Next query will re-explore database
```

## Summary

### Before
❌ Schema explored on every query  
❌ Redundant database calls  
❌ Slower response times  

### After
✅ Schema explored once  
✅ Cached in memory  
✅ Instant access on subsequent queries  
✅ Persists across entire session  

**Performance**:
- 1st query: 0.01s exploration
- 2nd+ queries: Instant (0s)

**The agent now efficiently caches database schema in memory!** 💾🎉
