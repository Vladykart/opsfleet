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
        
        prompt = f"""
Implement in pure Python using only stdlib. Shortest, elegant, clear, and efficient. Exclude all comments.

You are a data analyst expert. Generate a BigQuery SQL query for customer segmentation analysis.

USER QUERY: {query}

AVAILABLE SCHEMAS:
Users Table: {json.dumps(schema, indent=2)}
Orders Table: {json.dumps(orders_schema, indent=2)}

Generate ONE optimized BigQuery Standard SQL query that:
1. Segments customers by behavior (RFM analysis, purchase frequency, etc.)
2. Calculates key metrics per segment
3. Uses CTEs for clarity
4. Limits results to top segments (LIMIT 100)
5. Returns ONLY the SQL query, no explanation

SQL Query:
"""
        
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
        
        prompt = f"""
Implement in pure Python using only stdlib. Shortest, elegant, clear, and efficient. Exclude all comments.

Generate BigQuery SQL for product performance analysis.

USER QUERY: {query}

SCHEMAS:
Products: {json.dumps(products_schema, indent=2)}
Order Items: {json.dumps(order_items_schema, indent=2)}

Create ONE query that analyzes:
1. Top performing products by revenue/units
2. Product category trends
3. Profit margins
4. Return rates if applicable

Return ONLY SQL, no explanation. Use LIMIT 100.

SQL Query:
"""
        
        sql = await self._call_llm(prompt, temperature=0.1)
        sql = self._clean_sql(sql)
        
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
        
        prompt = f"""
Implement in pure Python using only stdlib. Shortest, elegant, clear, and efficient. Exclude all comments.

Generate BigQuery SQL for sales trend analysis.

USER QUERY: {query}

SCHEMAS:
Orders: {json.dumps(orders_schema, indent=2)}
Order Items: {json.dumps(order_items_schema, indent=2)}

Create ONE query analyzing:
1. Sales trends over time (daily/weekly/monthly)
2. Seasonality patterns
3. Growth rates
4. Peak periods

Return ONLY SQL. Use LIMIT 365 for time series.

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
        
        prompt = f"""
Implement in pure Python using only stdlib. Shortest, elegant, clear, and efficient. Exclude all comments.

Generate BigQuery SQL for geographic sales analysis.

USER QUERY: {query}

SCHEMAS:
Users: {json.dumps(users_schema, indent=2)}
Orders: {json.dumps(orders_schema, indent=2)}

Create ONE query analyzing:
1. Sales by region/country/state
2. Geographic customer distribution
3. Regional performance metrics
4. Market penetration

Return ONLY SQL. Use LIMIT 100.

SQL Query:
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
        
        prompt = f"""
Implement in pure Python using only stdlib. Shortest, elegant, clear, and efficient. Exclude all comments.

Generate BigQuery SQL for custom data analysis.

USER QUERY: {query}
ANALYSIS TYPE: {analysis_type}

AVAILABLE SCHEMAS:
{json.dumps(schemas, indent=2)}

Dataset: bigquery-public-data.thelook_ecommerce

Create ONE optimized BigQuery Standard SQL query that:
1. Addresses the user's specific question
2. Uses appropriate tables and joins
3. Calculates relevant metrics
4. Uses CTEs for complex logic
5. Limits results appropriately (LIMIT 100-500 depending on analysis)

Return ONLY the SQL query, no explanation or markdown.

SQL Query:
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
        return sql
    
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
