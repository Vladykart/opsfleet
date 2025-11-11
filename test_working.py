"""
Test that the agent is working end-to-end
"""
from agent import run_agent

print("Testing OpsFleet Agent\n")
print("="*60)

# Test query
query = "What are the top 5 products by retail price?"
print(f"\nQuery: {query}\n")

try:
    response = run_agent(query)
    print(f"Response:\n{response}\n")
    print("="*60)
    print("✅ Agent is working!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
