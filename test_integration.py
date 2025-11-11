import asyncio
import sys
import os
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from src.bigquery_runner import BigQueryRunner
from src.agents.data_analysis_agent import DataAnalysisAgent
import json


async def test_bigquery_connection():
    print("="*60)
    print("Test 1: BigQuery Connection")
    print("="*60)
    
    try:
        project_id = os.getenv("GCP_PROJECT_ID")
        print(f"Project ID: {project_id}")
        
        runner = BigQueryRunner(
            project_id=project_id,
            dataset_id="bigquery-public-data.thelook_ecommerce"
        )
        
        print("✓ BigQueryRunner initialized")
        
        tables = runner.list_tables()
        print(f"✓ Found {len(tables)} tables: {', '.join(tables[:5])}")
        
        schema = runner.get_table_schema("users")
        print(f"✓ Retrieved schema for 'users' table: {len(schema)} fields")
        print(f"  Sample fields: {', '.join([f['name'] for f in schema[:5]])}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


async def test_simple_query():
    print("\n" + "="*60)
    print("Test 2: Simple Query Execution")
    print("="*60)
    
    try:
        project_id = os.getenv("GCP_PROJECT_ID")
        runner = BigQueryRunner(
            project_id=project_id,
            dataset_id="bigquery-public-data.thelook_ecommerce"
        )
        
        sql = """
        SELECT 
            COUNT(*) as total_users,
            COUNT(DISTINCT country) as countries
        FROM `bigquery-public-data.thelook_ecommerce.users`
        LIMIT 1
        """
        
        print("Executing query...")
        df = runner.execute_query(sql)
        
        print(f"✓ Query executed successfully")
        print(f"  Total users: {df['total_users'].iloc[0]:,}")
        print(f"  Countries: {df['countries'].iloc[0]}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_data_analysis_agent():
    print("\n" + "="*60)
    print("Test 3: Data Analysis Agent")
    print("="*60)
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), "config", "agent_config.json")
        with open(config_path) as f:
            config = json.load(f)
        
        agent = DataAnalysisAgent(config)
        await agent.initialize()
        
        print("✓ DataAnalysisAgent initialized")
        
        query = "Show top 5 countries by number of users"
        print(f"\nQuery: {query}")
        print("Generating SQL and executing...")
        
        result = await agent.execute_custom_analysis(query, "geographic")
        
        print(f"✓ Analysis completed")
        print(f"  Rows returned: {result['row_count']}")
        print(f"\nGenerated SQL:")
        print(result['sql'][:300] + "..." if len(result['sql']) > 300 else result['sql'])
        
        print(f"\nInsights:")
        for i, insight in enumerate(result['insights'], 1):
            print(f"  {i}. {insight}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_customer_segmentation():
    print("\n" + "="*60)
    print("Test 4: Customer Segmentation Analysis")
    print("="*60)
    
    try:
        config_path = os.path.join(os.path.dirname(__file__), "config", "agent_config.json")
        with open(config_path) as f:
            config = json.load(f)
        
        agent = DataAnalysisAgent(config)
        await agent.initialize()
        
        query = "Segment customers by total orders and show top 10 segments"
        print(f"Query: {query}")
        print("Analyzing...")
        
        result = await agent.analyze_customer_segmentation(query)
        
        print(f"✓ Segmentation completed")
        print(f"  Rows returned: {result['row_count']}")
        
        print(f"\nKey Insights:")
        for i, insight in enumerate(result['insights'], 1):
            print(f"  {i}. {insight}")
        
        if result['row_count'] > 0:
            print(f"\nSample data shape: {result['data'].shape}")
            print(f"Columns: {', '.join(result['data'].columns[:5])}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    print("\n" + "🧪 BigQuery Data Analysis Agent - Integration Tests")
    print("="*60 + "\n")
    
    results = []
    
    result1 = await test_bigquery_connection()
    results.append(("BigQuery Connection", result1))
    
    result2 = await test_simple_query()
    results.append(("Simple Query", result2))
    
    result3 = await test_data_analysis_agent()
    results.append(("Data Analysis Agent", result3))
    
    result4 = await test_customer_segmentation()
    results.append(("Customer Segmentation", result4))
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:30s} {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
