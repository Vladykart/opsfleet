import asyncio
import json
import os
from typing import Dict, Any, List, Optional
import logging
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


class MCPClient:
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.sessions: Dict[str, ClientSession] = {}
        
    async def initialize(self):
        for server_name, server_config in self.config.get("mcpServers", {}).items():
            try:
                await self._connect_server(server_name, server_config)
                logger.info(f"Connected to MCP server: {server_name}")
            except Exception as e:
                logger.error(f"Failed to connect to {server_name}: {e}")
    
    async def _connect_server(self, name: str, config: Dict):
        command = config.get("command")
        args = config.get("args", [])
        env = config.get("env", {})
        
        resolved_env = {}
        for key, value in env.items():
            if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
                env_var = value[2:-1]
                resolved_env[key] = os.getenv(env_var, "")
            else:
                resolved_env[key] = value
        
        resolved_args = []
        for arg in args:
            if isinstance(arg, str) and "${" in arg:
                for env_var in os.environ:
                    arg = arg.replace(f"${{{env_var}}}", os.getenv(env_var, ""))
            resolved_args.append(arg)
        
        server_params = StdioServerParameters(
            command=command,
            args=resolved_args,
            env={**os.environ.copy(), **resolved_env}
        )
        
        session = await stdio_client(server_params)
        self.sessions[name] = session
    
    async def call_tool(
        self, 
        server: str, 
        tool: str, 
        arguments: Optional[Dict[str, Any]] = None
    ) -> Any:
        if server not in self.sessions:
            raise ValueError(f"MCP server '{server}' not connected")
        
        session = self.sessions[server]
        
        try:
            result = await session.call_tool(
                name=tool,
                arguments=arguments or {}
            )
            logger.info(f"MCP tool call successful: {server}.{tool}")
            return result
        except Exception as e:
            logger.error(f"MCP tool call failed: {server}.{tool} - {e}")
            raise
    
    async def list_tools(self, server: str) -> List[Dict[str, Any]]:
        if server not in self.sessions:
            raise ValueError(f"MCP server '{server}' not connected")
        
        session = self.sessions[server]
        tools = await session.list_tools()
        return tools
    
    async def close(self):
        for name, session in self.sessions.items():
            try:
                await session.close()
                logger.info(f"Closed MCP server: {name}")
            except Exception as e:
                logger.error(f"Error closing {name}: {e}")


_mcp_client: Optional[MCPClient] = None


async def get_mcp_client(config: Optional[Dict] = None) -> MCPClient:
    global _mcp_client
    
    if _mcp_client is None:
        if config is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "config",
                "mcp_config.json"
            )
            with open(config_path) as f:
                config = json.load(f)
        
        _mcp_client = MCPClient(config)
        await _mcp_client.initialize()
    
    return _mcp_client
