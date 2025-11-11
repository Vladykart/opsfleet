"""Tests for agent.py module."""
from __future__ import annotations

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from agent import (
    Config,
    _extract_content,
    load_prompt,
    run_agent,
    AgentState
)


class TestConfig:
    """Test Config dataclass."""
    
    def test_config_from_env(self):
        """Test loading config from environment."""
        with patch.dict('os.environ', {
            'LANGCHAIN_TRACING_V2': 'true',
            'LANGCHAIN_PROJECT': 'test-project'
        }):
            config = Config.from_env()
            assert config.langsmith_enabled is True
            assert config.langsmith_project == 'test-project'
    
    def test_config_defaults(self):
        """Test config with default values."""
        with patch.dict('os.environ', {'LANGCHAIN_TRACING_V2': 'false'}, clear=True):
            config = Config.from_env()
            assert config.langsmith_enabled is False
            assert config.langsmith_project == 'opsfleet-agent'


class TestExtractContent:
    """Test _extract_content function."""
    
    def test_extract_string_content(self):
        """Test extracting string content."""
        result = _extract_content("Hello, world!")
        assert result == "Hello, world!"
    
    def test_extract_list_content_with_dicts(self):
        """Test extracting content from list of dicts."""
        content = [
            {"text": "Hello"},
            {"text": "World"}
        ]
        result = _extract_content(content)
        assert result == "Hello\nWorld"
    
    def test_extract_list_content_with_strings(self):
        """Test extracting content from list of strings."""
        content = ["Hello", "World"]
        result = _extract_content(content)
        assert result == "Hello\nWorld"
    
    def test_extract_empty_list(self):
        """Test extracting from empty list."""
        result = _extract_content([])
        assert result == "No response generated"
    
    def test_extract_none_content(self):
        """Test extracting None content."""
        result = _extract_content(None)
        assert result == "No response generated"


class TestLoadPrompt:
    """Test load_prompt function."""
    
    def test_load_prompt_formats_query(self):
        """Test that load_prompt formats the query correctly."""
        query = "How many users?"
        result = load_prompt(query)
        
        assert "How many users?" in result
        assert "BigQuery" in result
        assert "e-commerce" in result
    
    def test_load_prompt_file_exists(self):
        """Test that prompt file exists."""
        prompt_path = Path(__file__).parent.parent / "prompts" / "system_prompt.txt"
        assert prompt_path.exists()


class TestRunAgent:
    """Test run_agent function."""
    
    @patch('agent.app')
    @patch('agent.load_prompt')
    def test_run_agent_returns_string(self, mock_load_prompt, mock_app):
        """Test that run_agent returns a string response."""
        from langchain_core.messages import AIMessage
        
        mock_load_prompt.return_value = "test prompt"
        mock_message = AIMessage(content="Test response")
        
        mock_app.invoke.return_value = {
            "messages": [mock_message]
        }
        
        result = run_agent("test query")
        assert isinstance(result, str)
        assert result == "Test response"
    
    @patch('agent.app')
    @patch('agent.load_prompt')
    def test_run_agent_handles_list_content(self, mock_load_prompt, mock_app):
        """Test that run_agent handles list content."""
        from langchain_core.messages import AIMessage
        
        mock_load_prompt.return_value = "test prompt"
        mock_message = AIMessage(content=[{"text": "Response 1"}, {"text": "Response 2"}])
        
        mock_app.invoke.return_value = {
            "messages": [mock_message]
        }
        
        result = run_agent("test query")
        assert "Response 1" in result
        assert "Response 2" in result


class TestAgentState:
    """Test AgentState TypedDict."""
    
    def test_agent_state_structure(self):
        """Test AgentState has correct structure."""
        from langchain_core.messages import HumanMessage
        
        state: AgentState = {
            "messages": [HumanMessage(content="test")]
        }
        
        assert "messages" in state
        assert len(state["messages"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
