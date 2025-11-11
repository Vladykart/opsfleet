"""
Genius-level strategic planner with multi-phase reasoning
"""
import json
from typing import Dict, Any
from langsmith import traceable


class GeniusPlanner:
    """Advanced planner with strategic reasoning and optimization"""
    
    def __init__(self, llm, tools, logger):
        self.llm = llm
        self.tools = tools
        self.logger = logger
    
    @traceable(name="genius_planning")
    async def create_genius_plan(
        self,
        query: str,
        understanding: Dict[str, Any],
        progress_callback=None
    ) -> Dict[str, Any]:
        """Create optimized plan using multi-phase reasoning"""
        
        if progress_callback:
            progress_callback("planning", "running", "Strategic analysis...")
        
        # Phase 1: Strategic Analysis
        strategic_analysis = await self._strategic_analysis(query, understanding)
        
        if progress_callback:
            progress_callback("planning", "running", "Decomposing problem...")
        
        # Phase 2: Problem Decomposition
        decomposition = await self._problem_decomposition(query, understanding, strategic_analysis)
        
        if progress_callback:
            progress_callback("planning", "running", "Optimizing execution...")
        
        # Phase 3: Execution Optimization
        optimized_plan = await self._optimize_execution(decomposition)
        
        if progress_callback:
            progress_callback("planning", "running", "Validating plan...")
        
        # Phase 4: Validation & Risk Assessment
        validated_plan = await self._validate_plan(optimized_plan, understanding)
        
        self.logger.info(f"🧠 Genius plan: {len(validated_plan['steps'])} steps, score: {validated_plan.get('complexity_score', 0.8)}")
        return validated_plan
    
    async def _strategic_analysis(self, query: str, understanding: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 1: High-level strategic thinking"""
        
        prompt = f"""You are a genius strategist. Analyze this data query strategically.

QUERY: {query}
INTENT: {understanding.get('intent', 'unknown')}
COMPLEXITY: {understanding.get('complexity', 'medium')}

THINK STRATEGICALLY:

1. ULTIMATE GOAL
   What is the real objective? What insight do we seek?

2. DATA STRATEGY
   Which tables? What joins? Filter early or late?

3. COMPUTATIONAL APPROACH
   One big query or multiple steps? Sequential or parallel?

4. RISKS & OPPORTUNITIES
   What could fail? How to optimize?

Output JSON:
{{
    "ultimate_goal": "clear objective",
    "key_insights": ["insight 1", "insight 2"],
    "data_strategy": "approach description",
    "computational_approach": "sequential/parallel",
    "risks": ["risk 1"],
    "optimizations": ["opt 1"]
}}
"""
        
        response = await self.llm._call_llm(prompt, temperature=0.3, max_tokens=600)
        return self._extract_json(response, {
            "ultimate_goal": "Execute query",
            "key_insights": ["data"],
            "data_strategy": "direct",
            "computational_approach": "sequential",
            "risks": [],
            "optimizations": []
        })
    
    async def _problem_decomposition(
        self,
        query: str,
        understanding: Dict[str, Any],
        strategic: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phase 2: Break into atomic steps"""
        
        tools_str = self._format_tools()
        
        prompt = f"""Break this task into ATOMIC steps. Each step = ONE action.

QUERY: {query}
GOAL: {strategic.get('ultimate_goal', 'unknown')}
APPROACH: {strategic.get('computational_approach', 'sequential')}

TOOLS AVAILABLE:
{tools_str}

PRINCIPLES:
- Each step does ONE thing
- Minimize dependencies
- Filter early, aggregate late
- Mark critical steps

Output JSON:
{{
    "atomic_steps": [
        {{
            "step_id": 1,
            "action": "bigquery",
            "purpose": "why needed",
            "description": "what it does",
            "depends_on": [],
            "critical": true,
            "estimated_ms": 1000
        }}
    ],
    "critical_path": [1],
    "total_time_ms": 1000
}}

ACTION must be: bigquery, analyze, or report
"""
        
        response = await self.llm._call_llm(prompt, temperature=0.2, max_tokens=800)
        return self._extract_json(response, {
            "atomic_steps": [{
                "step_id": 1,
                "action": "bigquery",
                "purpose": "fetch data",
                "description": "Execute query",
                "depends_on": [],
                "critical": True,
                "estimated_ms": 2000
            }],
            "critical_path": [1],
            "total_time_ms": 2000
        })
    
    async def _optimize_execution(self, decomposition: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 3: Optimize for performance"""
        
        steps = decomposition.get('atomic_steps', [])
        
        prompt = f"""Optimize this execution plan for maximum efficiency.

STEPS:
{json.dumps(steps, indent=2)}

OPTIMIZE FOR:
1. Combine queries where possible
2. Use CTEs for complex logic
3. Parallelize independent steps
4. Minimize data movement

Output OPTIMIZED JSON:
{{
    "steps": [
        {{
            "id": 1,
            "action": "bigquery",
            "description": "detailed description",
            "expected_output": "what this produces",
            "critical": true,
            "reasoning": "why this order",
            "optimization": "what was optimized"
        }}
    ],
    "strategy": "sequential/parallel",
    "estimated_time": "30 seconds",
    "performance_score": 0.95
}}

ACTION must be: bigquery, analyze, or report
"""
        
        response = await self.llm._call_llm(prompt, temperature=0.2, max_tokens=800)
        return self._extract_json(response, {
            "steps": [{
                "id": 1,
                "action": "bigquery",
                "description": "Execute query",
                "expected_output": "results",
                "critical": True,
                "reasoning": "data fetch",
                "optimization": "none"
            }],
            "strategy": "sequential",
            "estimated_time": "1 minute",
            "performance_score": 0.8
        })
    
    async def _validate_plan(
        self,
        optimized: Dict[str, Any],
        understanding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phase 4: Validate and assess risks"""
        
        prompt = f"""Validate this plan. Check completeness, correctness, robustness.

PLAN:
{json.dumps(optimized, indent=2)}

VALIDATE:
✓ Achieves goal?
✓ Tool names valid? (bigquery/analyze/report)
✓ Execution order logical?
✓ Handles failures?
✓ Optimal approach?

Output VALIDATED JSON:
{{
    "steps": [...validated steps...],
    "estimated_time": "time",
    "risk_level": "low/medium/high",
    "complexity_score": 0.7,
    "confidence": 0.95,
    "issues": ["potential issue"],
    "mitigations": ["how to handle"],
    "success_probability": 0.9
}}
"""
        
        response = await self.llm._call_llm(prompt, temperature=0.1, max_tokens=800)
        validated = self._extract_json(response, optimized)
        
        # Ensure valid structure
        if 'steps' not in validated or not validated['steps']:
            validated = {
                "steps": [{
                    "id": 1,
                    "action": "bigquery",
                    "description": "Execute query",
                    "expected_output": "results",
                    "critical": True
                }],
                "estimated_time": "1 minute",
                "risk_level": "low",
                "complexity_score": 0.5,
                "confidence": 0.8
            }
        
        return validated
    
    def _format_tools(self) -> str:
        """Format available tools"""
        return """- bigquery: Execute SQL queries on BigQuery
- analyze: Perform data analysis
- report: Generate formatted reports"""
    
    def _extract_json(self, text: str, default: Dict[str, Any]) -> Dict[str, Any]:
        """Extract JSON from LLM response"""
        try:
            import re
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            self.logger.warning(f"JSON extraction failed: {e}")
        return default
