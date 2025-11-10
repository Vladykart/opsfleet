import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.bigquery_runner import BigQueryRunner
import pandas as pd


@pytest.fixture
def mock_bigquery_client():
    with patch('src.bigquery_runner.bigquery.Client') as mock_client:
        yield mock_client


def test_bigquery_runner_initialization(mock_bigquery_client):
    runner = BigQueryRunner(project_id="test-project", dataset_id="test-dataset")
    
    assert runner.dataset_id == "test-dataset"
    mock_bigquery_client.assert_called_once_with(project="test-project")


def test_execute_query_success(mock_bigquery_client):
    mock_instance = mock_bigquery_client.return_value
    mock_job = Mock()
    mock_result = Mock()
    
    mock_df = pd.DataFrame({"col1": [1, 2, 3], "col2": ["a", "b", "c"]})
    mock_result.to_dataframe.return_value = mock_df
    mock_job.result.return_value = mock_result
    mock_instance.query.return_value = mock_job
    
    runner = BigQueryRunner(project_id="test-project")
    result = runner.execute_query("SELECT * FROM table")
    
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 3
    mock_instance.query.assert_called_once()


def test_get_table_schema(mock_bigquery_client):
    mock_instance = mock_bigquery_client.return_value
    mock_table = Mock()
    
    mock_field1 = Mock()
    mock_field1.name = "id"
    mock_field1.field_type = "INTEGER"
    mock_field1.mode = "REQUIRED"
    mock_field1.description = "User ID"
    
    mock_field2 = Mock()
    mock_field2.name = "name"
    mock_field2.field_type = "STRING"
    mock_field2.mode = "NULLABLE"
    mock_field2.description = None
    
    mock_table.schema = [mock_field1, mock_field2]
    mock_instance.get_table.return_value = mock_table
    
    runner = BigQueryRunner(project_id="test-project", dataset_id="test-dataset")
    schema = runner.get_table_schema("users")
    
    assert len(schema) == 2
    assert schema[0]["name"] == "id"
    assert schema[0]["type"] == "INTEGER"
    assert schema[1]["name"] == "name"
    assert schema[1]["description"] == ""


def test_execute_query_failure(mock_bigquery_client):
    mock_instance = mock_bigquery_client.return_value
    mock_instance.query.side_effect = Exception("Query failed")
    
    runner = BigQueryRunner(project_id="test-project")
    
    with pytest.raises(Exception) as exc_info:
        runner.execute_query("INVALID SQL")
    
    assert "Query failed" in str(exc_info.value)


def test_get_query_stats(mock_bigquery_client):
    mock_instance = mock_bigquery_client.return_value
    mock_job = Mock()
    mock_job.total_bytes_processed = 1024 * 1024 * 100
    mock_job.total_bytes_billed = 1024 * 1024 * 100
    mock_instance.query.return_value = mock_job
    
    runner = BigQueryRunner(project_id="test-project")
    stats = runner.get_query_stats("SELECT * FROM table")
    
    assert "total_bytes_processed" in stats
    assert "estimated_cost_usd" in stats
    assert stats["total_bytes_processed"] == 1024 * 1024 * 100


@pytest.mark.asyncio
async def test_data_analysis_agent_initialization():
    from src.agents.data_analysis_agent import DataAnalysisAgent
    
    config = {
        "bigquery": {
            "dataset": "test-dataset"
        },
        "llm": {
            "primary": {
                "provider": "google",
                "model": "gemini-1.5-pro"
            }
        }
    }
    
    with patch.dict(os.environ, {"GCP_PROJECT_ID": "test-project"}):
        with patch('src.agents.data_analysis_agent.BigQueryRunner'):
            agent = DataAnalysisAgent(config)
            await agent.initialize()
            
            assert agent.bq_runner is not None
