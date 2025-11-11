from src.agents.base_agent import BaseAgent
from src.bigquery_runner import BigQueryRunner
from typing import Dict, Any, List
import pandas as pd
import json
import os


class DataAnalysisAgent(BaseAgent):
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.bq_runner = None
        
    async def initialize(self):
        await super().initialize()
        project_id = os.getenv("GCP_PROJECT_ID")
        dataset_id = self.config.get("bigquery", {}).get("dataset", "bigquery-public-data.thelook_ecommerce")
        self.bq_runner = BigQueryRunner(project_id=project_id, dataset_id=dataset_id)
        self.logger.info(f"BigQueryRunner initialized with dataset: {dataset_id}")
    
    async def analyze_customer_segmentation(self, query: str) -> Dict[str, Any]:
        schema = self.bq_runner.get_table_schema("users")
        orders_schema = self.bq_runner.get_table_schema("orders")
        
        prompt = f"""Generate a BigQuery SQL query for customer segmentation.

Query: {query}

Tables:
- bigquery-public-data.thelook_ecommerce.users (id, first_name, last_name, country)
- bigquery-public-data.thelook_ecommerce.orders (order_id, user_id, status, num_of_item)

Requirements:
- Count orders per customer
- Segment customers by order count (High: >=10, Medium: >=5, Low: <5)
- Show segment name, customer count, average orders
- Use WITH clause for customer_orders
- LIMIT 10

Return ONLY the SQL query."""
        
        sql = await self._call_llm(prompt, temperature=0.1)
        sql = self._clean_sql(sql)
        
        df = self.bq_runner.execute_query(sql)
        
        insights = await self._generate_insights(df, "customer_segmentation")
        
        return {
            "sql": sql,
            "data": df,
            "insights": insights,
            "row_count": len(df)
        }
    
    async def analyze_product_performance(self, query: str) -> Dict[str, Any]:
        products_schema = self.bq_runner.get_table_schema("products")
        order_items_schema = self.bq_runner.get_table_schema("order_items")
        
        prompt = f"""Generate a BigQuery SQL query for product analysis.

Query: {query}

Tables available:
- bigquery-public-data.thelook_ecommerce.products (id, name, category, brand, cost, retail_price)
- bigquery-public-data.thelook_ecommerce.order_items (order_id, product_id, sale_price, status)

Requirements:
- Use BigQuery Standard SQL syntax
- JOIN products and order_items tables
- Calculate total revenue: SUM(sale_price)
- Group by product name
- Order by revenue DESC
- LIMIT 10
- Exclude cancelled orders

Return ONLY the SQL query, no explanations."""
        
        sql = await self._call_llm(prompt, temperature=0.1)
        sql = self._clean_sql(sql)
        
        self.logger.info(f"Generated SQL for product analysis: {sql[:200]}...")
        
        df = self.bq_runner.execute_query(sql)
        
        insights = await self._generate_insights(df, "product_performance")
        
        return {
            "sql": sql,
            "data": df,
            "insights": insights,
            "row_count": len(df)
        }
    
    async def analyze_sales_trends(self, query: str) -> Dict[str, Any]:
        orders_schema = self.bq_runner.get_table_schema("orders")
        order_items_schema = self.bq_runner.get_table_schema("order_items")
        
        prompt = f"""You are a BigQuery SQL expert. Generate a query for sales trend analysis.

USER QUERY: {query}

SCHEMAS:
Orders: {json.dumps(orders_schema, indent=2)}
Order Items: {json.dumps(order_items_schema, indent=2)}

Create ONE query analyzing:
1. Sales trends over time
2. Seasonality patterns
3. Growth rates

Return ONLY SQL. Use LIMIT 365.

SQL Query:
"""
        
        sql = await self._call_llm(prompt, temperature=0.1)
        sql = self._clean_sql(sql)
        
        df = self.bq_runner.execute_query(sql)
        
        insights = await self._generate_insights(df, "sales_trends")
        
        return {
            "sql": sql,
            "data": df,
            "insights": insights,
            "row_count": len(df)
        }
    
    async def analyze_geographic_patterns(self, query: str) -> Dict[str, Any]:
        users_schema = self.bq_runner.get_table_schema("users")
        orders_schema = self.bq_runner.get_table_schema("orders")
        
        prompt = f"""Generate a BigQuery SQL query for geographic analysis.

Query: {query}

Tables:
- `bigquery-public-data.thelook_ecommerce.users` (id, country, state, city, created_at)
- `bigquery-public-data.thelook_ecommerce.orders` (order_id, user_id, status, num_of_item, created_at)

Example:
SELECT 
    u.country,
    COUNT(DISTINCT o.order_id) as total_orders,
    COUNT(DISTINCT u.id) as total_customers,
    SUM(o.num_of_item) as total_items
FROM `bigquery-public-data.thelook_ecommerce.users` u
JOIN `bigquery-public-data.thelook_ecommerce.orders` o ON u.id = o.user_id
WHERE o.status = 'Complete'
GROUP BY u.country
ORDER BY total_orders DESC
LIMIT 10

Requirements:
- Use full table names with backticks
- Use table aliases (u for users, o for orders)
- Filter for completed orders only
- GROUP BY geographic dimension
- ORDER BY relevant metric DESC
- LIMIT 10

Return ONLY the SQL query.
"""
        
        sql = await self._call_llm(prompt, temperature=0.1)
        sql = self._clean_sql(sql)
        
        df = self.bq_runner.execute_query(sql)
        
        insights = await self._generate_insights(df, "geographic_patterns")
        
        return {
            "sql": sql,
            "data": df,
            "insights": insights,
            "row_count": len(df)
        }
    
    async def execute_custom_analysis(self, query: str, analysis_type: str) -> Dict[str, Any]:
        tables = ["users", "orders", "order_items", "products"]
        schemas = {}
        for table in tables:
            try:
                schemas[table] = self.bq_runner.get_table_schema(table)
            except Exception as e:
                self.logger.warning(f"Could not fetch schema for {table}: {e}")
        
        prompt = f"""Generate a BigQuery SQL query for {analysis_type} analysis.

Query: {query}

Tables (use full names with backticks):
- `bigquery-public-data.thelook_ecommerce.users` (id, country, state, city)
- `bigquery-public-data.thelook_ecommerce.orders` (order_id, user_id, status, num_of_item)
- `bigquery-public-data.thelook_ecommerce.order_items` (order_id, product_id, sale_price)
- `bigquery-public-data.thelook_ecommerce.products` (id, name, category, cost, retail_price)

Example for geographic analysis:
SELECT 
    u.country,
    COUNT(DISTINCT o.order_id) as order_count,
    COUNT(DISTINCT u.id) as customer_count
FROM `bigquery-public-data.thelook_ecommerce.users` u
JOIN `bigquery-public-data.thelook_ecommerce.orders` o ON u.id = o.user_id
WHERE o.status = 'Complete'
GROUP BY u.country
ORDER BY order_count DESC
LIMIT 10

Requirements:
- Use full table names with backticks
- Use clear table aliases (u, o, oi, p)
- Include WHERE clause to filter valid data
- GROUP BY all non-aggregated columns
- ORDER BY relevant metric DESC
- LIMIT 10

Return ONLY the SQL query, no explanations.
"""
        
        sql = await self._call_llm(prompt, temperature=0.1)
        sql = self._clean_sql(sql)
        
        df = self.bq_runner.execute_query(sql)
        
        insights = await self._generate_insights(df, analysis_type)
        
        return {
            "sql": sql,
            "data": df,
            "insights": insights,
            "row_count": len(df)
        }
    
    def _clean_sql(self, sql: str) -> str:
        sql = sql.strip()
        
        if sql.startswith("```sql"):
            sql = sql[6:]
        elif sql.startswith("```"):
            sql = sql[3:]
        if sql.endswith("```"):
            sql = sql[:-3]
        
        sql = sql.strip()
        
        lines = sql.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('--'):
                cleaned_lines.append(line)
        
        sql = ' '.join(cleaned_lines)
        
        if 'SQL Query:' in sql:
            sql = sql.split('SQL Query:')[-1].strip()
        
        sql = sql.replace('\\n', ' ')
        
        import re
        sql = re.sub(r'\s+', ' ', sql)
        
        return sql.strip()
    
    async def _generate_insights(self, df: pd.DataFrame, analysis_type: str) -> List[str]:
        if df.empty:
            return ["No data returned from query"]
        
        summary_stats = df.describe().to_dict() if not df.empty else {}
        
        prompt = f"""
Generate 3-5 key business insights from this data analysis.

ANALYSIS TYPE: {analysis_type}
DATA SHAPE: {df.shape[0]} rows, {df.shape[1]} columns
COLUMNS: {list(df.columns)}
SAMPLE DATA (first 5 rows):
{df.head().to_string()}

SUMMARY STATISTICS:
{json.dumps(summary_stats, indent=2, default=str)}

Provide concise, actionable insights. Each insight should be one clear sentence.
Format as a numbered list.
"""
        
        response = await self._call_llm(prompt, temperature=0.3, max_tokens=1024)
        
        insights = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('*')):
                insight = line.lstrip('0123456789.-* ')
                if insight:
                    insights.append(insight)
        
        return insights[:5]
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        query = state.get("user_query", "")
        analysis_type = state.get("analysis_type", "custom")
        
        try:
            if "customer" in query.lower() or "segment" in query.lower():
                result = await self.analyze_customer_segmentation(query)
            elif "product" in query.lower() or "inventory" in query.lower():
                result = await self.analyze_product_performance(query)
            elif "sales" in query.lower() or "revenue" in query.lower() or "trend" in query.lower():
                result = await self.analyze_sales_trends(query)
            elif "geographic" in query.lower() or "region" in query.lower() or "location" in query.lower():
                result = await self.analyze_geographic_patterns(query)
            else:
                result = await self.execute_custom_analysis(query, analysis_type)
            
            return {
                "analysis_results": result,
                "insights": result["insights"],
                "query_results": [result["data"]],
                "generated_sql": [result["sql"]]
            }
        except Exception as e:
            self.logger.error(f"Analysis failed: {e}", exc_info=True)
            return {
                "errors": [str(e)],
                "analysis_results": {},
                "insights": []
            }
