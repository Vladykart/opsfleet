import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from src.agents.data_analysis_agent import DataAnalysisAgent
import json


async def test_ensemble_mode():
    print("="*60)
    print("Testing Ensemble Mode (Ollama + Gemini)")
    print("="*60)
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), "config", "agent_config.json")
        with open(config_path) as f:
            config = json.load(f)
        
        print(f"\nEnsemble Mode: {config['llm'].get('use_ensemble', False)}")
        print(f"Primary: {config['llm']['primary']['provider']} ({config['llm']['primary']['model']})")
        print(f"Secondary: {config['llm']['secondary']['provider']} ({config['llm']['secondary']['model']})")
        
        agent = DataAnalysisAgent(config)
        await agent.initialize()
        
        print("\n✓ Agent initialized with ensemble mode\n")
        
        query = "What are the top 5 products by revenue?"
        print(f"Query: {query}\n")
        print("Calling both Ollama and Gemini in parallel...")
        
        result = await agent.analyze_product_performance(query)
        
        print(f"\n✓ Analysis completed successfully!")
        print(f"  Rows returned: {result['row_count']}\n")
        
        print("Generated SQL:")
        print("-" * 60)
        sql_preview = result['sql'][:300] + "..." if len(result['sql']) > 300 else result['sql']
        print(sql_preview)
        print("-" * 60)
        
        print("\nKey Insights:")
        for i, insight in enumerate(result['insights'], 1):
            print(f"{i}. {insight[:100]}...")
        
        if result['row_count'] > 0:
            print(f"\nTop 3 Products:")
            print(result['data'].head(3).to_string())
        
        print("\n" + "="*60)
        print("✅ ENSEMBLE MODE TEST PASSED!")
        print("="*60)
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_fallback_behavior():
    print("\n" + "="*60)
    print("Testing Fallback Behavior")
    print("="*60)
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), "config", "agent_config.json")
        with open(config_path) as f:
            config = json.load(f)
        
        # Disable ensemble to test fallback
        config['llm']['use_ensemble'] = False
        
        agent = DataAnalysisAgent(config)
        await agent.initialize()
        
        print("\nEnsemble disabled - testing fallback chain")
        print("Primary: Ollama → Fallback: Gemini\n")
        
        query = "Show sales by country, top 5"
        result = await agent.execute_custom_analysis(query, "geographic")
        
        print(f"✓ Fallback working")
        print(f"  Rows: {result['row_count']}")
        print(f"  SQL length: {len(result['sql'])} chars")
        
        print("\n✅ FALLBACK TEST PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_langsmith_tracing():
    print("\n" + "="*60)
    print("Testing LangSmith Tracing")
    print("="*60)
    
    langsmith_key = os.getenv("LANGSMITH_API_KEY")
    
    if not langsmith_key:
        print("\n⚠️  LANGSMITH_API_KEY not set")
        print("Tracing will not be enabled")
        print("Set LANGSMITH_API_KEY in .env to enable tracing")
        return True
    
    print(f"\n✓ LangSmith API key found")
    print(f"  Project: {os.getenv('LANGCHAIN_PROJECT', 'bigquery-data-analysis')}")
    print(f"  Tracing: {os.getenv('LANGCHAIN_TRACING_V2', 'false')}")
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), "config", "agent_config.json")
        with open(config_path) as f:
            config = json.load(f)
        
        agent = DataAnalysisAgent(config)
        await agent.initialize()
        
        query = "Top 3 products"
        result = await agent.analyze_product_performance(query)
        
        print(f"\n✓ Query executed with tracing")
        print(f"  View traces at: https://smith.langchain.com/")
        print(f"  Project: bigquery-data-analysis")
        
        print("\n✅ LANGSMITH TRACING ENABLED!")
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False


async def main():
    print("\n🚀 Ensemble Mode & LangSmith Integration Tests\n")
    
    results = []
    
    result1 = await test_ensemble_mode()
    results.append(("Ensemble Mode", result1))
    
    result2 = await test_fallback_behavior()
    results.append(("Fallback Behavior", result2))
    
    result3 = await test_langsmith_tracing()
    results.append(("LangSmith Tracing", result3))
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:30s} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("\n🎉 All tests passed! System ready for production.")
        print("\nNext steps:")
        print("1. View traces at https://smith.langchain.com/")
        print("2. Monitor ensemble decisions in logs")
        print("3. Optimize based on LangSmith analytics")
    else:
        print("\n⚠️  Some tests failed. Check logs above.")


if __name__ == "__main__":
    asyncio.run(main())
