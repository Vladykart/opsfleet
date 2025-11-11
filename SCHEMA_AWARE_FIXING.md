# ✅ Schema-Aware SQL Fixing

## Enhancement

Enhanced the SQL auto-fix feature with **complete schema information** so the LLM can fix column name errors correctly.

## Problem

The auto-retry was failing because the LLM didn't know the correct column names:

```
Error: Name product_id not found inside p at [9:58]
```

The SQL was trying to use `products.product_id`, but the correct column is `products.id`.

## Solution

Added complete schema information to the SQL fixing prompt:

```
AVAILABLE TABLES AND COLUMNS:
- `bigquery-public-data.thelook_ecommerce.products` 
  (id, name, category, cost, retail_price, brand, department)
  
- `bigquery-public-data.thelook_ecommerce.orders` 
  (order_id, user_id, status, created_at, num_of_item)
  
- `bigquery-public-data.thelook_ecommerce.order_items` 
  (id, order_id, product_id, user_id, sale_price, created_at)
  
- `bigquery-public-data.thelook_ecommerce.users` 
  (id, first_name, last_name, email, country, state, city, created_at)

COMMON ERRORS AND FIXES:
- "product_id not found in products" → Use "id" instead
- "user_id not found in users" → Use "id" instead
- Invalid JOIN → Check column names match between tables
```

## Key Schema Facts

| Table | Primary Key | Notes |
|-------|-------------|-------|
| **products** | `id` | NOT `product_id` |
| **users** | `id` | NOT `user_id` |
| **orders** | `order_id` | Has `user_id` FK |
| **order_items** | `id` | Has `product_id` and `user_id` FKs |

## Common Fixes

### Fix 1: Wrong Column in Products Table

**Broken**:
```sql
SELECT p.product_id, p.name
FROM `bigquery-public-data.thelook_ecommerce.products` p
```

**Fixed**:
```sql
SELECT p.id, p.name
FROM `bigquery-public-data.thelook_ecommerce.products` p
```

### Fix 2: Wrong JOIN Column

**Broken**:
```sql
SELECT p.name, oi.sale_price
FROM `bigquery-public-data.thelook_ecommerce.products` p
JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi 
  ON p.product_id = oi.product_id
```

**Fixed**:
```sql
SELECT p.name, oi.sale_price
FROM `bigquery-public-data.thelook_ecommerce.products` p
JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi 
  ON p.id = oi.product_id
```

### Fix 3: Users Table

**Broken**:
```sql
SELECT u.user_id, u.email
FROM `bigquery-public-data.thelook_ecommerce.users` u
```

**Fixed**:
```sql
SELECT u.id, u.email
FROM `bigquery-public-data.thelook_ecommerce.users` u
```

## How It Works

1. **SQL fails** with column name error
2. **LLM receives**:
   - Broken SQL
   - Error message
   - Complete schema with correct column names
   - Common error patterns
3. **LLM fixes** by:
   - Checking error message for column name
   - Looking up correct column in schema
   - Replacing wrong column with correct one
4. **Retry** with fixed SQL

## Benefits

✅ **Schema-aware** - Knows all table structures  
✅ **Column mapping** - Understands FK relationships  
✅ **Common patterns** - Recognizes typical errors  
✅ **Higher success rate** - More errors fixed correctly  

## Testing

```bash
python cli_chat.py --verbose

# These should now auto-fix correctly:
You: Show products with their sales
You: Join users with orders
You: Get product revenue
```

## File Modified

- **`src/orchestration/tools.py`**
  - Enhanced `_fix_sql()` with complete schema
  - Added common error patterns
  - Added column name mapping guidance

## Summary

✅ **Complete schema** - All tables and columns documented  
✅ **Error patterns** - Common mistakes identified  
✅ **Smart fixing** - LLM knows correct column names  
✅ **Higher success** - More SQL errors fixed automatically  

**The auto-retry now understands the database schema and fixes column name errors correctly!** 🎉
