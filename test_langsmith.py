#!/usr/bin/env python3
"""Test LangSmith tracing"""

import os
from dotenv import load_dotenv

load_dotenv()

# Print environment variables
print("Environment Variables:")
print(f"  LANGSMITH_API_KEY: {os.getenv('LANGSMITH_API_KEY')[:20]}...")
print(f"  LANGSMITH_TRACING: {os.getenv('LANGSMITH_TRACING')}")
print(f"  LANGSMITH_PROJECT: {os.getenv('LANGSMITH_PROJECT')}")
print(f"  LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
print(f"  LANGCHAIN_PROJECT: {os.getenv('LANGCHAIN_PROJECT')}")
print(f"  LANGCHAIN_ENDPOINT: {os.getenv('LANGCHAIN_ENDPOINT')}")

# Test tracing
from langsmith import traceable

@traceable(name="test_trace")
def test_function():
    return "Hello from LangSmith!"

result = test_function()
print(f"\nTest result: {result}")
print("\n✅ If you see this, tracing is configured!")
print("Check https://smith.langchain.com/ for traces")
