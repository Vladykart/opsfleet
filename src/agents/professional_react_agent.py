from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from langsmith import traceable
import json
import pandas as pd
import re
import logging
from typing import Any, Dict, List
from datetime import datetime
from pandas import Timestamp  # For JSON serialization

class ConversationMemory:
    """Long-term conversation memory for the agent"""
    
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self.short_term = []
        self.long_term = []
        self.context_summary = ""
        
    def add_interaction(self, interaction: Dict[str, Any]):
        """Add interaction to memory"""
        self.short_term.append(interaction)
        
        if len(self.short_term) > 10:
            self._consolidate_to_long_term()
    
    def _consolidate_to_long_term(self):
        """Move old interactions to long-term memory"""
        if len(self.short_term) > 5:
            to_consolidate = self.short_term[:5]
            self.long_term.extend(to_consolidate)
            self.short_term = self.short_term[5:]
            
            if len(self.long_term) > self.max_history:
                self.long_term = self.long_term[-self.max_history:]
    
    def get_context(self) -> str:
        """Get relevant context for current conversation"""
        context_parts = []
        
        if self.context_summary:
            context_parts.append(f"Previous context: {self.context_summary}")
        
        if self.short_term:
            context_parts.append("\nRecent interactions:")
            for interaction in self.short_term[-5:]:
                context_parts.append(
                    f"- User: {interaction.get('query', '')[:100]}"
                )
                context_parts.append(
                    f"  Result: {interaction.get('result', '')[:100]}"
                )
        
        return "\n".join(context_parts)
    
    def update_summary(self, summary: str):
        """Update context summary"""
        self.context_summary = summary


class ProfessionalReActAgent:
    """
    Professional multi-stage ReAct agent with long-term memory.

    Enhanced Stages:
    0. Database Exploration (optional) - Explore schema and data models
    1. Understanding - Analyze user intent and context
    2. Planning - Create execution plan with optimization
    3. Execution - Execute plan with ReAct loop
    4. Validation - Validate results with data quality checks
    5. Interpretation - Interpret results and extract insights
    6. Synthesis - Generate final response
    """
    
    # Class-level schema cache (shared across all instances)
    _shared_schema_cache = None
    
    def __init__(self, tools: List[Any], llm_client: Any, config: Dict[str, Any]):
        self.tools = {tool.name: tool for tool in tools}
        self.llm = llm_client
        
        # Initialize model router for task-specific models
        from src.model_router import ModelRouter
        self.model_router = ModelRouter()
        
        # Track clarification to ensure it only happens once
        self.clarification_given = False
        
        # Thread tracking for LangSmith
        self.thread_id = config.get("thread_id", None)
        self.session_metadata = {}
        if self.thread_id:
            self.session_metadata = {
                "session_id": self.thread_id,
                "thread_id": self.thread_id,
                "conversation_id": self.thread_id
            }
        
        # Initialize conversation cache
        from src.cache.conversation_cache import ConversationCache
        self.cache = ConversationCache(self.thread_id) if self.thread_id else None
        
        # Initialize history storage
        from src.cache.history_db import ConversationHistoryDB
        self.history_db = ConversationHistoryDB(None)  # Pass your DB connection
        self.config = config
        self.memory = ConversationMemory()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Use class-level cache if available
        self.db_schema_cache = ProfessionalReActAgent._shared_schema_cache
        self.enable_db_exploration = config.get("enable_db_exploration", True)
        self.progress_callback = None  # For real-time progress updates
        self.data_samples = {}  # Store data samples for context
        
        if self.db_schema_cache:
            self.logger.info(f"Using cached schema with {len(self.db_schema_cache.get('tables', []))} tables")
        
    @traceable(name="professional_react_agent")
    async def process(self, query: str) -> Dict[str, Any]:
        """Main processing pipeline with real-time progress"""
        
        self.logger.info(f"Processing query: {query[:100]}...")
        
        # Set LangSmith metadata for thread tracking
        import langsmith as ls
        if self.thread_id:
            try:
                run_tree = ls.get_current_run_tree()
                if run_tree:
                    if not hasattr(run_tree, 'extra') or run_tree.extra is None:
                        run_tree.extra = {}
                    if 'metadata' not in run_tree.extra:
                        run_tree.extra['metadata'] = {}
                    run_tree.extra['metadata'].update(self.session_metadata)
                    self.logger.info(f"Set thread metadata: {self.thread_id}")
            except Exception as e:
                self.logger.warning(f"Failed to set thread metadata: {e}")
        
        try:
            stage_0 = None
            if self.enable_db_exploration and not self.db_schema_cache:
                if self.progress_callback:
                    self.progress_callback("db_exploration", "running", "Exploring schema...")
                stage_0 = await self._stage_0_db_exploration()
                if self.progress_callback:
                    self.progress_callback("db_exploration", "complete", f"Cached {len(stage_0['tables'])} tables")
            elif self.db_schema_cache and self.progress_callback:
                # Schema already cached, skip exploration
                self.progress_callback("db_exploration", "complete", f"Using cached schema ({len(self.db_schema_cache['tables'])} tables)")
            
            if self.progress_callback:
                self.progress_callback("understanding", "running", "Analyzing intent...")
            stage_1 = await self._stage_1_understanding(query)
            if self.progress_callback:
                self.progress_callback("understanding", "complete", f"{stage_1.get('intent', 'N/A')}")
            
            # Only ask for clarification once per session
            if stage_1.get("needs_clarification", False) and not self.clarification_given:
                self.clarification_given = True
                clarification_response = self._generate_clarification_response(stage_1)
                return {
                    "success": True,
                    "needs_clarification": True,
                    "clarification_note": "Will proceed with best interpretation",
                    "query": query,
                    "understanding": stage_1,
                    "response": clarification_response,
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat()
                }
            
            if not stage_1.get("is_data_query", True):
                return {
                    "success": True,
                    "query": query,
                    "understanding": stage_1,
                    "response": "This doesn't appear to be a data analysis query. Please ask about products, orders, customers, or sales data.",
                    "session_id": self.session_id,
                    "timestamp": datetime.now().isoformat()
                }
            
            if self.progress_callback:
                self.progress_callback("planning", "running", "Creating plan...")
            stage_2 = await self._stage_2_planning(query, stage_1)
            if self.progress_callback:
                self.progress_callback("planning", "complete", f"{len(stage_2['steps'])} step(s)")
            
            if self.progress_callback:
                self.progress_callback("execution", "running", "Executing...")
            stage_3 = await self._stage_3_execution(query, stage_2)
            if self.progress_callback:
                self.progress_callback("execution", "complete", f"{stage_3['completed_steps']} completed")
            
            if self.progress_callback:
                self.progress_callback("validation", "running", "Validating...")
            stage_4 = await self._stage_4_validation(stage_3)
            if self.progress_callback:
                self.progress_callback("validation", "complete", f"Confidence: {stage_4.get('confidence', 0):.0%}")
            
            if self.progress_callback:
                self.progress_callback("interpretation", "running", "Extracting insights...")
            stage_5 = await self._stage_5_interpretation(query, stage_3, stage_4)
            if self.progress_callback:
                self.progress_callback("interpretation", "complete", f"{len(stage_5.get('insights', []))} insights")
            
            if self.progress_callback:
                self.progress_callback("synthesis", "running", "Generating response...")
            stage_6 = await self._stage_6_synthesis(query, stage_5)
            if self.progress_callback:
                self.progress_callback("synthesis", "complete", "Done")
            
            self._update_memory(query, stage_6)
            
            return {
                "success": True,
                "query": query,
                "db_exploration": stage_0,
                "understanding": stage_1,
                "plan": stage_2,
                "execution": stage_3,
                "validation": stage_4,
                "interpretation": stage_5,
                "response": stage_6,
                "session_id": self.session_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    @traceable(name="stage_0_db_exploration")
    async def _stage_0_db_exploration(self) -> Dict[str, Any]:
        """Stage 0: Explore database schema and data models (runs once per session)"""
        
        self.logger.info("Exploring database schema...")
        
        schema_info = {
            "tables": [
                {
                    "name": "products",
                    "full_name": "`bigquery-public-data.thelook_ecommerce.products`",
                    "columns": ["id", "name", "category", "cost", "retail_price", "brand", "department"],
                    "primary_key": "id",
                    "description": "Product catalog with pricing and categorization"
                },
                {
                    "name": "orders",
                    "full_name": "`bigquery-public-data.thelook_ecommerce.orders`",
                    "columns": ["order_id", "user_id", "status", "created_at"],
                    "primary_key": "order_id",
                    "foreign_keys": [{"column": "user_id", "references": "users.id"}],
                    "description": "Customer orders with status and timestamps. NOTE: created_at is TIMESTAMP, no order_date or num_of_item columns"
                },
                {
                    "name": "order_items",
                    "full_name": "`bigquery-public-data.thelook_ecommerce.order_items`",
                    "columns": ["id", "order_id", "product_id", "user_id", "sale_price", "created_at", "status"],
                    "primary_key": "id",
                    "foreign_keys": [
                        {"column": "order_id", "references": "orders.order_id"},
                        {"column": "product_id", "references": "products.id"},
                        {"column": "user_id", "references": "users.id"}
                    ],
                    "description": "Individual items within orders with pricing. NOTE: created_at is TIMESTAMP, no num_of_item column"
                },
                {
                    "name": "users",
                    "full_name": "`bigquery-public-data.thelook_ecommerce.users`",
                    "columns": ["id", "first_name", "last_name", "email", "country", "state", "city", "created_at"],
                    "primary_key": "id",
                    "description": "Customer information and demographics"
                }
            ],
            "relationships": [
                "orders.user_id → users.id",
                "order_items.order_id → orders.order_id",
                "order_items.product_id → products.id",
                "order_items.user_id → users.id"
            ],
            "common_queries": [
                "Product revenue analysis",
                "Customer segmentation",
                "Sales trends over time",
                "Geographic analysis"
            ]
        }
        
        # Save to both instance and class-level cache
        self.db_schema_cache = schema_info
        ProfessionalReActAgent._shared_schema_cache = schema_info
        self.logger.info(f"Schema cached: {len(schema_info['tables'])} tables (persisted)")
        
        return schema_info
    
    @traceable(name="stage_1_understanding")
    async def _stage_1_understanding(self, query: str) -> Dict[str, Any]:
        """Stage 1: Understand user intent and context"""
        
        context = self.memory.get_context()
        
        prompt = f"""You are a professional data analysis assistant for BigQuery e-commerce data.

CONVERSATION CONTEXT:
{context if context else "No previous context"}

CURRENT QUERY:
{query}

AVAILABLE DATA:
- Products (name, category, cost, retail_price)
- Orders (order_id, user_id, status, num_of_item)
- Users (id, country, state, city)
- Order Items (order_id, product_id, sale_price)

Analyze this query carefully:
1. Is it a valid data analysis request? (not just "status", "help", "history", etc.)
2. Is it clear what data/analysis the user wants?
3. What is the primary intent?
4. What clarifications are needed?
5. Does it mention seasons? (spring/summer/fall/winter or season numbers)
6. Does it ask for top/best products per category/group?

CRITICAL: Almost NEVER set "needs_clarification": true!

We have complete schema and data samples. Make reasonable assumptions:
- Use created_at for date columns (it's TIMESTAMP type)
- Use EXTRACT(MONTH FROM created_at) for months
- Use EXTRACT(YEAR FROM created_at) for years  
- Use SUM(sale_price) from order_items for revenue
- Use COUNT(DISTINCT order_id) for order count
- Use current year (2024) if not specified
- Include all statuses unless specified
- For "January" assume current year
- For "average order value" = total revenue / order count

ONLY set "needs_clarification": true if query is literally just "data" or "help"

Output as JSON:
{{
    "is_data_query": true/false,
    "needs_clarification": true/false,
    "intent": "primary goal or 'unclear'",
    "required_info": ["item1", "item2"],
    "complexity": "simple/medium/complex",
    "output_format": "table/chart/report",
    "clarifications_needed": ["question1", "question2"],
    "suggested_queries": ["example1", "example2"]
}}
"""
        
        # Use GPT-OSS for understanding (critical task)
        try:
            understanding_llm = self.model_router.get_llm_for_task("understanding", temperature=0.1)
            response = await understanding_llm.ainvoke(prompt)
            if hasattr(response, 'content'):
                response = response.content
        except:
            response = await self.llm._call_llm(prompt, temperature=0.1)
        
        understanding = self._extract_json(response, {
            "is_data_query": True,
            "needs_clarification": False,
            "clarification_note": "Will proceed with best interpretation",
            "intent": "unclear",
            "required_info": [],
            "complexity": "simple",
            "output_format": "text",
            "clarifications_needed": ["Could you please clarify what data you'd like to analyze?"],
            "suggested_queries": [
                "What are the top 10 products by revenue?",
                "Analyze customer segments by country",
                "Show sales trends for the last quarter"
            ]
        })
        
        self.logger.info(f"Understanding: {understanding.get('intent', 'unclear')}")
        return understanding
    
    @traceable(name="stage_2_planning")
    async def _stage_2_planning(
        self, 
        query: str, 
        understanding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Stage 2: Genius-level strategic planning with data sampling"""
        
        # Phase 0: Sample data to understand formats and types
        if self.progress_callback:
            self.progress_callback("planning", "running", "Sampling data...")
        
        data_samples = await self._sample_data_formats()
        
        # Phase 1: Strategic Analysis
        if self.progress_callback:
            self.progress_callback("planning", "running", "Strategic analysis...")
        
        strategic = await self._strategic_analysis(query, understanding, data_samples)
        
        # Phase 2: Problem Decomposition
        if self.progress_callback:
            self.progress_callback("planning", "running", "Decomposing problem...")
        
        decomposition = await self._problem_decomposition(query, understanding, strategic)
        
        # Phase 3: Optimize Execution
        if self.progress_callback:
            self.progress_callback("planning", "running", "Optimizing execution...")
        
        optimized = await self._optimize_execution(decomposition)
        
        # Phase 4: Validate Plan
        if self.progress_callback:
            self.progress_callback("planning", "running", "Validating plan...")
        
        validated = await self._validate_plan(optimized, understanding)
        
        self.logger.info(f"🧠 Genius plan: {len(validated['steps'])} steps, confidence: {validated.get('confidence', 0.8)}")
        return validated
    
    async def _sample_data_formats(self) -> Dict[str, Any]:
        """Sample data from tables to understand formats and types"""
        
        # Return cached samples if available
        if self.data_samples:
            self.logger.info("Using cached data samples")
            return self.data_samples
        
        samples = {}
        
        for table_info in self.db_schema_cache.get('tables', []):
            table_name = table_info['full_name']
            
            try:
                # Get 3 sample rows to understand data formats
                sample_query = f"SELECT * FROM {table_name} LIMIT 3"
                
                tool = self.tools.get('bigquery')
                if tool:
                    result = await tool.execute(sample_query)
                    
                    if result and 'data' in result:
                        samples[table_info['name']] = {
                            'sample_rows': result['data'][:3],
                            'columns': table_info['columns'],
                            'data_types': self._infer_data_types(result['data'][:3])
                        }
                        self.logger.info(f"Sampled {table_info['name']}: {len(result['data'])} rows")
            except Exception as e:
                self.logger.warning(f"Failed to sample {table_info['name']}: {e}")
        
        # Cache the samples
        self.data_samples = samples
        return samples
    
    def _infer_data_types(self, sample_rows: list) -> Dict[str, str]:
        """Infer data types from sample rows"""
        
        if not sample_rows:
            return {}
        
        types = {}
        first_row = sample_rows[0]
        
        for key, value in first_row.items():
            if value is None:
                types[key] = "NULLABLE"
            elif isinstance(value, bool):
                types[key] = "BOOLEAN"
            elif isinstance(value, int):
                types[key] = "INTEGER"
            elif isinstance(value, float):
                types[key] = "FLOAT"
            elif isinstance(value, str):
                # Check if it looks like a date/timestamp
                if 'date' in key.lower() or 'time' in key.lower() or 'created' in key.lower():
                    types[key] = "TIMESTAMP/DATE"
                else:
                    types[key] = "STRING"
            else:
                types[key] = str(type(value).__name__)
        
        return types
    
    async def _strategic_analysis(
        self,
        query: str,
        understanding: Dict[str, Any],
        data_samples: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phase 1: Strategic analysis with data awareness"""
        
        sample_info = "\n".join([
            f"- {table}: {info.get('data_types', {})}" 
            for table, info in data_samples.items()
        ])
        
        prompt = f"""Strategic analysis of this data query.

QUERY: {query}
INTENT: {understanding.get('intent', 'unknown')}

DATA SAMPLES (actual formats):
{sample_info}

THINK STRATEGICALLY:
1. Ultimate goal?
2. Which tables and columns?
3. Data types to handle (TIMESTAMP, etc)?
4. Sequential or parallel approach?
5. Risks and optimizations?

Output JSON:
{{
    "ultimate_goal": "objective",
    "tables_needed": ["table1"],
    "key_columns": ["col1"],
    "data_handling": "TIMESTAMP casting needed",
    "approach": "sequential",
    "risks": ["risk1"],
    "optimizations": ["opt1"]
}}"""
        
        response = await self.llm._call_llm(prompt, temperature=0.3, max_tokens=600)
        return self._extract_json(response, {
            "ultimate_goal": "Execute query",
            "tables_needed": [],
            "approach": "sequential",
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
        
        prompt = f"""Decompose into atomic steps.

QUERY: {query}
GOAL: {strategic.get('ultimate_goal', 'unknown')}
APPROACH: {strategic.get('approach', 'sequential')}

TOOLS:
{self._format_tools()}

PRINCIPLES:
- Each step = ONE action
- Filter early, aggregate late
- Mark critical steps

CRITICAL: Return ONLY valid JSON, no explanations.

Output JSON:
{{
    "atomic_steps": [
        {{
            "step_id": 1,
            "action": "bigquery",
            "purpose": "why",
            "description": "what",
            "critical": true
        }}
    ]
}}

ACTION must be: bigquery, analyze, or report"""
        
        response = await self.llm._call_llm(prompt, temperature=0.2, max_tokens=800)
        return self._extract_json(response, {
            "atomic_steps": [{
                "step_id": 1,
                "action": "bigquery",
                "purpose": "fetch data",
                "description": "Execute query",
                "critical": True
            }]
        })
    
    async def _optimize_execution(self, decomposition: Dict[str, Any]) -> Dict[str, Any]:
        """Phase 3: Optimize for performance"""
        
        steps = decomposition.get('atomic_steps', [])
        
        prompt = f"""Optimize this plan.

STEPS:
{json.dumps(steps, indent=2)}

OPTIMIZE:
- Combine queries
- Use CTEs
- Minimize data movement

Output JSON:
{{
    "steps": [
        {{
            "id": 1,
            "action": "bigquery",
            "description": "detailed",
            "expected_output": "what",
            "critical": true,
            "reasoning": "why",
            "optimization": "what optimized"
        }}
    ],
    "estimated_time": "30 seconds"
}}

ACTION must be: bigquery, analyze, or report"""
        
        response = await self.llm._call_llm(prompt, temperature=0.2, max_tokens=800)
        return self._extract_json(response, {
            "steps": [{
                "id": 1,
                "action": "bigquery",
                "description": "Execute query",
                "expected_output": "results",
                "critical": True
            }],
            "estimated_time": "1 minute"
        })
    
    async def _validate_plan(
        self,
        optimized: Dict[str, Any],
        understanding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Phase 4: Validate and assess"""
        
        prompt = f"""Validate this plan.

PLAN:
{json.dumps(optimized, indent=2)}

CHECK:
✓ Achieves goal?
✓ Valid tools? (bigquery/analyze/report)
✓ Logical order?
✓ Handles failures?

Output JSON:
{{
    "steps": [...validated...],
    "estimated_time": "time",
    "risk_level": "low",
    "confidence": 0.95,
    "success_probability": 0.9
}}"""
        
        response = await self.llm._call_llm(prompt, temperature=0.1, max_tokens=800)
        validated = self._extract_json(response, optimized)
        
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
                "confidence": 0.8
            }
        
        return validated
    
    @traceable(name="stage_3_execution")
    async def _stage_3_execution(
        self,
        query: str,
        plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Stage 3: Execute plan using ReAct loop (step-by-step)"""
        
        execution_log = []
        results = {}
        total_steps = len(plan['steps'])
        
        for idx, step in enumerate(plan['steps'], 1):
            step_num = f"{idx}/{total_steps}"
            
            # Progress: Starting step
            if self.progress_callback:
                self.progress_callback("execution", "running", f"Step {step_num}: Thinking...")
            
            self.logger.info(f"[Step {step_num}] {step['description']}")
            
            # ReAct: Think
            thought = await self._think(step, results, query)
            self.logger.info(f"[Step {step_num}] Thought: {thought[:100]}...")
            
            # Progress: Acting
            if self.progress_callback:
                self.progress_callback("execution", "running", f"Step {step_num}: Executing {step['action']}...")
            
            # ReAct: Act
            action_result = await self._act(step, thought)
            
            # ReAct: Observe
            observation = self._observe(step, action_result)
            self.logger.info(f"[Step {step_num}] Observation: {observation[:100]}...")
            
            # Log the complete ReAct cycle
            execution_log.append({
                "step_id": step['id'],
                "step_number": f"{idx}/{total_steps}",
                "thought": thought,
                "action": step['action'],
                "observation": observation,
                "status": "success" if action_result else "failed",
                "result_preview": str(action_result)[:200] if action_result else None
            })
            
            results[f"step_{step['id']}"] = action_result
            
            # Progress: Step complete
            if self.progress_callback:
                status = "✓" if action_result else "✗"
                self.progress_callback("execution", "running", f"Step {step_num}: {status} Complete")
            
            # Stop if critical step failed
            if step.get('critical') and not action_result:
                self.logger.error(f"[Step {step_num}] Critical step failed, stopping execution")
                break
        
        return {
            "execution_log": execution_log,
            "results": results,
            "completed_steps": len([log for log in execution_log if log['status'] == 'success']),
            "total_steps": total_steps
        }
    
    @traceable(name="react_think")
    async def _think(
        self,
        step: Dict[str, Any],
        previous_results: Dict[str, Any],
        original_query: str
    ) -> str:
        """ReAct: Think about current step"""
        
        prompt = f"""Think about how to execute this step.

ORIGINAL QUERY: {original_query}

CURRENT STEP:
- Action: {step['action']}
- Description: {step['description']}
- Expected: {step['expected_output']}

PREVIOUS RESULTS:
{json.dumps(previous_results, indent=2) if previous_results else "None"}

Think through:
1. What do I need to do?
2. What information do I have?
3. What tool should I use?
4. What input should I provide?

Provide your reasoning (2-3 sentences).
"""
        
        thought = await self.llm._call_llm(prompt, temperature=0.2, max_tokens=200)
        return thought.strip()
    
    @traceable(name="react_act")
    async def _act(self, step: Dict[str, Any], thought: str) -> Any:
        """ReAct: Execute action with self-healing retry"""
        
        tool_name = step['action']
        
        if tool_name not in self.tools:
            self.logger.warning(f"Tool not found: {tool_name}")
            return None
        
        tool = self.tools[tool_name]
        
        tool_input = await self._prepare_tool_input(step, thought)
        
        max_retries = 2  # Try up to 2 times to fix the query
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                result = await tool.execute(tool_input)
                
                # Check if result has error
                if isinstance(result, dict) and 'error' in result:
                    last_error = result['error']
                    
                    # If this is not the last attempt, try to fix
                    if attempt < max_retries and tool_name == 'bigquery':
                        self.logger.warning(f"Attempt {attempt + 1} failed: {last_error}")
                        
                        # Use ReAct to fix the query
                        fixed_input = await self._react_fix_query(tool_input, last_error, step)
                        if fixed_input and fixed_input != tool_input:
                            self.logger.info(f"Retrying with fixed query (attempt {attempt + 2})")
                            tool_input = fixed_input
                            continue
                    
                    # Last attempt or couldn't fix, return error
                    return result
                
                # Success!
                if attempt > 0:
                    self.logger.info(f"Query succeeded after {attempt + 1} attempts")
                return result
                
            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Tool execution failed (attempt {attempt + 1}): {e}")
                
                # If this is not the last attempt and it's BigQuery, try to fix
                if attempt < max_retries and tool_name == 'bigquery':
                    fixed_input = await self._react_fix_query(tool_input, last_error, step)
                    if fixed_input and fixed_input != tool_input:
                        self.logger.info(f"Retrying with fixed query (attempt {attempt + 2})")
                        tool_input = fixed_input
                        continue
                
                # Last attempt, return error
                if attempt == max_retries:
                    return {"error": last_error}
        
        return {"error": last_error}
    
    @traceable(name="react_fix_query")
    async def _react_fix_query(self, broken_query: str, error: str, step: Dict[str, Any]) -> str:
        """Use ReAct reasoning to fix a broken SQL query"""
        
        self.logger.info("Using ReAct to fix broken query...")
        
        schema_info = ""
        if self.db_schema_cache:
            tables = self.db_schema_cache.get('tables', [])
            schema_info = "\n".join([
                f"- {t['full_name']}: {', '.join(t['columns'])}"
                for t in tables
            ])
        
        prompt = f"""You are a SQL expert. A query failed and you need to fix it.

BROKEN QUERY:
{broken_query}

ERROR MESSAGE:
{error}

AVAILABLE SCHEMA:
{schema_info}

COMMON ISSUES AND FIXES:
1. TIMESTAMP vs DATE comparison:
   - WRONG: WHERE created_at >= '2024-01-01'
   - RIGHT: WHERE CAST(created_at AS DATE) >= DATE('2024-01-01')

2. Column name errors:
   - products table uses "id" not "product_id"
   - users table uses "id" not "user_id"

3. Missing table aliases or wrong JOIN conditions

4. Incorrect aggregation or GROUP BY

TASK: Analyze the error and fix the SQL query.

CRITICAL RULES:
1. Return ONLY the fixed SQL query, nothing else
2. Do not add explanations or markdown
3. Fix the specific error mentioned
4. Use correct column names from schema
5. Handle date/timestamp comparisons correctly

FIXED SQL:"""
        
        try:
            fixed_query = await self.llm._call_llm(prompt, temperature=0.1, max_tokens=500)
            fixed_query = fixed_query.strip()
            
            # Remove markdown if present
            if fixed_query.startswith("```"):
                import re
                match = re.search(r'```(?:sql)?\s*(.*?)\s*```', fixed_query, re.DOTALL)
                if match:
                    fixed_query = match.group(1).strip()
            
            self.logger.info(f"Generated fixed query: {fixed_query[:100]}...")
            return fixed_query
            
        except Exception as e:
            self.logger.error(f"Failed to generate fixed query: {e}")
            return broken_query  # Return original if fix fails
    
    def _observe(self, step: Dict[str, Any], result: Any) -> str:
        """ReAct: Observe action result"""
        
        if not result:
            return "Action failed - no result"
        
        if isinstance(result, dict):
            if "error" in result:
                return f"Error: {result['error']}"
            if "rows" in result:
                return f"Retrieved {result['rows']} rows of data"
            if "data" in result:
                return f"Data processed: {len(result['data'])} items"
        
        return f"Action completed: {str(result)[:100]}"
    
    @traceable(name="stage_4_validation")
    async def _stage_4_validation(self, execution: Dict[str, Any]) -> Dict[str, Any]:
        """Stage 4: Validate execution results with self-healing"""
        
        # Make execution log JSON-safe
        def _make_json_safe_helper(obj):
            """Convert non-JSON-serializable objects to strings"""
            from datetime import datetime
            try:
                from pandas import Timestamp
            except:
                Timestamp = type(None)
            
            try:
                if Timestamp and isinstance(obj, Timestamp):
                    return obj.isoformat()
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: _make_json_safe_helper(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [_make_json_safe_helper(item) for item in obj]
                else:
                    return obj
            except Exception as e:
                return str(obj)  # Fallback to string representation
        
        try:
            safe_log = _make_json_safe_helper(execution['execution_log'])
        except Exception as e:
            self.logger.error(f"Failed to make execution log JSON-safe: {e}")
            # Fallback: use simplified log
            safe_log = [
                {
                    "step_id": log.get("step_id", i),
                    "action": log.get("action", "unknown"),
                    "status": log.get("status", "unknown")
                }
                for i, log in enumerate(execution.get('execution_log', []), 1)
            ]
        
        prompt = f"""Validate the execution results.

EXECUTION LOG:
{json.dumps(safe_log, indent=2)[:2000]}

RESULTS SUMMARY:
- Completed steps: {execution.get('completed_steps', 0)}
- Total steps: {len(execution.get('execution_log', []))}

Validate:
1. Were all critical steps completed?
2. Are results consistent and logical?
3. Are there any errors or anomalies?
4. Is additional analysis needed?

Output as JSON:
{{
    "valid": true/false,
    "confidence": 0.95,
    "issues": [],
    "recommendations": []
}}
"""
        
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                response = await self.llm._call_llm(prompt, temperature=0.1)
                validation = self._extract_json(response, {
                    "valid": execution.get('completed_steps', 0) > 0,
                    "confidence": 0.8,
                    "issues": [],
                    "recommendations": []
                })
                
                # Validate the validation result
                if 'valid' in validation and 'confidence' in validation:
                    self.logger.info(f"Validation: {validation['valid']} (confidence: {validation.get('confidence', 0)})")
                    return validation
                else:
                    if attempt < max_retries:
                        self.logger.warning(f"Invalid validation response (attempt {attempt + 1}), retrying...")
                        continue
                    
            except Exception as e:
                self.logger.error(f"Validation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries:
                    continue
        
        # Fallback validation
        self.logger.warning("Using fallback validation")
        return {
            "valid": execution.get('completed_steps', 0) > 0,
            "confidence": 0.7,
            "issues": ["Validation stage encountered errors"],
            "recommendations": ["Review execution log manually"]
        }
    
    @traceable(name="stage_5_interpretation")
    async def _stage_5_interpretation(
        self,
        query: str,
        execution: Dict[str, Any],
        validation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Stage 5: Interpret results and extract insights"""
        
        # Extract actual data from execution results
        actual_data = []
        columns_info = {}
        
        for step_key, step_data in execution.get('results', {}).items():
            if isinstance(step_data, dict) and 'data' in step_data:
                actual_data = step_data['data'][:10]  # Get first 10 rows
                
                # Inspect columns and data types
                if actual_data and len(actual_data) > 0:
                    first_row = actual_data[0]
                    for col, val in first_row.items():
                        val_type = type(val).__name__
                        columns_info[col] = val_type
                    
                    self.logger.info(f"Data inspection: {len(actual_data)} rows, columns: {list(columns_info.keys())}")
                    self.logger.info(f"Column types: {columns_info}")
                
                break
        
        # Convert results to JSON-safe format (handle Timestamps)
        def _make_json_safe_helper(obj):
            """Convert non-JSON-serializable objects to strings"""
            from datetime import datetime
            try:
                from pandas import Timestamp
            except:
                Timestamp = type(None)
            
            try:
                if Timestamp and isinstance(obj, Timestamp):
                    return obj.isoformat()
                elif isinstance(obj, datetime):
                    return obj.isoformat()
                elif isinstance(obj, dict):
                    return {k: _make_json_safe_helper(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [_make_json_safe_helper(item) for item in obj]
                else:
                    return obj
            except:
                return str(obj)
        
        safe_results = _make_json_safe_helper(execution.get('results', {}))
        results_summary = json.dumps(safe_results, indent=2)[:1000]
        
        prompt = f"""Interpret the data analysis results and extract key insights.

ORIGINAL QUERY: {query}

EXECUTION RESULTS:
{results_summary}

VALIDATION:
- Valid: {validation.get('valid', False)}
- Confidence: {validation.get('confidence', 0)}

Extract and interpret FROM THE ACTUAL DATA:
1. Key metrics and numbers (use EXACT values from data)
2. Patterns and trends (based on actual data)
3. Anomalies or outliers (if present in data)
4. Business implications (derived from real numbers)
5. Actionable insights (based on data patterns)

CRITICAL: Use ONLY the actual data provided. Do NOT make up numbers or insights.

Output as JSON:
{{
    "key_metrics": {{"metric_name": value}},
    "insights": ["insight1", "insight2"],
    "trends": ["trend1", "trend2"],
    "anomalies": ["anomaly1"],
    "business_impact": "description",
    "recommendations": ["rec1", "rec2"]
}}
"""
        
        response = await self.llm._call_llm(prompt, temperature=0.2, max_tokens=400)
        
        interpretation = self._extract_json(response, {
            "key_metrics": {},
            "insights": ["Data analysis completed"],
            "trends": [],
            "anomalies": [],
            "business_impact": "Results provide valuable information for decision making",
            "recommendations": ["Review findings and take appropriate action"]
        })
        
        interpretation['actual_data'] = actual_data  # Add actual data
        self.logger.info(f"Interpretation: {len(interpretation.get('insights', []))} insights extracted")
        return interpretation
    
    @traceable(name="stage_6_synthesis")
    async def _stage_6_synthesis(
        self,
        query: str,
        interpretation: Dict[str, Any]
    ) -> str:
        """Stage 6: Synthesize final response with actual data"""
        
        insights_text = '\n'.join([f"- {insight}" for insight in interpretation.get('insights', [])])
        recommendations_text = '\n'.join([f"- {rec}" for rec in interpretation.get('recommendations', [])])
        
        # Get actual data
        actual_data = interpretation.get('actual_data', [])
        data_text = ""
        if actual_data:
            data_text = "\n\nACTUAL DATA (use these EXACT numbers):\n"
            for i, row in enumerate(actual_data[:5], 1):
                data_text += f"{i}. {row}\n"
        
        prompt = f"""Generate a professional, comprehensive response using ACTUAL DATA.

ORIGINAL QUERY: {query}

KEY INSIGHTS:
{insights_text or "- Analysis completed successfully"}

BUSINESS IMPACT:
{interpretation.get('business_impact', 'Results provide valuable information')}

RECOMMENDATIONS:
{recommendations_text or "- Review findings"}

{data_text}

CRITICAL: If actual data is provided above, use those EXACT numbers in your response.
Do NOT make up or estimate any numbers. Use the real data shown above.

Generate a response that:
1. Directly answers the user's question
2. Provides key insights and findings
3. Includes relevant data points
4. Suggests next steps if applicable
5. Is clear, concise, and professional

Format as a well-structured response with:
- Executive summary
- Key findings (bullet points)
- Detailed analysis
- Recommendations (if applicable)
"""
        
        response = await self.llm._call_llm(prompt, temperature=0.3, max_tokens=1024)
        return response.strip()
    
    async def _prepare_tool_input(self, step: Dict[str, Any], thought: str) -> str:
        """Prepare input for tool based on step and thought"""
        
        tool_name = step.get('action', '')
        
        if tool_name == 'bigquery':
            schema_info = ""
            relationships_info = ""
            query_patterns = ""
            
            if self.db_schema_cache:
                tables = self.db_schema_cache.get('tables', [])
                schema_info = "\n".join([
                    f"- {t['full_name']} ({', '.join(t['columns'])})"
                    for t in tables
                ])
                
                relationships = self.db_schema_cache.get('relationships', [])
                relationships_info = "\n".join([f"  {rel}" for rel in relationships])
                
                common_queries = self.db_schema_cache.get('common_queries', [])
                query_patterns = "\n".join([f"  • {q}" for q in common_queries])
            else:
                schema_info = """- `bigquery-public-data.thelook_ecommerce.products` (id, name, category, cost, retail_price, brand, department)
- `bigquery-public-data.thelook_ecommerce.orders` (order_id, user_id, status, created_at, num_of_item)
- `bigquery-public-data.thelook_ecommerce.order_items` (id, order_id, product_id, user_id, sale_price, created_at)
- `bigquery-public-data.thelook_ecommerce.users` (id, first_name, last_name, email, country, state, city, created_at)"""
                relationships_info = """  orders.user_id → users.id
  order_items.order_id → orders.order_id
  order_items.product_id → products.id
  order_items.user_id → users.id"""
                query_patterns = """  • Product revenue analysis
  • Customer segmentation
  • Sales trends over time
  • Geographic analysis"""
            
            prompt = f"""Generate a BigQuery SQL query.

TASK: {step['description']}
REASONING: {thought}

DATABASE SCHEMA:
{schema_info}

TABLE RELATIONSHIPS:
{relationships_info}

COMMON QUERY PATTERNS (use as reference):
{query_patterns}

CRITICAL COLUMN RULES:
⚠️  products table: Use "id" (NOT product_id)
⚠️  users table: Use "id" (NOT user_id)
⚠️  orders table: Use "created_at" (NOT order_date), columns: order_id, user_id, status, created_at
⚠️  order_items table: columns are id, order_id, product_id, user_id, sale_price, created_at, status (NO num_of_item)
✓  orders table: Has "user_id" FK to users.id
✓  order_items table: Has "product_id" FK to products.id and "user_id" FK to users.id

COLUMNS THAT DO NOT EXIST (will cause errors):
❌ orders.order_date (use orders.created_at)
❌ orders.num_of_item (not in schema)
❌ order_items.num_of_item (not in schema)
❌ order_items.order_date (use order_items.created_at)

QUERY PATTERN EXAMPLES:

1. Product Revenue Analysis:
   SELECT p.name, SUM(oi.sale_price) as revenue
   FROM `bigquery-public-data.thelook_ecommerce.products` p
   JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi ON p.id = oi.product_id
   GROUP BY p.name ORDER BY revenue DESC LIMIT 10

2. Customer Segmentation by Purchase Frequency:
   SELECT u.id, u.country, COUNT(o.order_id) as purchase_count
   FROM `bigquery-public-data.thelook_ecommerce.users` u
   LEFT JOIN `bigquery-public-data.thelook_ecommerce.orders` o ON u.id = o.user_id
   GROUP BY u.id, u.country ORDER BY purchase_count DESC LIMIT 100

3. Geographic Analysis:
   SELECT u.country, COUNT(DISTINCT u.id) as customers, SUM(oi.sale_price) as revenue
   FROM `bigquery-public-data.thelook_ecommerce.users` u
   JOIN `bigquery-public-data.thelook_ecommerce.orders` o ON u.id = o.user_id
   JOIN `bigquery-public-data.thelook_ecommerce.order_items` oi ON o.order_id = oi.order_id
   GROUP BY u.country ORDER BY revenue DESC LIMIT 20

CRITICAL BIGQUERY RULES:
1. DATE/TIME FUNCTIONS:
   - Use EXTRACT(MONTH FROM date) NOT MONTH(date)
   - Use EXTRACT(YEAR FROM date) NOT YEAR(date)
   - Use EXTRACT(DAY FROM date) NOT DAY(date)
   - Example: WHERE EXTRACT(MONTH FROM created_at) = 1

2. TIMESTAMP HANDLING:
   - created_at columns are TIMESTAMP type
   - For date comparisons: CAST(created_at AS DATE) >= DATE('2024-01-01')
   - For year filter: EXTRACT(YEAR FROM created_at) = 2024
   - For month filter: EXTRACT(MONTH FROM created_at) = 1

3. GROUP BY + HAVING:
   - HAVING clause can only reference:
     * Columns in GROUP BY
     * Aggregate functions (COUNT, SUM, MAX, MIN, AVG)
   - Example: GROUP BY month HAVING COUNT(*) > 10
   - Example: GROUP BY EXTRACT(MONTH FROM created_at)

4. COLUMN NAMES:
   - products.id (NOT products.product_id)
   - users.id (NOT users.user_id)
   - orders.user_id (FK to users.id)
   - order_items.product_id (FK to products.id)

5. OUTPUT FORMAT:
   - Return ONLY SQL query
   - NO explanations, NO "Here's", NO markdown
   - Start with SELECT, WITH, or other SQL keyword
   - Use full table names with backticks
   - LIMIT results to 500 rows

NOW GENERATE THE SQL QUERY (SQL only, no text):
"""
        else:
            prompt = f"""Generate the exact input for this tool.

STEP: {step['description']}
TOOL: {tool_name}
REASONING: {thought}

Return ONLY the tool input, no explanations.
"""
        
        tool_input = await self.llm._call_llm(prompt, temperature=0.1, max_tokens=500)
        
        tool_input = tool_input.strip()
        
        if tool_name == 'bigquery':
            import re
            if tool_input.startswith('```'):
                match = re.search(r'```(?:sql)?\s*(.*?)\s*```', tool_input, re.DOTALL)
                if match:
                    tool_input = match.group(1).strip()
            
            if not tool_input.upper().startswith(('SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE', 'CREATE')):
                self.logger.warning(f"Generated text instead of SQL: {tool_input[:50]}")
                tool_input = f"SELECT * FROM `bigquery-public-data.thelook_ecommerce.products` LIMIT 10"
        
        return tool_input
    
    def _format_tools(self) -> str:
        """Format available tools"""
        return "\n".join([
            f"- {name}: {tool.description}"
            for name, tool in self.tools.items()
        ])
    
    def _generate_clarification_response(self, understanding: Dict[str, Any]) -> str:
        """Generate a helpful clarification response"""
        
        clarifications = understanding.get("clarifications_needed", [])
        suggestions = understanding.get("suggested_queries", [])
        
        response = "## I need some clarification\n\n"
        
        if clarifications:
            response += "**Questions:**\n\n"
            for i, clarification in enumerate(clarifications, 1):
                response += f"{i}. {clarification}\n"
            response += "\n"
        
        if suggestions:
            response += "**Here are some example queries you can try:**\n\n"
            for suggestion in suggestions:
                response += f"- {suggestion}\n"
            response += "\n"
        
        response += "**Available data:**\n"
        response += "- Products (name, category, price, cost)\n"
        response += "- Orders (status, items, dates)\n"
        response += "- Customers (country, state, city)\n"
        response += "- Sales (revenue, quantity)\n"
        
        return response
    
    def _extract_json(self, response: str, default: Dict[str, Any]) -> Dict[str, Any]:
        """Extract JSON from LLM response, handling markdown code blocks"""
        import re
        
        # Try 1: Direct JSON parse
        try:
            return json.loads(response.strip())
        except:
            pass
        
        # Try 2: Extract from markdown code block
        try:
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(1))
        except Exception as e:
            self.logger.debug(f"Markdown extraction failed: {e}")
        
        # Try 3: Find first complete JSON object
        try:
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
        except Exception as e:
            self.logger.debug(f"Regex extraction failed: {e}")
        
        # Try 4: Find any JSON-like structure
        try:
            start = response.find('{')
            end = response.rfind('}')
            if start != -1 and end != -1 and end > start:
                json_str = response[start:end+1]
                return json.loads(json_str)
        except Exception as e:
            self.logger.debug(f"Bracket extraction failed: {e}")
        
        self.logger.warning(f"Failed to extract JSON from response (length: {len(response)}), using default")
        if len(response) < 200:
            self.logger.debug(f"Response preview: {response}")
        return default
    
    def _update_memory(self, query: str, response: str):
        """Update conversation memory"""
        self.memory.add_interaction({
            "query": query,
            "result": response[:200] if len(response) > 200 else response,
            "timestamp": datetime.now().isoformat()
        })
