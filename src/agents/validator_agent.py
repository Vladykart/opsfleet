from src.agents.base_agent import BaseAgent
from utils.validation_utils import validate_dataframe, validate_query_results
from typing import Dict, List, Any
import pandas as pd


class ValidatorAgent(BaseAgent):
    
    async def validate_results(self, results: List[pd.DataFrame]) -> Dict:
        validation_report = validate_query_results(results)
        
        validation_report["status"] = validation_report["failed"] == 0
        
        return validation_report
    
    async def validate_sql(self, sql_queries: List[str]) -> Dict:
        from utils.validation_utils import validate_sql
        
        validation_report = {
            "total_queries": len(sql_queries),
            "valid": 0,
            "invalid": 0,
            "errors": []
        }
        
        for idx, sql in enumerate(sql_queries):
            is_valid, errors = validate_sql(sql)
            
            if is_valid:
                validation_report["valid"] += 1
            else:
                validation_report["invalid"] += 1
                validation_report["errors"].extend([
                    f"SQL {idx}: {error}" for error in errors
                ])
        
        validation_report["status"] = validation_report["invalid"] == 0
        
        return validation_report
    
    async def validate_state(self, state: Dict[str, Any]) -> Dict:
        errors = []
        warnings = []
        
        if not state.get("user_query"):
            errors.append("Missing user_query in state")
        
        if state.get("current_step") == "execute_query":
            if not state.get("generated_sql"):
                errors.append("No SQL queries generated")
        
        if state.get("current_step") == "analyze_data":
            if not state.get("query_results"):
                errors.append("No query results available")
        
        return {
            "status": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        validation = await self.validate_state(state)
        
        return {
            "validation_status": validation["status"],
            "validation_errors": validation["errors"]
        }
