"""Tests for endpoints module."""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from endpoints.bigquery_client import (
    BigQueryConfig,
    create_bigquery_client,
    query_bigquery,
    analyze_schema
)


class TestBigQueryConfig:
    """Test BigQueryConfig dataclass."""
    
    def test_config_from_env(self):
        """Test loading config from environment."""
        with patch.dict('os.environ', {
            'GCP_PROJECT_ID': 'test-project',
            'GOOGLE_APPLICATION_CREDENTIALS': '/path/to/creds.json'
        }):
            config = BigQueryConfig.from_env()
            assert config.project_id == 'test-project'
            assert config.credentials_path == Path('/path/to/creds.json')
    
    def test_config_no_credentials(self):
        """Test config without credentials path."""
        with patch.dict('os.environ', {'GCP_PROJECT_ID': 'test-project'}, clear=True):
            config = BigQueryConfig.from_env()
            assert config.project_id == 'test-project'
            assert config.credentials_path is None


class TestCreateBigQueryClient:
    """Test create_bigquery_client function."""
    
    @patch('endpoints.bigquery_client.bigquery.Client')
    def test_create_client_with_adc(self, mock_client):
        """Test creating client with ADC."""
        config = BigQueryConfig(project_id='test-project', credentials_path=None)
        
        client = create_bigquery_client(config)
        
        mock_client.assert_called_once_with(project='test-project')
    
    @patch('endpoints.bigquery_client.bigquery.Client')
    @patch('endpoints.bigquery_client.service_account.Credentials')
    def test_create_client_with_credentials(self, mock_creds, mock_client):
        """Test creating client with service account credentials."""
        creds_path = Path('/tmp/test_creds.json')
        config = BigQueryConfig(project_id='test-project', credentials_path=creds_path)
        
        with patch.object(Path, 'exists', return_value=True):
            client = create_bigquery_client(config)
            
            mock_creds.from_service_account_file.assert_called_once()


class TestQueryBigQuery:
    """Test query_bigquery tool."""
    
    @patch('endpoints.bigquery_client._default_client')
    def test_query_success(self, mock_client):
        """Test successful query execution."""
        mock_job = Mock()
        mock_job.result.return_value = [
            {'name': 'Alice', 'age': 30},
            {'name': 'Bob', 'age': 25}
        ]
        mock_client.query.return_value = mock_job
        
        result = query_bigquery.invoke({"sql": "SELECT * FROM users"})
        
        assert isinstance(result, str)
        assert 'Alice' in result or 'Bob' in result
    
    @patch('endpoints.bigquery_client._default_client')
    def test_query_empty_result(self, mock_client):
        """Test query with empty result."""
        mock_job = Mock()
        mock_job.result.return_value = []
        mock_client.query.return_value = mock_job
        
        result = query_bigquery.invoke({"sql": "SELECT * FROM users WHERE 1=0"})
        
        assert "no results" in result.lower()
    
    @patch('endpoints.bigquery_client._default_client')
    def test_query_error(self, mock_client):
        """Test query execution error."""
        mock_client.query.side_effect = Exception("Query failed")
        
        result = query_bigquery.invoke({"sql": "INVALID SQL"})
        
        assert "Error" in result
        assert "Query failed" in result


class TestAnalyzeSchema:
    """Test analyze_schema tool."""
    
    @patch('endpoints.bigquery_client.get_schema_info')
    @patch('endpoints.bigquery_client.get_relationships')
    def test_analyze_specific_table(self, mock_relationships, mock_schema):
        """Test analyzing a specific table."""
        mock_schema.return_value = {
            'table_name': 'users',
            'row_count': 1000,
            'size_mb': 10.5,
            'column_count': 5,
            'columns': [
                {'name': 'id', 'type': 'INTEGER', 'description': 'User ID'},
                {'name': 'name', 'type': 'STRING', 'description': 'User name'}
            ]
        }
        mock_relationships.return_value = {}
        
        result = analyze_schema.invoke({"table_name": "users"})
        
        assert "users" in result
        assert "1,000" in result
        assert "10.5" in result
    
    @patch('endpoints.bigquery_client.get_schema_info')
    def test_analyze_all_tables(self, mock_schema):
        """Test analyzing all tables (summary)."""
        mock_schema.return_value = {
            'dataset': 'test_dataset',
            'table_count': 3,
            'total_rows': 5000,
            'total_size_mb': 50.0,
            'tables': {
                'users': {'rows': 1000, 'columns': 5, 'size_mb': 10.0},
                'orders': {'rows': 2000, 'columns': 8, 'size_mb': 20.0}
            }
        }
        
        result = analyze_schema.invoke({"table_name": None})
        
        assert "test_dataset" in result
        assert "3" in result
        assert "5,000" in result
    
    @patch('endpoints.bigquery_client.get_schema_info')
    def test_analyze_schema_error(self, mock_schema):
        """Test schema analysis error."""
        mock_schema.side_effect = Exception("Schema error")
        
        result = analyze_schema.invoke({"table_name": "invalid_table"})
        
        assert "Error" in result
        assert "Schema error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
