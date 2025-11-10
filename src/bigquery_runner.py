import logging
from typing import Optional, List, Dict, Any
import pandas as pd
from google.cloud import bigquery


class BigQueryRunner:
    
    def __init__(self, project_id: Optional[str] = None, dataset_id: Optional[str] = "bigquery-public-data.thelook_ecommerce") -> None:
        logging.info("Initializing BigQuery client")
        try:
            self.client = bigquery.Client(project=project_id)
            self.dataset_id = dataset_id
            logging.info(f"BigQuery client initialized for dataset: {self.dataset_id}")
        except Exception as e:
            logging.error(f"Failed to initialize BigQuery client: {str(e)}")
            raise
    
    def execute_query(self, sql_query: str) -> pd.DataFrame:
        try:
            logging.info(f"Executing BigQuery query")
            query_job = self.client.query(sql_query)
            df = query_job.result().to_dataframe()
            logging.info(f"Query completed successfully, returned {len(df)} rows")
            return df
        except Exception as e:
            logging.error(f"BigQuery execution failed: {str(e)}")
            raise 

    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        try:
            table_ref = f"{self.dataset_id}.{table_name}"
            table = self.client.get_table(table_ref)
            schema_info = []
            for field in table.schema:
                schema_info.append({
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode,
                    "description": field.description or ""
                })
            logging.info(f"Retrieved schema for table {table_name}")
            return schema_info
        except Exception as e:
            logging.error(f"Failed to get schema for table {table_name}: {str(e)}")
            raise

    def list_tables(self) -> List[str]:
        try:
            dataset_ref = self.dataset_id.split('.')[-1]
            project_dataset = self.dataset_id.split('.')[0] if '.' in self.dataset_id else None
            
            if project_dataset:
                dataset = self.client.get_dataset(f"{project_dataset}.{dataset_ref}")
            else:
                dataset = self.client.get_dataset(dataset_ref)
            
            tables = list(self.client.list_tables(dataset))
            table_names = [table.table_id for table in tables]
            logging.info(f"Found {len(table_names)} tables in dataset")
            return table_names
        except Exception as e:
            logging.error(f"Failed to list tables: {str(e)}")
            raise

    def get_query_stats(self, sql_query: str) -> Dict[str, Any]:
        try:
            job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
            query_job = self.client.query(sql_query, job_config=job_config)
            
            return {
                "total_bytes_processed": query_job.total_bytes_processed,
                "total_bytes_billed": query_job.total_bytes_billed,
                "estimated_cost_usd": (query_job.total_bytes_billed / (1024**4)) * 5.0
            }
        except Exception as e:
            logging.error(f"Failed to get query stats: {str(e)}")
            return {}
