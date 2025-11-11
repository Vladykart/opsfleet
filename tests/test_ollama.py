import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from src.agents.data_analysis_agent import DataAnalysisAgent
import json


async def test_ollama_integration():
    print("="*60)
    print("Testing Ollama Integration for SQL Generation")
    print("="*60)
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), "config", "agent_config.json")
        with open(config_path) as f:
            config = json.load(f)
        
        print(f"\nPrimary LLM: {config['llm']['primary']['provider']}")
        print(f"Model: {config['llm']['primary']['model']}")
        print(f"Fallback: {config['llm']['fallback']['provider']}\n")
        
        agent = DataAnalysisAgent(config)
        await agent.initialize()
        
        print("✓ Agent initialized with Ollama\n")
        
        query = "What are the top 5 products by revenue?"
        print(f"Query: {query}\n")
        print("Generating SQL with Ollama...")
        
        result = await agent.analyze_product_performance(query)
        
        print(f"\n✓ Analysis completed successfully!")
        print(f"  Rows returned: {result['row_count']}\n")
        
        print("Generated SQL:")
        print("-" * 60)
        print(result['sql'])
        print("-" * 60)
        
        print("\nKey Insights:")
        for i, insight in enumerate(result['insights'], 1):
            print(f"{i}. {insight}")
        
        if result['row_count'] > 0:
            print(f"\nTop 3 Products:")
            print(result['data'].head(3).to_string())
        
        print("\n" + "="*60)
        print("✅ OLLAMA INTEGRATION SUCCESSFUL!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_customer_segmentation():
    print("\n" + "="*60)
    print("Testing Customer Segmentation with Ollama")
    print("="*60)
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), "config", "agent_config.json")
        with open(config_path) as f:
            config = json.load(f)
        
        agent = DataAnalysisAgent(config)
        await agent.initialize()
        
        query = "Segment customers by order count and show top 5 segments"
        print(f"\nQuery: {query}\n")
        
        result = await agent.analyze_customer_segmentation(query)
        
        print(f"✓ Segmentation completed")
        print(f"  Rows: {result['row_count']}\n")
        
        print("Generated SQL:")
        print("-" * 60)
        print(result['sql'][:400] + "..." if len(result['sql']) > 400 else result['sql'])
        print("-" * 60)
        
        print("\nInsights:")
        for i, insight in enumerate(result['insights'], 1):
            print(f"{i}. {insight}")
        
        print("\n✅ CUSTOMER SEGMENTATION SUCCESSFUL!")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("\n🚀 Ollama Integration Tests\n")
    
    results = []
    
    result1 = await test_ollama_integration()
    results.append(("Product Analysis with Ollama", result1))
    
    result2 = await test_customer_segmentation()
    results.append(("Customer Segmentation with Ollama", result2))
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:40s} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
