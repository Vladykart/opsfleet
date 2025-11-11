import asyncio
import os
from dotenv import load_dotenv
from src.model_router import ModelRouter

load_dotenv()


async def demo_model_router():
    print("="*60)
    print("🤖 Model Router Demo")
    print("="*60)
    
    router = ModelRouter()
    
    print("\n📋 Available task mappings:")
    tasks = ["generation", "validation", "analysis", "routing"]
    for task in tasks:
        model = router.select_model_for_task(task)
        print(f"   {task:12} → {model}")
    
    print("\n🧪 Testing model selection...")
    
    try:
        llm = router.get_llm_for_task("generation", temperature=0.7)
        print(f"✅ Got LLM for generation task")
        print(f"   Model type: {type(llm).__name__}")
    except Exception as e:
        print(f"❌ Failed to get LLM: {e}")
    
    print("\n" + "="*60)
    print("💡 To use different models:")
    print("   1. For OpenAI: Set OPENAI_API_KEY in .env")
    print("   2. For Ollama: Install and run 'ollama serve'")
    print("   3. For Gemini: Check billing/quota limits")
    print("="*60)


async def demo_weaviate():
    print("\n="*60)
    print("🧠 Weaviate Vector Store Demo")
    print("="*60)
    
    try:
        import weaviate
        from weaviate.classes.init import Auth
        
        url = os.getenv("WEAVIATE_URL")
        api_key = os.getenv("WEAVIATE_API_KEY")
        
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=url,
            auth_credentials=Auth.api_key(api_key)
        )
        
        print(f"\n✅ Connected to Weaviate")
        print(f"   Status: {'Ready' if client.is_ready() else 'Not Ready'}")
        
        collections = client.collections.list_all()
        print(f"   Collections: {len(collections)}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Weaviate error: {e}")
    
    print("="*60)


async def demo_bigquery():
    print("\n="*60)
    print("📊 BigQuery Connection Demo")
    print("="*60)
    
    try:
        from google.cloud import bigquery
        
        project_id = os.getenv("GCP_PROJECT_ID")
        client = bigquery.Client(project=project_id)
        
        print(f"\n✅ Connected to BigQuery")
        print(f"   Project: {project_id}")
        
        datasets = list(client.list_datasets())
        print(f"   Datasets: {len(datasets)}")
        
        if datasets:
            for ds in datasets[:5]:
                print(f"     - {ds.dataset_id}")
        else:
            print("   (No datasets found - you may need to create one)")
        
    except Exception as e:
        print(f"❌ BigQuery error: {str(e)[:150]}")
    
    print("="*60)


async def main():
    print("\n🚀 LangGraph Data Analysis Agent - System Demo\n")
    
    await demo_model_router()
    await demo_weaviate()
    await demo_bigquery()
    
    print("\n✨ Demo complete!")
    print("\n📚 Next steps:")
    print("   1. Fix Gemini quota or use alternative LLM")
    print("   2. Grant BigQuery permissions to service account")
    print("   3. Run: python build_multi_agent_system.py")
    print()


if __name__ == "__main__":
    asyncio.run(main())
