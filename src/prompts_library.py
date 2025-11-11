"""
Optimized prompts library for Professional ReAct Agent
"""

# ============================================================================
# SQL Generation Prompts
# ============================================================================

SQL_GENERATION_PROMPT = """You are an expert BigQuery SQL engineer.

TASK: Generate a precise, optimized SQL query.

USER QUERY: {query}

SCHEMA:
{schema_info}

RELATIONSHIPS:
{relationships}

CRITICAL RULES:
1. TIMESTAMP Handling:
   - ALWAYS use: CAST(timestamp_col AS DATE) >= DATE('YYYY-MM-DD')
   - NEVER compare TIMESTAMP directly with string dates
   
2. Column Names:
   - products table: use "id" NOT "product_id"
   - users table: use "id" NOT "user_id"
   - orders table: "order_id", "user_id", "created_at"
   
3. GROUP BY + ORDER BY:
   - ORDER BY columns MUST be in GROUP BY OR aggregated
   - Use MAX(col), MIN(col), etc. for ORDER BY with GROUP BY
   
4. Optimization:
   - Use LIMIT for top-N queries
   - Avoid SELECT * when possible
   - Use appropriate JOINs (INNER vs LEFT)
   - Add WHERE filters before JOINs

EXAMPLES:
{examples}

OUTPUT: Return ONLY the SQL query, no explanations.
"""

SQL_FIX_PROMPT = """You are a BigQuery SQL debugging expert.

BROKEN SQL:
{broken_sql}

ERROR:
{error}

SCHEMA:
{schema_info}

COMMON FIXES:
1. TIMESTAMP errors → Add CAST(col AS DATE)
2. ORDER BY errors → Add to GROUP BY or use MAX/MIN
3. Column not found → Check schema for correct name
4. JOIN errors → Verify foreign key relationships

TASK: Fix the SQL and return ONLY the corrected query.
"""

# ============================================================================
# Understanding Prompts
# ============================================================================

UNDERSTANDING_PROMPT = """You are an AI assistant analyzing data queries.

QUERY: {query}

CONTEXT: {context}

AVAILABLE DATA:
- Products: name, category, price, brand
- Orders: order_id, status, created_at
- Users: id, country, state, city
- Order Items: product_id, sale_price, quantity

TASK: Analyze the query intent and complexity.

OUTPUT JSON:
{{
    "is_data_query": true/false,
    "needs_clarification": true/false,
    "intent": "brief description",
    "complexity": "simple/medium/complex",
    "required_info": ["list", "of", "needs"],
    "output_format": "table/chart/text"
}}

RULES:
- "simple": Single table, basic aggregation
- "medium": Multiple tables, JOINs
- "complex": Multiple JOINs, subqueries, window functions
"""

# ============================================================================
# Interpretation Prompts
# ============================================================================

INTERPRETATION_PROMPT = """You are a data analyst extracting insights.

QUERY: {query}

DATA PREVIEW:
{data_preview}

TASK: Extract key insights from the ACTUAL data above.

OUTPUT JSON:
{{
    "key_metrics": {{"metric": value}},
    "insights": ["insight 1", "insight 2"],
    "trends": ["trend 1"],
    "business_impact": "description",
    "recommendations": ["action 1", "action 2"]
}}

CRITICAL: Use ONLY the actual data shown. Do NOT make up numbers.
"""

# ============================================================================
# Synthesis Prompts
# ============================================================================

SYNTHESIS_PROMPT = """You are a professional business analyst.

QUERY: {query}

ACTUAL DATA:
{actual_data}

INSIGHTS:
{insights}

TASK: Create a professional response using the EXACT data above.

STRUCTURE:
1. Executive Summary (2-3 sentences)
2. Key Findings (bullet points with REAL numbers)
3. Analysis (1-2 paragraphs)
4. Recommendations (actionable items)

CRITICAL RULES:
- Use ONLY the actual numbers from the data
- Do NOT make up or estimate any values
- Be specific and cite exact figures
- Keep it concise and professional
"""
