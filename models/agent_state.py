from typing import TypedDict, List, Optional, Dict, Any
import pandas as pd
from datetime import datetime


class AgentState(TypedDict):
    
    user_query: str
    timestamp: datetime
    session_id: str
    
    conversation_history: List[Dict[str, str]]
    retrieved_context: List[Dict[str, Any]]
    persona_config: Dict[str, Any]
    
    analysis_type: Optional[str]
    required_tables: List[str]
    query_plan: Optional[Dict[str, Any]]
    
    generated_sql: List[str]
    sql_metadata: Dict[str, Any]
    
    query_results: List[pd.DataFrame]
    execution_stats: Dict[str, Any]
    
    analysis_results: Dict[str, Any]
    key_metrics: Dict[str, float]
    insights: List[str]
    
    validation_status: bool
    validation_errors: List[str]
    
    report: Optional[str]
    recommendations: List[str]
    
    errors: List[str]
    retry_count: int
    current_step: str


class StateManager:
    
    def __init__(self):
        self.state_history: List[AgentState] = []
        
    def update_state(self, current_state: AgentState, updates: Dict) -> AgentState:
        new_state = {**current_state, **updates}
        self.state_history.append(new_state)
        return new_state
    
    def get_current_step(self, state: AgentState) -> str:
        return state.get("current_step", "init")
    
    def rollback(self, steps: int = 1) -> AgentState:
        if len(self.state_history) > steps:
            return self.state_history[-(steps + 1)]
        return self.state_history[0]
    
    def checkpoint(self, state: AgentState, checkpoint_name: str):
        pass
