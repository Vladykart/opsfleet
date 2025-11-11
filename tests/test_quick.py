import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from src.agents.data_analysis_agent import DataAnalysisAgent
import json


async def test_product_analysis():
    print("="*60)
    print("Quick Test: Product Performance Analysis")
    print("="*60)
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), "config", "agent_config.json")
        with open(config_path) as f:
            config = json.load(f)
        
        agent = DataAnalysisAgent(config)
        await agent.initialize()
        
        print("✓ Agent initialized\n")
        
        query = "What are the top 10 products by revenue?"
        print(f"Query: {query}\n")
        
        try:
            result = await agent.analyze_product_performance(query)
        except Exception as e:
            print(f"Error during analysis: {e}")
            print("\nTrying to get SQL that was generated...")
            raise
        
        print(f"✓ Analysis completed")
        print(f"  Rows: {result['row_count']}\n")
        
        print("Generated SQL:")
        print("-" * 60)
        print(result['sql'][:400] + "..." if len(result['sql']) > 400 else result['sql'])
        
        print("\n" + "="*60)
        print("Key Insights:")
        print("="*60)
        for i, insight in enumerate(result['insights'], 1):
            print(f"{i}. {insight}")
        
        if result['row_count'] > 0:
            print(f"\n" + "="*60)
            print("Sample Data:")
            print("="*60)
            print(result['data'].head(3).to_string())
        
        print("\n✅ TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(test_product_analysis())
