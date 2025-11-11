"""
Direct test of the agent with a simple query
"""
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing BigQuery Agent with LangGraph\n")
print("="*60)

# Check environment
print("\n1. Checking environment variables...")
if not os.getenv("GOOGLE_API_KEY"):
    print("❌ GOOGLE_API_KEY not set")
    exit(1)
if not os.getenv("GCP_PROJECT_ID"):
    print("❌ GCP_PROJECT_ID not set")
    exit(1)

print("✅ Environment configured")
print(f"   Project: {os.getenv('GCP_PROJECT_ID')}")
print(f"   API Key: {'*' * 20}")

# Test imports
print("\n2. Testing imports...")
try:
    from agent import run_agent
    print("✅ Agent imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test simple query
print("\n3. Testing agent with simple query...")
print("-" * 60)

try:
    query = "How many users are in the database?"
    print(f"Query: {query}\n")
    
    response = run_agent(query)
    
    print(f"Response: {response}")
    print("-" * 60)
    print("\n✅ Agent test successful!")
    
except Exception as e:
    print(f"\n❌ Agent test failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "="*60)
print("🎉 All tests passed!")
print("="*60)
