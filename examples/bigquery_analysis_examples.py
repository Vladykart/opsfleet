import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dotenv import load_dotenv
from src.agents.data_analysis_agent import DataAnalysisAgent
from utils.logging_utils import setup_logging
import json

load_dotenv()


async def run_example_queries():
    logger = setup_logging(log_level="INFO")
    
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "agent_config.json")
    with open(config_path) as f:
        config = json.load(f)
    
    agent = DataAnalysisAgent(config)
    await agent.initialize()
    
    logger.info("BigQuery Data Analysis Agent initialized")
    
    examples = [
        {
            "name": "Customer Segmentation",
            "query": "Segment customers by purchase frequency and total spend. Show top 10 segments."
        },
        {
            "name": "Product Performance",
            "query": "What are the top 20 best-selling products by revenue in the last year?"
        },
        {
            "name": "Sales Trends",
            "query": "Show monthly sales trends for the past 12 months with growth rates"
        },
        {
            "name": "Geographic Analysis",
            "query": "Analyze sales distribution by country and state. Show top 15 regions."
        },
        {
            "name": "Custom Analysis",
            "query": "Find customers who made purchases in multiple categories and calculate their average order value"
        }
    ]
    
    for example in examples:
        print("\n" + "="*80)
        print(f"EXAMPLE: {example['name']}")
        print("="*80)
        print(f"Query: {example['query']}\n")
        
        try:
            result = await agent.process({"user_query": example["query"]})
            
            print("Generated SQL:")
            print("-"*80)
            for sql in result.get("generated_sql", []):
                print(sql)
            print()
            
            print("Insights:")
            print("-"*80)
            for i, insight in enumerate(result.get("insights", []), 1):
                print(f"{i}. {insight}")
            
            print(f"\nRows returned: {result['analysis_results'].get('row_count', 0)}")
            
        except Exception as e:
            logger.error(f"Example failed: {e}", exc_info=True)
            print(f"Error: {e}")
        
        print("\n")


async def interactive_mode():
    logger = setup_logging(log_level="INFO")
    
    config_path = os.path.join(os.path.dirname(__file__), "..", "config", "agent_config.json")
    with open(config_path) as f:
        config = json.load(f)
    
    agent = DataAnalysisAgent(config)
    await agent.initialize()
    
    print("\n" + "="*80)
    print("🔍 BigQuery Data Analysis Agent - Interactive Mode")
    print("="*80)
    print("Available analysis types:")
    print("  • Customer segmentation and behavior")
    print("  • Product performance and recommendations")
    print("  • Sales trends and seasonality")
    print("  • Geographic sales patterns")
    print("  • Custom queries")
    print("\nType 'exit' to quit")
    print("="*80 + "\n")
    
    while True:
        try:
            query = input("Your analysis query: ")
            
            if query.lower() in ['exit', 'quit']:
                break
            
            if not query.strip():
                continue
            
            print("\n⏳ Analyzing...\n")
            
            result = await agent.process({"user_query": query})
            
            print("📊 Results:")
            print("-"*80)
            print(f"Rows: {result['analysis_results'].get('row_count', 0)}")
            print("\nGenerated SQL:")
            for sql in result.get("generated_sql", []):
                print(sql[:500] + "..." if len(sql) > 500 else sql)
            
            print("\n💡 Key Insights:")
            for i, insight in enumerate(result.get("insights", []), 1):
                print(f"  {i}. {insight}")
            
            print("-"*80 + "\n")
            
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            logger.error(f"Query failed: {e}", exc_info=True)
            print(f"\n❌ Error: {e}\n")


async def main():
    import argparse
    parser = argparse.ArgumentParser(description="BigQuery Data Analysis Examples")
    parser.add_argument("--mode", choices=["examples", "interactive"], default="examples",
                       help="Run mode: examples or interactive")
    args = parser.parse_args()
    
    if args.mode == "examples":
        await run_example_queries()
    else:
        await interactive_mode()


if __name__ == "__main__":
    asyncio.run(main())
