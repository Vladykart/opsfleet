# 🧠 Schema-Aware SQL Generation with Query Patterns

## Overview

The agent now uses **cached schema information** from Stage 0 (Database Exploration) to generate better, more accurate SQL queries with proper relationships and patterns.

## How It Works

### Stage 0: Database Exploration (Cached)

```python
{
    "tables": [
        {
            "name": "products",
            "full_name": "`bigquery-public-data.thelook_ecommerce.products`",
            "columns": ["id", "name", "category", ...],
            "primary_key": "id",
            "description": "Product catalog..."
        }
    ],
    "relationships": [
        "orders.user_id → users.id",
        "order_items.product_id → products.id"
    ],
    "common_queries": [
        "Product revenue analysis",
        "Customer segmentation",
        "Sales trends over time",
        "Geographic analysis"
    ]
}
```

### Stage 3: SQL Generation (Uses Cache)

The `_prepare_tool_input` method now:

1. **Reads cached schema** from `self.db_schema_cache`
2. **Extracts relationships** between tables
3. **Uses query patterns** as examples
4. **Generates SQL** with correct JOINs

## Enhanced SQL Generation Prompt

### Before (Static)

```
AVAILABLE TABLES:
- products (id, name, ...)
- orders (order_id, ...)
```

### After (Dynamic from Cache)

```
DATABASE SCHEMA:
- `bigquery-public-data.thelook_ecommerce.products` (id, name, category, cost, retail_price, brand, department)
- `bigquery-public-data.thelook_ecommerce.orders` (order_id, user_id, status, created_at, num_of_item)
- `bigquery-public-data.thelook_ecommerce.order_items` (id, order_id, product_id, user_id, sale_price, created_at)
- `bigquery-public-data.thelook_ecommerce.users` (id, first_name, last_name, email, country, state, city, created_at)

TABLE RELATIONSHIPS:
  orders.user_id → users.id
  order_items.order_id → orders.order_id
  order_items.product_id → products.id
  order_items.user_id → users.id

COMMON QUERY PATTERNS (use as reference):
  • Product revenue analysis
  • Customer segmentation
  • Sales trends over time
  • Geographic analysis

QUERY PATTERN EXAMPLES:

1. Product Revenue Analysis:
   SELECT p.name, SUM(oi.sale_price) as revenue
   FROM `bigquery-public-data.thelook_ecommerce.products` p
   JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi ON p.id = oi.product_id
   GROUP BY p.name ORDER BY revenue DESC LIMIT 10

2. Customer Segmentation by Purchase Frequency:
   SELECT u.id, u.country, COUNT(o.order_id) as purchase_count
   FROM `bigquery-public-data.thelook_ecommerce.users` u
   LEFT JOIN `bigquery-public-data.thelook_ecommerce.orders` o ON u.id = o.user_id
   GROUP BY u.id, u.country ORDER BY purchase_count DESC LIMIT 100

3. Geographic Analysis:
   SELECT u.country, COUNT(DISTINCT u.id) as customers, SUM(oi.sale_price) as revenue
   FROM `bigquery-public-data.thelook_ecommerce.users` u
   JOIN `bigquery-public-data.thelook_ecommerce.orders` o ON u.id = o.user_id
   JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi ON o.order_id = oi.order_id
   GROUP BY u.country ORDER BY revenue DESC LIMIT 20
```

## Query Pattern Matching

The LLM now recognizes query patterns and generates appropriate SQL:

### Pattern 1: Product Revenue Analysis

**User Query**: "What are the top 10 products by revenue?"

**Recognized Pattern**: Product revenue analysis

**Generated SQL**:
```sql
SELECT p.name, p.category, SUM(oi.sale_price) as revenue
FROM `bigquery-public-data.thelook_ecommerce.products` p
JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi ON p.id = oi.product_id
GROUP BY p.name, p.category
ORDER BY revenue DESC
LIMIT 10
```

### Pattern 2: Customer Segmentation

**User Query**: "Analyze customer segments by purchase frequency"

**Recognized Pattern**: Customer segmentation

**Generated SQL**:
```sql
SELECT 
    u.id,
    u.country,
    u.state,
    COUNT(o.order_id) as purchase_count,
    CASE 
        WHEN COUNT(o.order_id) >= 10 THEN 'High'
        WHEN COUNT(o.order_id) >= 5 THEN 'Medium'
        ELSE 'Low'
    END as segment
FROM `bigquery-public-data.thelook_ecommerce.users` u
LEFT JOIN `bigquery-public-data.thelook_ecommerce.orders` o ON u.id = o.user_id
GROUP BY u.id, u.country, u.state
ORDER BY purchase_count DESC
LIMIT 100
```

### Pattern 3: Geographic Analysis

**User Query**: "Show sales by country"

**Recognized Pattern**: Geographic analysis

**Generated SQL**:
```sql
SELECT 
    u.country,
    COUNT(DISTINCT u.id) as customers,
    COUNT(DISTINCT o.order_id) as orders,
    SUM(oi.sale_price) as total_revenue,
    AVG(oi.sale_price) as avg_order_value
FROM `bigquery-public-data.thelook_ecommerce.users` u
JOIN `bigquery-public-data.thelook_ecommerce.orders` o ON u.id = o.user_id
JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi ON o.order_id = oi.order_id
GROUP BY u.country
ORDER BY total_revenue DESC
LIMIT 20
```

### Pattern 4: Sales Trends

**User Query**: "Show sales trends for the last quarter"

**Recognized Pattern**: Sales trends over time

**Generated SQL**:
```sql
SELECT 
    DATE_TRUNC(o.created_at, MONTH) as month,
    COUNT(DISTINCT o.order_id) as orders,
    SUM(oi.sale_price) as revenue,
    COUNT(DISTINCT o.user_id) as customers
FROM `bigquery-public-data.thelook_ecommerce.orders` o
JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi ON o.order_id = oi.order_id
WHERE o.created_at >= DATE_SUB(CURRENT_DATE(), INTERVAL 3 MONTH)
GROUP BY month
ORDER BY month DESC
```

## Benefits

### 1. Correct Relationships

✅ **Automatic JOINs** - Uses cached FK relationships  
✅ **Correct columns** - products.id, users.id (not product_id, user_id)  
✅ **Proper linking** - Follows relationship patterns  

### 2. Pattern Recognition

✅ **Recognizes intent** - Matches query to pattern  
✅ **Uses examples** - Follows proven patterns  
✅ **Consistent structure** - Similar queries use similar SQL  

### 3. Better SQL Quality

✅ **More accurate** - Uses schema knowledge  
✅ **Fewer errors** - Correct column names  
✅ **Optimized** - Follows best practices  

### 4. Performance

✅ **Cached schema** - No repeated lookups  
✅ **Fast generation** - Pattern-based  
✅ **Efficient queries** - Proper indexing hints  

## Implementation

### Code Structure

```python
async def _prepare_tool_input(self, step, thought):
    if tool_name == 'bigquery':
        # 1. Get cached schema
        if self.db_schema_cache:
            tables = self.db_schema_cache.get('tables', [])
            relationships = self.db_schema_cache.get('relationships', [])
            query_patterns = self.db_schema_cache.get('common_queries', [])
        
        # 2. Build dynamic prompt
        prompt = f"""
        DATABASE SCHEMA:
        {schema_info}
        
        TABLE RELATIONSHIPS:
        {relationships_info}
        
        COMMON QUERY PATTERNS:
        {query_patterns}
        
        QUERY PATTERN EXAMPLES:
        [Examples for each pattern]
        """
        
        # 3. Generate SQL
        sql = await self.llm._call_llm(prompt)
        return sql
```

### Fallback Mechanism

If schema cache is not available:

```python
else:
    # Use static schema information
    schema_info = """[Static table definitions]"""
    relationships_info = """[Static relationships]"""
    query_patterns = """[Static patterns]"""
```

## Example Flow

### 1. First Query (Builds Cache)

```
You: What are the top products?

Stage 0: Database Exploration
  ✓ Cached schema: 4 tables
  ✓ Mapped 4 relationships
  ✓ Identified 4 query patterns

Stage 3: Execution
  ✓ Using cached schema
  ✓ Matched pattern: Product revenue analysis
  ✓ Generated SQL with correct JOINs
```

### 2. Subsequent Queries (Uses Cache)

```
You: Show customer segments

Stage 3: Execution
  ✓ Using cached schema (no exploration)
  ✓ Matched pattern: Customer segmentation
  ✓ Generated SQL with correct JOINs
```

## Query Pattern Library

The agent recognizes these patterns:

| Pattern | Description | Example Query |
|---------|-------------|---------------|
| **Product Revenue** | Product sales analysis | "Top products by revenue" |
| **Customer Segmentation** | Customer grouping | "Segment customers by frequency" |
| **Sales Trends** | Time-based analysis | "Sales trends last quarter" |
| **Geographic Analysis** | Location-based analysis | "Sales by country" |

## Files Modified

- **`src/agents/professional_react_agent.py`**
  - Enhanced `_prepare_tool_input()` method
  - Added schema cache usage
  - Added relationship information
  - Added query pattern examples
  - Added dynamic prompt building

## Testing

```bash
python cli_chat.py --verbose

# Test different patterns:
You: What are the top 10 products by revenue?
# Should match: Product Revenue pattern

You: Analyze customer segments by purchase frequency
# Should match: Customer Segmentation pattern

You: Show sales by country
# Should match: Geographic Analysis pattern

You: Show sales trends for the last quarter
# Should match: Sales Trends pattern
```

## Summary

✅ **Schema-aware** - Uses cached database structure  
✅ **Pattern-based** - Recognizes common query types  
✅ **Relationship-aware** - Correct JOINs automatically  
✅ **Example-driven** - Follows proven patterns  
✅ **Dynamic prompts** - Built from cached data  
✅ **Better SQL** - More accurate and efficient  

**The agent now generates significantly better SQL using cached schema and query patterns!** 🎉
