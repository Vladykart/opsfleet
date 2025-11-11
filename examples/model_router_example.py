import asyncio
from src.model_router import ModelRouter


async def main():
    router = ModelRouter()
    
    print("="*60)
    print("Model Router Example")
    print("="*60)
    
    print("\n1. Get LLM for specific tasks:")
    
    generation_llm = router.get_llm_for_task("generation", temperature=0.8)
    print(f"   Generation task: {router.select_model_for_task('generation')}")
    
    validation_llm = router.get_llm_for_task("validation", temperature=0.3)
    print(f"   Validation task: {router.select_model_for_task('validation')}")
    
    analysis_llm = router.get_llm_for_task("analysis", temperature=0.5)
    print(f"   Analysis task: {router.select_model_for_task('analysis')}")
    
    print("\n2. Get specific models:")
    
    gpt4_llm = router.get_llm("gpt-4", temperature=0.7)
    print(f"   GPT-4 model loaded")
    
    llama_llm = router.get_llm("llama3.2", temperature=0.7)
    print(f"   Llama 3.2 model loaded")
    
    print("\n3. Test generation:")
    try:
        response = await generation_llm.ainvoke("Say hello!")
        print(f"   Response: {response.content}")
    except Exception as e:
        print(f"   Error: {e}")
        print("   Make sure Ollama is running: ollama serve")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    asyncio.run(main())
