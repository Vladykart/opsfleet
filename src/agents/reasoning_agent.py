from src.agents.base_agent import BaseAgent
from src.mcp_client import get_mcp_client
import json
from typing import Dict, List, Any


class ReasoningAgent(BaseAgent):
    
    async def initialize(self):
        self.mcp_client = await get_mcp_client()
    
    async def create_analysis_plan(
        self, 
        query: str, 
        context: List[Dict]
    ) -> Dict:
        langgraph_docs = await self.mcp_client.call_tool(
            server="context7",
            tool="get-library-docs",
            arguments={
                "context7CompatibleLibraryID": "/langchain-ai/langgraph",
                "topic": "planning and reasoning patterns",
                "tokens": 3000
            }
        )
        
        datasets = await self.mcp_client.call_tool(
            server="bigquery",
            tool="list-datasets",
            arguments={}
        )
        
        prompt = f"""
Implement in pure Python using only stdlib. Shortest, elegant, clear, and efficient. Exclude all comments.

You are an analysis planning expert. Create a structured plan.

LANGGRAPH PATTERNS (From Context7 - Latest):
{langgraph_docs}

USER QUERY:
{query}

AVAILABLE DATASETS:
{datasets}

RELEVANT CONTEXT:
{json.dumps(context, indent=2)}

Create a detailed JSON plan with:
1. analysis_type: "segmentation" | "trends" | "geographic" | "product"
2. required_tables: List of tables needed
3. join_strategy: How to join tables
4. key_metrics: Metrics to calculate
5. reasoning_steps: Step-by-step approach
6. expected_insights: What we expect to find

Return ONLY valid JSON:
"""
        
        plan_json = await self._call_llm(prompt, temperature=0.2)
        
        try:
            plan = json.loads(plan_json)
        except json.JSONDecodeError:
            cleaned = plan_json.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            plan = json.loads(cleaned.strip())
        
        return plan
    
    async def analyze_data(
        self,
        dataframes: List[Any],
        query_plan: Dict
    ) -> Dict:
        
        df_summaries = []
        for idx, df in enumerate(dataframes):
            summary = {
                "query_index": idx,
                "rows": len(df),
                "columns": list(df.columns),
                "sample": df.head(5).to_dict() if not df.empty else {}
            }
            df_summaries.append(summary)
        
        prompt = f"""
Analyze this e-commerce data and extract insights:

QUERY PLAN:
{json.dumps(query_plan, indent=2)}

DATA SUMMARIES:
{json.dumps(df_summaries, indent=2)}

Focus on:
- Significant patterns
- Anomalies or outliers
- Business implications
- Actionable trends

Provide structured analysis with metrics in JSON format:
{{
    "key_findings": [],
    "metrics": {{}},
    "patterns": [],
    "anomalies": [],
    "business_implications": []
}}
"""
        
        analysis_json = await self._call_llm(prompt, temperature=0.2)
        
        try:
            analysis = json.loads(analysis_json)
        except json.JSONDecodeError:
            cleaned = analysis_json.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            analysis = json.loads(cleaned.strip())
        
        return analysis
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return state
