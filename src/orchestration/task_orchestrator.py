from typing import Dict, Any, List, Optional
import logging
import asyncio
from enum import Enum
from langsmith import traceable


class OrchestrationPattern(Enum):
    """Available orchestration patterns"""
    REACT = "react"
    PLAN_EXECUTE = "plan_execute"
    HYBRID = "hybrid"
    AUTO = "auto"


class TaskOrchestrator:
    """
    Advanced task orchestration system supporting multiple patterns:
    - ReAct: For simple, iterative tasks
    - Plan-and-Execute: For complex, multi-step tasks
    - Hybrid: Combines both patterns
    - Auto: Automatically selects best pattern
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.task_history = []
        
    @traceable(name="orchestrate_task")
    async def orchestrate(
        self,
        query: str,
        pattern: OrchestrationPattern = OrchestrationPattern.AUTO,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Main orchestration entry point"""
        
        if pattern == OrchestrationPattern.AUTO:
            pattern = await self._select_pattern(query, context)
        
        self.logger.info(f"Using {pattern.value} pattern for query: {query[:50]}...")
        
        try:
            if pattern == OrchestrationPattern.REACT:
                result = await self._execute_react(query, context)
            elif pattern == OrchestrationPattern.PLAN_EXECUTE:
                result = await self._execute_plan_execute(query, context)
            elif pattern == OrchestrationPattern.HYBRID:
                result = await self._execute_hybrid(query, context)
            else:
                raise ValueError(f"Unknown pattern: {pattern}")
            
            self._log_execution(query, pattern, result)
            return result
            
        except Exception as e:
            self.logger.error(f"Orchestration failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "pattern": pattern.value
            }
    
    @traceable(name="select_pattern")
    async def _select_pattern(
        self,
        query: str,
        context: Optional[Dict]
    ) -> OrchestrationPattern:
        """Automatically select best orchestration pattern"""
        
        complexity_score = await self._assess_complexity(query)
        
        if complexity_score < 3:
            return OrchestrationPattern.REACT
        elif complexity_score > 7:
            return OrchestrationPattern.PLAN_EXECUTE
        else:
            return OrchestrationPattern.HYBRID
    
    async def _assess_complexity(self, query: str) -> int:
        """Assess task complexity (0-10 scale)"""
        complexity_indicators = {
            "multiple steps": 3,
            "analyze": 2,
            "compare": 3,
            "generate report": 4,
            "segment": 3,
            "trend": 2,
            "forecast": 4,
            "aggregate": 2,
            "join": 2,
            "complex": 3
        }
        
        query_lower = query.lower()
        score = 0
        
        for indicator, points in complexity_indicators.items():
            if indicator in query_lower:
                score += points
        
        return min(score, 10)
    
    async def _execute_react(
        self,
        query: str,
        context: Optional[Dict]
    ) -> Dict[str, Any]:
        """Execute using ReAct pattern"""
        from .react_agent import ReActAgent
        
        tools = self._get_tools(context)
        llm = self._get_llm()
        
        agent = ReActAgent(tools, llm)
        result = await agent.execute(query)
        
        return {
            "success": result.get("completed", False),
            "pattern": "react",
            "iterations": result.get("iteration", 0),
            "observations": result.get("observations", []),
            "final_answer": result.get("final_answer"),
            "metadata": {
                "max_iterations": agent.max_iterations,
                "tools_used": len(result.get("observations", []))
            }
        }
    
    async def _execute_plan_execute(
        self,
        query: str,
        context: Optional[Dict]
    ) -> Dict[str, Any]:
        """Execute using Plan-and-Execute pattern"""
        from .plan_execute_agent import PlanAndExecuteAgent
        
        tools = self._get_tools(context)
        llm = self._get_llm()
        
        agent = PlanAndExecuteAgent(tools, llm)
        result = await agent.run(query)
        
        return {
            "success": result.get("success", False),
            "pattern": "plan_execute",
            "plan": result.get("plan", []),
            "execution": result.get("execution", {}),
            "final_result": result.get("final_result"),
            "metadata": {
                "subtasks": len(result.get("plan", [])),
                "completed_tasks": sum(
                    1 for r in result.get("execution", {}).get("results", {}).values()
                    if r.get("status") == "success"
                )
            }
        }
    
    async def _execute_hybrid(
        self,
        query: str,
        context: Optional[Dict]
    ) -> Dict[str, Any]:
        """Execute using hybrid approach"""
        
        subtasks = await self._decompose_task(query)
        
        results = []
        for subtask in subtasks:
            complexity = await self._assess_complexity(subtask["description"])
            
            if complexity < 5:
                result = await self._execute_react(subtask["description"], context)
            else:
                result = await self._execute_plan_execute(subtask["description"], context)
            
            results.append({
                "subtask": subtask,
                "result": result
            })
        
        final_answer = await self._synthesize_hybrid_results(query, results)
        
        return {
            "success": all(r["result"]["success"] for r in results),
            "pattern": "hybrid",
            "subtasks": subtasks,
            "results": results,
            "final_answer": final_answer,
            "metadata": {
                "total_subtasks": len(subtasks),
                "react_used": sum(1 for r in results if r["result"]["pattern"] == "react"),
                "plan_execute_used": sum(1 for r in results if r["result"]["pattern"] == "plan_execute")
            }
        }
    
    async def _decompose_task(self, query: str) -> List[Dict[str, Any]]:
        """Decompose complex task into subtasks"""
        llm = self._get_llm()
        
        prompt = f"""Decompose this task into independent subtasks:

Task: {query}

Output format (JSON):
{{
    "subtasks": [
        {{
            "id": "task_1",
            "description": "what to do",
            "priority": 1
        }}
    ]
}}
"""
        
        response = await llm.generate(prompt)
        
        import json
        import re
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            data = json.loads(json_match.group())
            return data.get("subtasks", [])
        
        return [{"id": "task_1", "description": query, "priority": 1}]
    
    async def _synthesize_hybrid_results(
        self,
        query: str,
        results: List[Dict]
    ) -> str:
        """Synthesize final answer from hybrid execution"""
        llm = self._get_llm()
        
        results_summary = "\n".join([
            f"Subtask {i+1}: {r['subtask']['description']}\n"
            f"Result: {r['result'].get('final_answer') or r['result'].get('final_result', 'N/A')}"
            for i, r in enumerate(results)
        ])
        
        prompt = f"""Synthesize a comprehensive answer from these subtask results:

Original Query: {query}

Subtask Results:
{results_summary}

Provide a clear, actionable final answer.
"""
        
        return await llm.generate(prompt)
    
    def _get_tools(self, context: Optional[Dict]) -> List[Any]:
        """Get available tools based on context"""
        from .tools import BigQueryTool, AnalysisTool, ReportTool
        
        tools = [
            BigQueryTool(context.get("bigquery_runner") if context else None),
            AnalysisTool(),
            ReportTool()
        ]
        
        return tools
    
    def _get_llm(self) -> Any:
        """Get LLM client"""
        from ..agents.base_agent import BaseAgent
        
        dummy_agent = BaseAgent(self.config)
        return dummy_agent
    
    def _log_execution(
        self,
        query: str,
        pattern: OrchestrationPattern,
        result: Dict[str, Any]
    ):
        """Log execution for monitoring"""
        self.task_history.append({
            "query": query,
            "pattern": pattern.value,
            "success": result.get("success", False),
            "metadata": result.get("metadata", {})
        })
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get orchestration performance metrics"""
        if not self.task_history:
            return {}
        
        total_tasks = len(self.task_history)
        successful_tasks = sum(1 for t in self.task_history if t["success"])
        
        pattern_usage = {}
        for task in self.task_history:
            pattern = task["pattern"]
            pattern_usage[pattern] = pattern_usage.get(pattern, 0) + 1
        
        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "success_rate": successful_tasks / total_tasks if total_tasks > 0 else 0,
            "pattern_usage": pattern_usage
        }
