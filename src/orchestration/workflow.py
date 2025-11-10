from langgraph.graph import StateGraph, END
from typing import Dict, Any
import logging
from datetime import datetime
import uuid

from src.orchestration.state import AgentState
from src.agents.core_agent import CoreAgent
from src.agents.memory_agent import MemoryAgent
from src.agents.reasoning_agent import ReasoningAgent
from src.agents.validator_agent import ValidatorAgent
from src.agents.data_analysis_agent import DataAnalysisAgent

logger = logging.getLogger(__name__)


class DataAnalysisWorkflow:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        self.memory_agent = MemoryAgent(config)
        self.core_agent = CoreAgent(config)
        self.reasoning_agent = ReasoningAgent(config)
        self.validator_agent = ValidatorAgent(config)
        self.data_analysis_agent = DataAnalysisAgent(config)
        
        self.workflow = self._build_workflow()
        
    async def initialize(self):
        await self.memory_agent.initialize()
        await self.core_agent.initialize()
        await self.reasoning_agent.initialize()
        await self.data_analysis_agent.initialize()
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        workflow.add_node("retrieve_memory", self._retrieve_memory_node)
        workflow.add_node("plan_analysis", self._plan_analysis_node)
        workflow.add_node("execute_bigquery_analysis", self._execute_bigquery_analysis_node)
        workflow.add_node("generate_sql", self._generate_sql_node)
        workflow.add_node("execute_query", self._execute_query_node)
        workflow.add_node("validate_results", self._validate_results_node)
        workflow.add_node("analyze_data", self._analyze_data_node)
        workflow.add_node("generate_report", self._generate_report_node)
        workflow.add_node("store_memory", self._store_memory_node)
        
        workflow.set_entry_point("retrieve_memory")
        workflow.add_edge("retrieve_memory", "plan_analysis")
        workflow.add_conditional_edges(
            "plan_analysis",
            self._route_analysis,
            {
                "bigquery": "execute_bigquery_analysis",
                "custom": "generate_sql"
            }
        )
        workflow.add_edge("execute_bigquery_analysis", "generate_report")
        workflow.add_edge("plan_analysis", "generate_sql")
        workflow.add_edge("generate_sql", "execute_query")
        workflow.add_edge("execute_query", "validate_results")
        
        workflow.add_conditional_edges(
            "validate_results",
            self._should_continue,
            {
                "continue": "analyze_data",
                "retry": "generate_sql",
                "error": END
            }
        )
        
        workflow.add_edge("analyze_data", "generate_report")
        workflow.add_edge("generate_report", "store_memory")
        workflow.add_edge("store_memory", END)
        
        return workflow.compile()
    
    async def _retrieve_memory_node(self, state: AgentState) -> Dict[str, Any]:
        logger.info("Retrieving memory context")
        context = await self.memory_agent.retrieve_context(
            query=state["user_query"],
            limit=5
        )
        return {
            "retrieved_context": context,
            "current_step": "retrieve_memory"
        }
    
    async def _plan_analysis_node(self, state: AgentState) -> Dict[str, Any]:
        logger.info("Planning analysis")
        plan = await self.reasoning_agent.create_analysis_plan(
            query=state["user_query"],
            context=state.get("retrieved_context", [])
        )
        return {
            "analysis_type": plan.get("analysis_type"),
            "required_tables": plan.get("required_tables", []),
            "query_plan": plan,
            "current_step": "plan_analysis"
        }
    
    async def _generate_sql_node(self, state: AgentState) -> Dict[str, Any]:
        logger.info("Generating SQL")
        sql_queries = await self.core_agent.generate_sql(
            plan=state["query_plan"],
            tables=state["required_tables"]
        )
        return {
            "generated_sql": sql_queries,
            "current_step": "generate_sql"
        }
    
    async def _execute_query_node(self, state: AgentState) -> Dict[str, Any]:
        logger.info("Executing queries")
        results = await self.core_agent.execute_queries(
            sql_queries=state["generated_sql"]
        )
        return {
            "query_results": results["dataframes"],
            "execution_stats": results["stats"],
            "current_step": "execute_query"
        }
    
    async def _validate_results_node(self, state: AgentState) -> Dict[str, Any]:
        logger.info("Validating results")
        validation = await self.validator_agent.validate_results(
            results=state["query_results"]
        )
        return {
            "validation_status": validation["status"],
            "validation_errors": validation.get("errors", []),
            "current_step": "validate_results"
        }
    
    async def _analyze_data_node(self, state: AgentState) -> Dict[str, Any]:
        logger.info("Analyzing data")
        analysis = await self.reasoning_agent.analyze_data(
            dataframes=state["query_results"],
            query_plan=state["query_plan"]
        )
        return {
            "analysis_results": analysis,
            "key_metrics": analysis.get("metrics", {}),
            "insights": analysis.get("key_findings", []),
            "current_step": "analyze_data"
        }
    
    async def _generate_report_node(self, state: AgentState) -> Dict[str, Any]:
        logger.info("Generating report")
        report = await self.core_agent.generate_report(
            insights=state["insights"],
            metrics=state["key_metrics"],
            analysis=state["analysis_results"]
        )
        return {
            "report": report["text"],
            "recommendations": report.get("recommendations", []),
            "current_step": "generate_report"
        }
    
    async def _store_memory_node(self, state: AgentState) -> Dict[str, Any]:
        logger.info("Storing in memory")
        await self.memory_agent.store_analysis(
            query=state["user_query"],
            insights=state["insights"],
            report=state["report"],
            analysis_type=state.get("analysis_type", "unknown")
        )
        return {
            "current_step": "store_memory"
        }
    
    def _route_analysis(self, state: AgentState) -> str:
        query = state.get("user_query", "").lower()
        keywords = ["customer", "segment", "product", "sales", "revenue", "trend", "geographic", "region"]
        if any(keyword in query for keyword in keywords):
            return "bigquery"
        return "custom"
    
    async def _execute_bigquery_analysis_node(self, state: AgentState) -> Dict[str, Any]:
        logger.info("Executing BigQuery analysis")
        result = await self.data_analysis_agent.process(state)
        return {
            "analysis_results": result.get("analysis_results", {}),
            "insights": result.get("insights", []),
            "query_results": result.get("query_results", []),
            "generated_sql": result.get("generated_sql", []),
            "validation_status": True,
            "current_step": "execute_bigquery_analysis"
        }
    
    def _should_continue(self, state: AgentState) -> str:
        if state.get("validation_status"):
            return "continue"
        
        retry_count = state.get("retry_count", 0)
        if retry_count < 2:
            logger.warning(f"Validation failed, retrying (attempt {retry_count + 1})")
            return "retry"
        
        logger.error("Validation failed after max retries")
        return "error"
    
    async def run(self, query: str) -> Dict[str, Any]:
        initial_state: AgentState = {
            "user_query": query,
            "timestamp": datetime.now(),
            "session_id": str(uuid.uuid4()),
            "conversation_history": [],
            "retrieved_context": [],
            "persona_config": {},
            "analysis_type": None,
            "required_tables": [],
            "query_plan": None,
            "generated_sql": [],
            "sql_metadata": {},
            "query_results": [],
            "execution_stats": {},
            "analysis_results": {},
            "key_metrics": {},
            "insights": [],
            "validation_status": False,
            "validation_errors": [],
            "report": None,
            "recommendations": [],
            "errors": [],
            "retry_count": 0,
            "current_step": "init"
        }
        
        result = await self.workflow.ainvoke(initial_state)
        
        return result


def create_workflow(config: Dict[str, Any]) -> DataAnalysisWorkflow:
    return DataAnalysisWorkflow(config)
