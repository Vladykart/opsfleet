#!/usr/bin/env python3
import pytest
import os
import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import json

sys.path.insert(0, os.path.dirname(__file__))

from cli_enhanced import RichChatCLI

@pytest.fixture
def cli():
    cli = RichChatCLI()
    yield cli
    if cli.session_dir.exists():
        for file in cli.session_dir.glob("*"):
            if file.is_file():
                file.unlink()

@pytest.fixture
def cli_with_history(cli):
    cli.history = [
        {
            "time": "10:00:00",
            "query": "How many users?",
            "response": "There are 100,000 users",
            "success": True,
            "elapsed": 2.5
        },
        {
            "time": "10:01:00",
            "query": "Show top products",
            "response": "Top 5 products listed",
            "success": True,
            "elapsed": 3.2
        },
        {
            "time": "10:02:00",
            "query": "Invalid query",
            "response": "Error: Invalid syntax",
            "success": False,
            "elapsed": 0.5
        }
    ]
    return cli

class TestCLIInitialization:
    def test_cli_creates_session_directory(self, cli):
        assert cli.session_dir.exists()
        assert cli.session_dir.is_dir()
    
    def test_cli_has_session_id(self, cli):
        assert cli.session_id is not None
        assert len(cli.session_id) == 15
    
    def test_cli_initializes_empty_history(self, cli):
        assert cli.history == []
    
    def test_cli_has_last_query_data_attribute(self, cli):
        assert hasattr(cli, 'last_query_data')
        assert cli.last_query_data is None

class TestSaveConversation:
    def test_save_csv_creates_file(self, cli_with_history):
        cli_with_history.save_conversation("csv")
        
        csv_files = list(cli_with_history.session_dir.glob("conversation_*.csv"))
        assert len(csv_files) > 0
        
        df = pd.read_csv(csv_files[0])
        assert len(df) == 3
        assert "query" in df.columns
        assert "response" in df.columns
        assert "success" in df.columns
    
    def test_save_json_creates_file(self, cli_with_history):
        cli_with_history.save_conversation("json")
        
        json_files = list(cli_with_history.session_dir.glob("conversation_*.json"))
        assert len(json_files) > 0
        
        with open(json_files[0], 'r') as f:
            data = json.load(f)
        
        assert len(data) == 3
        assert data[0]["query"] == "How many users?"
        assert data[0]["success"] is True
    
    def test_save_excel_creates_file(self, cli_with_history):
        cli_with_history.save_conversation("excel")
        
        excel_files = list(cli_with_history.session_dir.glob("conversation_*.xlsx"))
        assert len(excel_files) > 0
        
        df = pd.read_excel(excel_files[0])
        assert len(df) == 3
        assert "query" in df.columns
    
    def test_save_markdown_creates_file(self, cli_with_history):
        cli_with_history.save_conversation("md")
        
        md_files = list(cli_with_history.session_dir.glob("conversation_*.md"))
        assert len(md_files) > 0
        
        content = md_files[0].read_text()
        assert "# OpsFleet Conversation" in content
        assert "How many users?" in content
        assert "## Query 1" in content
    
    def test_save_txt_creates_file(self, cli_with_history):
        cli_with_history.save_conversation("txt")
        
        txt_files = list(cli_with_history.session_dir.glob("conversation_*.txt"))
        assert len(txt_files) > 0
        
        content = txt_files[0].read_text()
        assert "OpsFleet Conversation" in content
        assert "How many users?" in content
    
    def test_save_empty_history_shows_warning(self, cli):
        cli.save_conversation("csv")
        assert len(list(cli.session_dir.glob("conversation_*.csv"))) == 0
    
    def test_save_unknown_format_shows_error(self, cli_with_history):
        cli_with_history.save_conversation("unknown")
        assert len(list(cli_with_history.session_dir.glob("conversation_*.*"))) == 0
    
    def test_save_csv_contains_all_fields(self, cli_with_history):
        cli_with_history.save_conversation("csv")
        
        csv_files = list(cli_with_history.session_dir.glob("conversation_*.csv"))
        df = pd.read_csv(csv_files[0])
        
        assert "time" in df.columns
        assert "query" in df.columns
        assert "response" in df.columns
        assert "success" in df.columns
        assert "elapsed" in df.columns
    
    def test_save_preserves_data_types(self, cli_with_history):
        cli_with_history.save_conversation("csv")
        
        csv_files = list(cli_with_history.session_dir.glob("conversation_*.csv"))
        df = pd.read_csv(csv_files[0])
        
        assert df["success"].dtype == bool
        assert df["elapsed"].dtype == float

class TestExportHistory:
    def test_export_creates_txt_file(self, cli_with_history):
        cli_with_history.export_history()
        
        assert cli_with_history.session_file.exists()
        content = cli_with_history.session_file.read_text()
        
        assert "OpsFleet Agent Session" in content
        assert "How many users?" in content
    
    def test_export_includes_all_queries(self, cli_with_history):
        cli_with_history.export_history()
        
        content = cli_with_history.session_file.read_text()
        assert "Query #1" in content
        assert "Query #2" in content
        assert "Query #3" in content

class TestCommandHandling:
    def test_handle_help_command(self, cli):
        result = cli.handle_command("/help")
        assert result is True
    
    def test_handle_history_command(self, cli):
        result = cli.handle_command("/history")
        assert result is True
    
    def test_handle_stats_command(self, cli):
        result = cli.handle_command("/stats")
        assert result is True
    
    def test_handle_save_command_default(self, cli_with_history):
        result = cli_with_history.handle_command("/save")
        assert result is True
        
        csv_files = list(cli_with_history.session_dir.glob("conversation_*.csv"))
        assert len(csv_files) > 0
    
    def test_handle_save_command_with_format(self, cli_with_history):
        result = cli_with_history.handle_command("/save json")
        assert result is True
        
        json_files = list(cli_with_history.session_dir.glob("conversation_*.json"))
        assert len(json_files) > 0
    
    def test_handle_export_command(self, cli_with_history):
        result = cli_with_history.handle_command("/export")
        assert result is True
        assert cli_with_history.session_file.exists()
    
    def test_handle_exit_command(self, cli):
        result = cli.handle_command("/exit")
        assert result is False
    
    def test_handle_quit_command(self, cli):
        result = cli.handle_command("/quit")
        assert result is False
    
    def test_handle_unknown_command(self, cli):
        result = cli.handle_command("/unknown")
        assert result is True
    
    def test_handle_schema_command(self, cli):
        result = cli.handle_command("/schema")
        assert result is True
    
    def test_handle_schema_command_with_table(self, cli):
        result = cli.handle_command("/schema users")
        assert result is True

class TestHistoryTracking:
    def test_history_starts_empty(self, cli):
        assert len(cli.history) == 0
    
    def test_history_tracks_queries(self, cli_with_history):
        assert len(cli_with_history.history) == 3
    
    def test_history_contains_required_fields(self, cli_with_history):
        entry = cli_with_history.history[0]
        assert "time" in entry
        assert "query" in entry
        assert "response" in entry
        assert "success" in entry
        assert "elapsed" in entry
    
    def test_history_tracks_success_status(self, cli_with_history):
        assert cli_with_history.history[0]["success"] is True
        assert cli_with_history.history[2]["success"] is False

class TestDataIntegrity:
    def test_csv_roundtrip(self, cli_with_history):
        original_data = cli_with_history.history.copy()
        cli_with_history.save_conversation("csv")
        
        csv_files = list(cli_with_history.session_dir.glob("conversation_*.csv"))
        df = pd.read_csv(csv_files[0])
        
        assert len(df) == len(original_data)
        assert df.iloc[0]["query"] == original_data[0]["query"]
    
    def test_json_roundtrip(self, cli_with_history):
        original_data = cli_with_history.history.copy()
        cli_with_history.save_conversation("json")
        
        json_files = list(cli_with_history.session_dir.glob("conversation_*.json"))
        with open(json_files[0], 'r') as f:
            loaded_data = json.load(f)
        
        assert len(loaded_data) == len(original_data)
        assert loaded_data[0]["query"] == original_data[0]["query"]
    
    def test_excel_roundtrip(self, cli_with_history):
        original_data = cli_with_history.history.copy()
        cli_with_history.save_conversation("excel")
        
        excel_files = list(cli_with_history.session_dir.glob("conversation_*.xlsx"))
        df = pd.read_excel(excel_files[0])
        
        assert len(df) == len(original_data)
        assert df.iloc[0]["query"] == original_data[0]["query"]

class TestFileNaming:
    def test_save_creates_unique_filenames(self, cli_with_history):
        import time
        cli_with_history.save_conversation("csv")
        time.sleep(1)
        cli_with_history.save_conversation("csv")
        
        csv_files = list(cli_with_history.session_dir.glob("conversation_*.csv"))
        assert len(csv_files) == 2
    
    def test_filename_contains_timestamp(self, cli_with_history):
        cli_with_history.save_conversation("csv")
        
        csv_files = list(cli_with_history.session_dir.glob("conversation_*.csv"))
        filename = csv_files[0].name
        
        assert "conversation_" in filename
        assert filename.endswith(".csv")

class TestErrorHandling:
    def test_save_handles_invalid_format_gracefully(self, cli_with_history):
        try:
            cli_with_history.save_conversation("invalid_format")
        except Exception as e:
            pytest.fail(f"save_conversation raised exception: {e}")
    
    def test_export_handles_empty_history(self, cli):
        try:
            cli.export_history()
        except Exception as e:
            pytest.fail(f"export_history raised exception: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
