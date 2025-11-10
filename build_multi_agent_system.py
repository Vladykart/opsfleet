import asyncio
import json
import os
from dotenv import load_dotenv
from src.orchestration.workflow import create_workflow
from src.mcp_client import get_mcp_client
from utils.logging_utils import setup_logging

load_dotenv()


async def main():
    logger = setup_logging(log_level=os.getenv("LOG_LEVEL", "INFO"))
    
    config_path = os.path.join(os.path.dirname(__file__), "config", "agent_config.json")
    with open(config_path) as f:
        agent_config = json.load(f)
    
    mcp_config_path = os.path.join(os.path.dirname(__file__), "config", "mcp_config.json")
    with open(mcp_config_path) as f:
        mcp_config = json.load(f)
    
    logger.info("Initializing MCP servers...")
    mcp_client = await get_mcp_client(mcp_config)
    
    for server_name in mcp_config["mcpServers"].keys():
        try:
            tools = await mcp_client.list_tools(server_name)
            logger.info(f"MCP Server '{server_name}' tools: {[t.get('name', 'unknown') for t in tools]}")
        except Exception as e:
            logger.warning(f"Could not list tools for {server_name}: {e}")
    
    logger.info("Building LangGraph workflow...")
    workflow = create_workflow(agent_config)
    await workflow.initialize()
    
    print("\n" + "="*60)
    print("🤖 Data Analysis Agent Ready (MCP-Powered)")
    print("="*60)
    print("Available MCP Servers:")
    for server in mcp_config["mcpServers"].keys():
        print(f"  ✓ {server}")
    print("="*60 + "\n")
    
    while True:
        try:
            query = input("Your query (or 'exit' to quit): ")
            
            if query.lower() in ['exit', 'quit']:
                break
            
            if not query.strip():
                continue
            
            logger.info(f"Processing query: {query}")
            result = await workflow.run(query)
            
            print("\n" + "-"*60)
            print("📊 Analysis Report:")
            print("-"*60)
            print(result.get("report", "No report generated"))
            
            if result.get("recommendations"):
                print("\n💡 Recommendations:")
                for i, rec in enumerate(result["recommendations"], 1):
                    print(f"  {i}. {rec}")
            
            print("-"*60 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            print(f"\n❌ Error: {e}\n")
    
    await mcp_client.close()
    logger.info("MCP connections closed")


if __name__ == "__main__":
    asyncio.run(main())
