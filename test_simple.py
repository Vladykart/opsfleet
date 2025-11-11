"""
Simple test to verify the agent works
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check required env vars
required_vars = ["GCP_PROJECT_ID", "GOOGLE_API_KEY"]
missing = [var for var in required_vars if not os.getenv(var)]

if missing:
    print(f"❌ Missing environment variables: {', '.join(missing)}")
    print("\nPlease set them in your .env file:")
    for var in missing:
        print(f"  {var}=your-value-here")
    exit(1)

print("✅ Environment variables configured")
print(f"   GCP_PROJECT_ID: {os.getenv('GCP_PROJECT_ID')}")
print(f"   GOOGLE_API_KEY: {'*' * 20}")

# Test imports
try:
    from langgraph.graph import StateGraph
    from langchain_google_genai import ChatGoogleGenerativeAI
    from google.cloud import bigquery
    print("\n✅ All dependencies imported successfully")
except ImportError as e:
    print(f"\n❌ Import error: {e}")
    exit(1)

# Test BigQuery connection
try:
    client = bigquery.Client()
    query = "SELECT COUNT(*) as count FROM `bigquery-public-data.thelook_ecommerce.users` LIMIT 1"
    result = client.query(query).result()
    count = list(result)[0]['count']
    print(f"\n✅ BigQuery connection successful")
    print(f"   Found {count:,} users in the database")
except Exception as e:
    print(f"\n❌ BigQuery error: {e}")
    print("\nMake sure you've run: gcloud auth application-default login")
    exit(1)

# Test Gemini
try:
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.3)
    response = llm.invoke("Say 'Hello, I am working!' and nothing else")
    print(f"\n✅ Gemini API working")
    print(f"   Response: {response.content}")
except Exception as e:
    print(f"\n❌ Gemini error: {e}")
    print("\nCheck your GOOGLE_API_KEY in .env")
    exit(1)

print("\n" + "="*60)
print("🎉 All tests passed! The agent is ready to use.")
print("="*60)
print("\nRun the agent with: python agent.py")
