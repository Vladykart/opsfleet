import pandas as pd
from typing import Dict, List, Tuple


def validate_dataframe(df: pd.DataFrame, min_rows: int = 1) -> Tuple[bool, List[str]]:
    errors = []
    
    if df.empty:
        errors.append("DataFrame is empty")
        return False, errors
    
    if len(df) < min_rows:
        errors.append(f"DataFrame has {len(df)} rows, minimum required: {min_rows}")
        return False, errors
    
    null_pct = df.isnull().sum().sum() / df.size if df.size > 0 else 0
    if null_pct > 0.5:
        errors.append(f"High null percentage: {null_pct:.2%}")
        return False, errors
    
    return True, []


def validate_sql(sql: str) -> Tuple[bool, List[str]]:
    errors = []
    
    if not sql or not sql.strip():
        errors.append("SQL query is empty")
        return False, errors
    
    required_keywords = ['SELECT', 'FROM']
    sql_upper = sql.upper()
    
    for keyword in required_keywords:
        if keyword not in sql_upper:
            errors.append(f"Missing required SQL keyword: {keyword}")
    
    if errors:
        return False, errors
    
    return True, []


def validate_query_results(results: List[pd.DataFrame]) -> Dict[str, any]:
    validation_report = {
        "total_queries": len(results),
        "successful": 0,
        "failed": 0,
        "warnings": [],
        "errors": []
    }
    
    for idx, df in enumerate(results):
        is_valid, errors = validate_dataframe(df)
        
        if is_valid:
            validation_report["successful"] += 1
        else:
            validation_report["failed"] += 1
            validation_report["errors"].extend([
                f"Query {idx}: {error}" for error in errors
            ])
    
    return validation_report
