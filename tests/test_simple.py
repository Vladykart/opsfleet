import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def test_weaviate():
    print("\n✅ Testing Weaviate...")
    try:
        import weaviate
        from weaviate.classes.init import Auth
        
        url = os.getenv("WEAVIATE_URL")
        api_key = os.getenv("WEAVIATE_API_KEY")
        
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=url,
            auth_credentials=Auth.api_key(api_key)
        )
        
        print(f"   ✓ Connected: {client.is_ready()}")
        client.close()
        return True
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        return False


async def test_bigquery_list():
    print("\n✅ Testing BigQuery (list datasets)...")
    try:
        from google.cloud import bigquery
        
        project_id = os.getenv("GCP_PROJECT_ID")
        client = bigquery.Client(project=project_id)
        
        datasets = list(client.list_datasets())
        print(f"   ✓ Found {len(datasets)} datasets")
        if datasets:
            for ds in datasets[:3]:
                print(f"     - {ds.dataset_id}")
        return True
    except Exception as e:
        print(f"   ✗ Failed: {str(e)[:100]}")
        return False


async def test_gemini_list():
    print("\n✅ Testing Gemini (list models)...")
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        
        models = genai.list_models()
        available = [m.name for m in models if 'generateContent' in m.supported_generation_methods]
        
        print(f"   ✓ Found {len(available)} models")
        for model in available[:3]:
            print(f"     - {model}")
        
        if available:
            model_name = available[0].replace('models/', '')
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Hello")
            print(f"   ✓ Test generation: {response.text[:30]}...")
            return True
        return False
    except Exception as e:
        print(f"   ✗ Failed: {str(e)[:100]}")
        return False


async def test_model_router():
    print("\n✅ Testing ModelRouter...")
    try:
        from src.model_router import ModelRouter
        
        router = ModelRouter()
        print(f"   ✓ Router initialized")
        
        model_name = router.select_model_for_task("generation")
        print(f"   ✓ Selected model for generation: {model_name}")
        
        return True
    except Exception as e:
        print(f"   ✗ Failed: {str(e)[:100]}")
        return False


async def main():
    print("="*60)
    print("🧪 Quick Connection Test")
    print("="*60)
    
    results = []
    results.append(await test_weaviate())
    results.append(await test_bigquery_list())
    results.append(await test_gemini_list())
    results.append(await test_model_router())
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"📊 Result: {passed}/{total} tests passed")
    
    if passed >= 3:
        print("\n🎉 Core systems working! Ready to proceed.")
    else:
        print("\n⚠️  Some systems need attention.")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
