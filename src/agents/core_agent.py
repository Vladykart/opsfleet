from src.agents.base_agent import BaseAgent
from src.mcp_client import get_mcp_client
from src.bigquery_runner import BigQueryRunner
import pandas as pd
import json
import os
from typing import List, Dict, Any


class CoreAgent(BaseAgent):
    
    async def initialize(self):
        self.mcp_client = await get_mcp_client()
        project_id = os.getenv("GCP_PROJECT_ID")
        dataset_id = self.config.get("bigquery", {}).get("dataset", "bigquery-public-data.thelook_ecommerce")
        self.bq_runner = BigQueryRunner(project_id=project_id, dataset_id=dataset_id)
    
    async def get_table_schema(self, table_name: str, dataset: str = None) -> Dict:
        if dataset is None:
            dataset = self.config.get("bigquery", {}).get("dataset", "thelook_ecommerce")
        
        result = await self.mcp_client.call_tool(
            server="bigquery",
            tool="describe-table",
            arguments={
                "table": table_name,
                "dataset": dataset
            }
        )
        
        return result
    
    async def list_tables(self, dataset: str = None) -> List[str]:
        if dataset is None:
            dataset = self.config.get("bigquery", {}).get("dataset", "thelook_ecommerce")
        
        result = await self.mcp_client.call_tool(
            server="bigquery",
            tool="list-tables",
            arguments={"dataset": dataset}
        )
        
        return result.get("tables", [])
    
    async def generate_sql(self, plan: Dict, tables: List[str]) -> List[str]:
        bigquery_docs = await self.mcp_client.call_tool(
            server="context7",
            tool="get-library-docs",
            arguments={
                "context7CompatibleLibraryID": "/googleapis/google-cloud-python",
                "topic": "BigQuery Standard SQL",
                "tokens": 3000
            }
        )
        
        schemas = {}
        for table in tables:
            schema = await self.get_table_schema(table)
            schemas[table] = schema
        
        prompt = self._build_sql_prompt_with_docs(
            plan=plan,
            schemas=schemas,
            bigquery_docs=bigquery_docs
        )
        
        sql_response = await self._call_llm(prompt, temperature=0.1)
        
        queries = self._parse_sql_response(sql_response)
        return queries
    
    def _build_sql_prompt_with_docs(
        self, 
        plan: Dict, 
        schemas: Dict,
        bigquery_docs: str
    ) -> str:
        
        prompt = f"""
Implement in pure Python using only stdlib. Shortest, elegant, clear, and efficient. Exclude all comments.

You are a BigQuery SQL expert. Generate optimized SQL queries for this analysis.

BIGQUERY DOCUMENTATION (From Context7 - Latest):
{bigquery_docs}

ANALYSIS PLAN:
{json.dumps(plan, indent=2)}

AVAILABLE TABLES AND SCHEMAS:
{json.dumps(schemas, indent=2)}

REQUIREMENTS:
1. Use BigQuery Standard SQL (not Legacy SQL)
2. Use the latest BigQuery functions and syntax from the docs above
3. Optimize for the 1TB free tier (use LIMIT, avoid SELECT *)
4. Include CTEs for readability
5. Return ONLY valid SQL queries, one per line

Generate the SQL queries:
"""
        return prompt
    
    def _parse_sql_response(self, response: str) -> List[str]:
        lines = response.strip().split('\n')
        queries = []
        current_query = []
        
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('#') and not stripped.startswith('--'):
                current_query.append(line)
                if ';' in line:
                    queries.append('\n'.join(current_query))
                    current_query = []
        
        if current_query:
            queries.append('\n'.join(current_query))
        
        return queries
    
    async def execute_queries(self, sql_queries: List[str]) -> Dict:
        results = []
        stats = {}
        
        for idx, sql in enumerate(sql_queries):
            try:
                result = await self.mcp_client.call_tool(
                    server="bigquery",
                    tool="execute-query",
                    arguments={"query": sql}
                )
                
                if isinstance(result, dict):
                    df = pd.DataFrame(result.get("rows", []))
                else:
                    df = pd.DataFrame(result)
                
                results.append(df)
                
                stats[f"query_{idx}"] = {
                    "rows": len(df),
                    "columns": len(df.columns),
                    "success": True,
                    "bytes_processed": result.get("bytes_processed", 0) if isinstance(result, dict) else 0
                }
                
                self.logger.info(f"Query {idx} executed: {len(df)} rows")
                
            except Exception as e:
                self.logger.error(f"Query {idx} failed: {e}")
                stats[f"query_{idx}"] = {
                    "success": False,
                    "error": str(e)
                }
        
        return {
            "dataframes": results,
            "stats": stats
        }
    
    async def generate_report(
        self, 
        insights: List[str], 
        metrics: Dict, 
        analysis: Dict
    ) -> Dict:
        langgraph_docs = await self.mcp_client.call_tool(
            server="context7",
            tool="get-library-docs",
            arguments={
                "context7CompatibleLibraryID": "/langchain-ai/langgraph",
                "topic": "state management and structured outputs",
                "tokens": 2000
            }
        )
        
        prompt = self._build_report_prompt(
            insights=insights,
            metrics=metrics,
            analysis=analysis,
            langgraph_docs=langgraph_docs
        )
        
        report_text = await self._call_llm(prompt, temperature=0.3)
        
        return {
            "text": report_text,
            "recommendations": self._extract_recommendations(report_text)
        }
    
    def _build_report_prompt(
        self,
        insights: List[str],
        metrics: Dict,
        analysis: Dict,
        langgraph_docs: str
    ) -> str:
        prompt = f"""
Generate a comprehensive business analysis report.

INSIGHTS:
{json.dumps(insights, indent=2)}

KEY METRICS:
{json.dumps(metrics, indent=2)}

ANALYSIS RESULTS:
{json.dumps(analysis, indent=2)}

Create a report with:
1. Executive Summary
2. Key Findings
3. Business Implications
4. Recommendations

Format as markdown.
"""
        return prompt
    
    def _extract_recommendations(self, report_text: str) -> List[str]:
        recommendations = []
        lines = report_text.split('\n')
        in_recommendations = False
        
        for line in lines:
            if 'recommendation' in line.lower():
                in_recommendations = True
                continue
            if in_recommendations and line.strip().startswith(('-', '*', '1.', '2.', '3.')):
                recommendations.append(line.strip().lstrip('-*123456789. '))
        
        return recommendations
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return state
