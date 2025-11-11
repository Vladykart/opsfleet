from typing import Dict, Any, List, Optional
import logging
from langsmith import traceable


class ReActAgent:
    """
    ReAct (Reasoning and Acting) pattern implementation.
    Iterative approach: Think -> Act -> Observe -> Repeat
    """
    
    def __init__(self, tools: List[Any], llm_client: Any, max_iterations: int = 5):
        self.tools = {tool.name: tool for tool in tools}
        self.llm = llm_client
        self.max_iterations = max_iterations
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @traceable(name="react_reasoning")
    async def reason(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Reasoning step: analyze current state and decide next action"""
        prompt = f"""You are a data analysis assistant using ReAct pattern.

Current State:
- Query: {state.get('query')}
- Observations: {state.get('observations', [])}
- Iteration: {state.get('iteration', 0)}

Available Tools:
{self._format_tools()}

Think step by step:
1. What do I know so far?
2. What do I need to find out?
3. Which tool should I use next?

Respond in this format:
Thought: [your reasoning]
Action: [tool name]
Action Input: [input for the tool]
"""
        
        response = await self.llm.generate(prompt)
        return self._parse_response(response)
    
    @traceable(name="react_act")
    async def act(self, action: str, action_input: str) -> Any:
        """Acting step: execute the chosen action"""
        if action not in self.tools:
            raise ValueError(f"Unknown tool: {action}")
        
        tool = self.tools[action]
        result = await tool.execute(action_input)
        return result
    
    @traceable(name="react_observe")
    def observe(self, state: Dict[str, Any], result: Any) -> Dict[str, Any]:
        """Observation step: record action result"""
        observation = {
            "iteration": state.get("iteration", 0),
            "action": state.get("current_action"),
            "result": result
        }
        
        state.setdefault("observations", []).append(observation)
        return state
    
    @traceable(name="react_execute")
    async def execute(self, query: str) -> Dict[str, Any]:
        """Execute ReAct loop"""
        state = {
            "query": query,
            "observations": [],
            "iteration": 0,
            "completed": False
        }
        
        while state["iteration"] < self.max_iterations and not state["completed"]:
            try:
                reasoning = await self.reason(state)
                
                if reasoning.get("final_answer"):
                    state["final_answer"] = reasoning["final_answer"]
                    state["completed"] = True
                    break
                
                state["current_action"] = reasoning["action"]
                result = await self.act(reasoning["action"], reasoning["action_input"])
                
                state = self.observe(state, result)
                state["iteration"] += 1
                
            except Exception as e:
                self.logger.error(f"ReAct iteration {state['iteration']} failed: {e}")
                state["error"] = str(e)
                break
        
        return state
    
    def _format_tools(self) -> str:
        """Format available tools for prompt"""
        return "\n".join([
            f"- {name}: {tool.description}"
            for name, tool in self.tools.items()
        ])
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        lines = response.strip().split("\n")
        result = {}
        
        for line in lines:
            if line.startswith("Thought:"):
                result["thought"] = line.replace("Thought:", "").strip()
            elif line.startswith("Action:"):
                result["action"] = line.replace("Action:", "").strip()
            elif line.startswith("Action Input:"):
                result["action_input"] = line.replace("Action Input:", "").strip()
            elif line.startswith("Final Answer:"):
                result["final_answer"] = line.replace("Final Answer:", "").strip()
        
        return result
