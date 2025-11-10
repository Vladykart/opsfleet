import pytest
import asyncio
from src.mcp_client import MCPClient


@pytest.mark.asyncio
async def test_mcp_client_initialization():
    config = {
        "mcpServers": {
            "test_server": {
                "command": "echo",
                "args": ["test"]
            }
        }
    }
    
    client = MCPClient(config)
    assert client is not None
    assert "test_server" in client.servers


def test_environment_variable_resolution():
    from src.mcp_client import MCPClient
    import os
    
    os.environ["TEST_VAR"] = "test_value"
    
    config = {
        "mcpServers": {
            "test": {
                "command": "test",
                "env": {
                    "KEY": "${TEST_VAR}"
                }
            }
        }
    }
    
    client = MCPClient(config)
    resolved_env = client._resolve_env_vars(config["mcpServers"]["test"].get("env", {}))
    
    assert resolved_env["KEY"] == "test_value"
