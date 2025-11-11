from typing import Any, Optional
from abc import ABC, abstractmethod


class BaseTool(ABC):
    """Base class for all tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    async def execute(self, input_data: str) -> Any:
        """Execute the tool"""
        pass


class BigQueryTool(BaseTool):
    """Tool for executing BigQuery queries with auto-retry on syntax errors"""
    
    def __init__(self, bigquery_runner: Optional[Any] = None, llm_client: Optional[Any] = None):
        super().__init__(
            name="bigquery",
            description="Execute SQL queries on BigQuery. Input: SQL query string"
        )
        self.bq_runner = bigquery_runner
        self.llm = llm_client
        self.max_retries = 2
    
    async def execute(self, input_data: str) -> Any:
        """Execute BigQuery SQL with auto-retry on errors"""
        if not self.bq_runner:
            raise ValueError("BigQuery runner not initialized")
        
        sql_query = input_data.strip()
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                df = self.bq_runner.execute_query(sql_query)
                return {
                    "rows": len(df),
                    "columns": list(df.columns),
                    "data": df.to_dict('records')[:10],
                    "summary": df.describe().to_dict() if not df.empty else {},
                    "sql_used": sql_query,
                    "attempts": attempt + 1
                }
            except Exception as e:
                error_msg = str(e)
                last_error = error_msg
                
                # Check if it's a fixable error
                fixable_errors = [
                    "Syntax error",
                    "No matching signature",
                    "TIMESTAMP",
                    "DATE",
                    "not found",
                    "Unrecognized name",
                    "ORDER BY clause",
                    "neither grouped nor aggregated",
                    "Function not found",
                    "MONTH",
                    "YEAR",
                    "DAY"
                ]
                
                is_fixable = any(err in error_msg for err in fixable_errors)
                
                if is_fixable and attempt < self.max_retries and self.llm:
                    print(f"[Attempt {attempt + 1}] SQL Error detected, attempting to fix...")
                    sql_query = await self._fix_sql(sql_query, error_msg)
                    print(f"[Attempt {attempt + 1}] Retrying with fixed SQL...")
                else:
                    break
        
        raise Exception(f"Failed after {self.max_retries + 1} attempts. Last error: {last_error}")
    
    async def _fix_sql(self, broken_sql: str, error_msg: str) -> str:
        """Use LLM to fix broken SQL"""
        if not self.llm:
            return broken_sql
        
        prompt = f"""Fix this BigQuery SQL query. Return ONLY the corrected SQL.

BROKEN SQL:
{broken_sql}

ERROR:
{error_msg}

FIXES FOR COMMON ERRORS:

1. "Function not found: YEAR" or "Function not found: MONTH"
   FIX: Use EXTRACT(YEAR FROM date) or EXTRACT(MONTH FROM date)
   Example: EXTRACT(YEAR FROM created_at) = 2024

2. "HAVING clause expression references X which is neither grouped nor aggregated"
   FIX: Either add X to GROUP BY or use aggregate function
   Example: HAVING EXTRACT(YEAR FROM MAX(created_at)) = 2024
   OR: Add to GROUP BY: GROUP BY month, EXTRACT(YEAR FROM created_at)

3. "ORDER BY clause expression references X which is neither grouped nor aggregated"
   FIX: Use aggregate function like MAX(X) or MIN(X)
   Example: ORDER BY MAX(created_at) DESC

4. "No matching signature for operator >= for argument types: TIMESTAMP, DATE"
   FIX: CAST(created_at AS DATE) >= DATE('2024-01-01')

SCHEMA (EXACT COLUMNS):
- orders: order_id, user_id, status, created_at (TIMESTAMP)
- order_items: id, order_id, product_id, user_id, sale_price, created_at (TIMESTAMP), status

COLUMNS THAT DO NOT EXIST:
❌ orders.order_date (use orders.created_at)
❌ orders.num_of_item (does not exist)
❌ order_items.num_of_item (does not exist)
❌ order_items.order_date (use order_items.created_at)

RULES:
- Return ONLY the SQL query
- NO explanations, NO markdown, NO "Here is", NO "The fixed query"
- Start directly with SELECT

FIXED SQL:"""
        
        try:
            fixed_sql = await self.llm._call_llm(prompt, temperature=0.1, max_tokens=500)
            fixed_sql = fixed_sql.strip()
            
            # Remove markdown code blocks
            if fixed_sql.startswith("```"):
                import re
                match = re.search(r'```(?:sql)?\s*(.*?)\s*```', fixed_sql, re.DOTALL)
                if match:
                    fixed_sql = match.group(1).strip()
            
            # Remove any leading explanatory text
            lines = fixed_sql.split('\n')
            sql_lines = []
            found_select = False
            
            for line in lines:
                line = line.strip()
                # Start capturing from SELECT
                if line.upper().startswith('SELECT') or line.upper().startswith('WITH'):
                    found_select = True
                
                if found_select:
                    sql_lines.append(line)
            
            if sql_lines:
                fixed_sql = '\n'.join(sql_lines)
            
            # Validate it starts with SELECT or WITH
            if not (fixed_sql.upper().startswith('SELECT') or fixed_sql.upper().startswith('WITH')):
                print(f"Warning: Fixed SQL doesn't start with SELECT/WITH: {fixed_sql[:50]}")
                return broken_sql
            
            return fixed_sql
        except Exception as e:
            print(f"Failed to fix SQL: {e}")
            return broken_sql


class AnalysisTool(BaseTool):
    """Tool for data analysis"""
    
    def __init__(self):
        super().__init__(
            name="analyze",
            description="Analyze data and generate insights. Input: data description or query results"
        )
    
    async def execute(self, input_data: str) -> Any:
        """Perform analysis"""
        return {
            "analysis": f"Analysis of: {input_data[:100]}",
            "insights": [
                "Key finding 1",
                "Key finding 2",
                "Key finding 3"
            ]
        }


class ReportTool(BaseTool):
    """Tool for generating reports"""
    
    def __init__(self):
        super().__init__(
            name="report",
            description="Generate formatted reports. Input: report requirements"
        )
    
    async def execute(self, input_data: str) -> Any:
        """Generate report"""
        return {
            "report": f"Report generated for: {input_data}",
            "sections": ["Executive Summary", "Findings", "Recommendations"],
            "format": "markdown"
        }
