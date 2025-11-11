import asyncio
import os
from dotenv import load_dotenv

load_dotenv()


async def test_weaviate():
    print("\n🔍 Testing Weaviate Connection...")
    try:
        import weaviate
        from weaviate.classes.init import Auth
        
        url = os.getenv("WEAVIATE_URL")
        api_key = os.getenv("WEAVIATE_API_KEY")
        
        if not url.startswith("http"):
            url = f"https://{url}"
        
        client = weaviate.connect_to_weaviate_cloud(
            cluster_url=url,
            auth_credentials=Auth.api_key(api_key)
        )
        
        print(f"✅ Connected to Weaviate: {url}")
        print(f"   Ready: {client.is_ready()}")
        client.close()
        return True
    except Exception as e:
        print(f"❌ Weaviate connection failed: {e}")
        return False


async def test_bigquery():
    print("\n🔍 Testing BigQuery Connection...")
    try:
        from google.cloud import bigquery
        
        project_id = os.getenv("GCP_PROJECT_ID")
        client = bigquery.Client(project=project_id)
        
        query = "SELECT 1 as test"
        result = client.query(query).result()
        
        print(f"✅ BigQuery connected: {project_id}")
        print(f"   Test query successful")
        return True
    except Exception as e:
        print(f"❌ BigQuery connection failed: {e}")
        return False


async def test_gemini():
    print("\n🔍 Testing Google Gemini...")
    try:
        import google.generativeai as genai
        
        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say hello")
        
        print(f"✅ Gemini connected")
        print(f"   Response: {response.text[:50]}...")
        return True
    except Exception as e:
        print(f"❌ Gemini connection failed: {e}")
        return False


async def test_openai():
    print("\n🔍 Testing OpenAI...")
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=10
        )
        
        print(f"✅ OpenAI connected")
        print(f"   Response: {response.choices[0].message.content}")
        return True
    except Exception as e:
        print(f"❌ OpenAI connection failed: {e}")
        return False


async def main():
    print("="*60)
    print("🧪 Testing All Connections")
    print("="*60)
    
    results = []
    
    results.append(("Weaviate", await test_weaviate()))
    results.append(("BigQuery", await test_bigquery()))
    results.append(("Gemini", await test_gemini()))
    results.append(("OpenAI", await test_openai()))
    
    print("\n" + "="*60)
    print("📊 Test Results Summary")
    print("="*60)
    
    for name, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All systems ready! You can now run:")
        print("   python build_multi_agent_system.py")
    else:
        print("\n⚠️  Some connections failed. Check the errors above.")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
