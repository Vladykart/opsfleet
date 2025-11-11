from typing import Dict, Any, List
import logging
from langsmith import traceable
import asyncio


class PlanAndExecuteAgent:
    """
    Plan-and-Execute pattern implementation.
    Two-phase approach: Plan first, then execute sequentially.
    """
    
    def __init__(self, tools: List[Any], llm_client: Any):
        self.tools = {tool.name: tool for tool in tools}
        self.llm = llm_client
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @traceable(name="plan_phase")
    async def plan(self, query: str) -> List[Dict[str, Any]]:
        """Planning phase: break down task into subtasks"""
        prompt = f"""You are a task planning assistant for data analysis.

Task: {query}

Available Tools:
{self._format_tools()}

Create a detailed execution plan. Break the task into subtasks.

Output format (JSON):
{{
    "subtasks": [
        {{
            "id": "task_1",
            "name": "descriptive name",
            "description": "what to do",
            "tool": "tool name to use",
            "input": "input for the tool",
            "dependencies": []
        }}
    ]
}}

Requirements:
1. Appropriate subtask granularity
2. Clear task dependencies
3. Logical execution order
4. Each subtask uses one tool
"""
        
        response = await self.llm.generate(prompt)
        plan = self._parse_plan(response)
        
        self._validate_plan(plan)
        return plan
    
    @traceable(name="execute_phase")
    async def execute(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execution phase: execute subtasks in order"""
        results = {}
        execution_log = []
        
        for subtask in plan:
            try:
                self.logger.info(f"Executing subtask: {subtask['id']} - {subtask['name']}")
                
                if not self._dependencies_met(subtask, results):
                    self.logger.warning(f"Dependencies not met for {subtask['id']}")
                    continue
                
                tool_input = self._prepare_input(subtask, results)
                
                tool = self.tools.get(subtask['tool'])
                if not tool:
                    raise ValueError(f"Tool not found: {subtask['tool']}")
                
                result = await tool.execute(tool_input)
                
                results[subtask['id']] = {
                    "subtask": subtask,
                    "result": result,
                    "status": "success"
                }
                
                execution_log.append({
                    "subtask_id": subtask['id'],
                    "status": "success",
                    "result_summary": str(result)[:100]
                })
                
            except Exception as e:
                self.logger.error(f"Subtask {subtask['id']} failed: {e}")
                results[subtask['id']] = {
                    "subtask": subtask,
                    "error": str(e),
                    "status": "failed"
                }
                execution_log.append({
                    "subtask_id": subtask['id'],
                    "status": "failed",
                    "error": str(e)
                })
                
                if subtask.get('critical', False):
                    break
        
        return {
            "results": results,
            "execution_log": execution_log,
            "completed": all(r["status"] == "success" for r in results.values())
        }
    
    @traceable(name="plan_and_execute")
    async def run(self, query: str) -> Dict[str, Any]:
        """Complete plan-and-execute workflow"""
        try:
            plan = await self.plan(query)
            
            self.logger.info(f"Generated plan with {len(plan)} subtasks")
            
            execution_result = await self.execute(plan)
            
            final_result = await self._synthesize_results(
                query, 
                plan, 
                execution_result
            )
            
            return {
                "query": query,
                "plan": plan,
                "execution": execution_result,
                "final_result": final_result,
                "success": execution_result["completed"]
            }
            
        except Exception as e:
            self.logger.error(f"Plan-and-execute failed: {e}")
            return {
                "query": query,
                "error": str(e),
                "success": False
            }
    
    @traceable(name="synthesize_results")
    async def _synthesize_results(
        self, 
        query: str, 
        plan: List[Dict], 
        execution: Dict
    ) -> str:
        """Synthesize final answer from execution results"""
        prompt = f"""Synthesize the final answer based on execution results.

Original Query: {query}

Execution Plan:
{self._format_plan(plan)}

Execution Results:
{self._format_results(execution['results'])}

Generate a comprehensive final answer that:
1. Directly answers the original query
2. Incorporates key findings from all subtasks
3. Provides actionable insights
4. Is clear and concise
"""
        
        return await self.llm.generate(prompt)
    
    def _format_tools(self) -> str:
        """Format available tools"""
        return "\n".join([
            f"- {name}: {tool.description}"
            for name, tool in self.tools.items()
        ])
    
    def _parse_plan(self, response: str) -> List[Dict[str, Any]]:
        """Parse plan from LLM response"""
        import json
        import re
        
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            plan_data = json.loads(json_match.group())
            return plan_data.get("subtasks", [])
        
        return []
    
    def _validate_plan(self, plan: List[Dict[str, Any]]):
        """Validate plan structure and dependencies"""
        task_ids = {task['id'] for task in plan}
        
        for task in plan:
            for dep in task.get('dependencies', []):
                if dep not in task_ids:
                    raise ValueError(f"Invalid dependency: {dep} not in plan")
    
    def _dependencies_met(self, subtask: Dict, results: Dict) -> bool:
        """Check if subtask dependencies are met"""
        for dep in subtask.get('dependencies', []):
            if dep not in results or results[dep]['status'] != 'success':
                return False
        return True
    
    def _prepare_input(self, subtask: Dict, results: Dict) -> str:
        """Prepare input for subtask, incorporating previous results"""
        base_input = subtask['input']
        
        for dep in subtask.get('dependencies', []):
            if dep in results:
                dep_result = results[dep]['result']
                base_input += f"\n\nPrevious result from {dep}: {dep_result}"
        
        return base_input
    
    def _format_plan(self, plan: List[Dict]) -> str:
        """Format plan for display"""
        return "\n".join([
            f"{i+1}. {task['name']}: {task['description']}"
            for i, task in enumerate(plan)
        ])
    
    def _format_results(self, results: Dict) -> str:
        """Format execution results"""
        return "\n".join([
            f"- {task_id}: {data['status']} - {str(data.get('result', data.get('error', '')))[:100]}"
            for task_id, data in results.items()
        ])
