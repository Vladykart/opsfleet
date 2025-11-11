"""BigQuery client and query operations.

This module handles all BigQuery-related operations including
client creation, query execution, and schema analysis.
"""
from __future__ import annotations

import os
from pathlib import Path
from dataclasses import dataclass

from google.cloud import bigquery
from google.oauth2 import service_account
from langchain_core.tools import tool
from dotenv import load_dotenv

from schema_analyzer import get_schema_info, get_relationships


@dataclass(frozen=True)
class BigQueryConfig:
    """BigQuery client configuration."""
    project_id: str | None
    credentials_path: Path | None

    @classmethod
    def from_env(cls) -> BigQueryConfig:
        """Load BigQuery configuration from environment variables.
        
        Returns:
            BigQueryConfig instance with loaded settings
        """
        load_dotenv()
        
        creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        return cls(
            project_id=os.getenv("GCP_PROJECT_ID"),
            credentials_path=Path(creds_path) if creds_path else None
        )


def create_bigquery_client(config: BigQueryConfig | None = None) -> bigquery.Client:
    """Create BigQuery client with appropriate credentials.
    
    Args:
        config: Optional BigQuery configuration. If None, loads from environment.
        
    Returns:
        Configured BigQuery client
    """
    cfg = config or BigQueryConfig.from_env()
    
    match cfg.credentials_path:
        case Path() as path if path.exists():
            credentials = service_account.Credentials.from_service_account_file(str(path))
            return bigquery.Client(project=cfg.project_id, credentials=credentials)
        case _:
            # Use Application Default Credentials
            return bigquery.Client(project=cfg.project_id)


# Initialize default client
_default_client = create_bigquery_client()


@tool
def query_bigquery(sql: str) -> str:
    """Execute a BigQuery SQL query and return results.
    
    Args:
        sql: The SQL query to execute
        
    Returns:
        Query results as formatted string
    """
    try:
        query_job = _default_client.query(sql)
        rows = [dict(row) for row in query_job.result()]
        
        match rows:
            case []:
                return "Query executed successfully but returned no results."
            case [*results]:
                # Return first 10 rows
                return str(results[:10])
    except Exception as e:
        return f"Error executing query: {str(e)}"


@tool
def analyze_schema(table_name: str | None = None) -> str:
    """Analyze database schema and return detailed information.
    
    Args:
        table_name: Optional table name to analyze. If None, returns summary of all tables.
        
    Returns:
        Schema analysis as formatted string
    """
    try:
        match table_name:
            case str() as name:
                # Analyze specific table
                analysis = get_schema_info(name)
                
                result = f"""
📋 Table: {analysis['table_name']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Statistics:
  • Rows: {analysis['row_count']:,}
  • Size: {analysis['size_mb']} MB
  • Columns: {analysis['column_count']}

📝 Columns:
"""
                for col in analysis['columns']:
                    result += f"  • {col['name']} ({col['type']}) - {col['description']}\n"
                
                # Add relationships
                relationships = get_relationships()
                if name in relationships:
                    result += "\n🔗 Relationships:\n"
                    for rel in relationships[name]:
                        result += f"  → {rel}\n"
                
                return result
            
            case None:
                # Return summary of all tables
                summary = get_schema_info()
                result = f"""
📊 Database Summary: {summary['dataset']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  • Tables: {summary['table_count']}
  • Total Rows: {summary['total_rows']:,}
  • Total Size: {summary['total_size_mb']} MB

📋 Tables:
"""
                for table, info in summary['tables'].items():
                    result += f"  • {table}: {info['rows']:,} rows, {info['columns']} columns, {info['size_mb']} MB\n"
                
                return result
            
    except Exception as e:
        return f"Error analyzing schema: {str(e)}"
