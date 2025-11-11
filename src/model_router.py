from typing import Literal, Optional
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.language_models.chat_models import BaseChatModel
import os


class ModelRouter:
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
    def get_llm(
        self,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> BaseChatModel:
        if model_name.startswith("gpt") and model_name != "gpt-oss:120b-cloud":
            return ChatOpenAI(
                model=model_name,
                temperature=temperature,
                max_tokens=max_tokens,
                api_key=self.openai_api_key
            )
        else:
            return ChatOllama(
                model=model_name,
                base_url=self.ollama_base_url,
                temperature=temperature
            )
    
    def select_model_for_task(self, task: str) -> str:
        """Select best model for each task type"""
        task_models = {
            # Critical tasks - use GPT-OSS (most capable)
            "sql_generation": "gpt-oss:120b-cloud",
            "sql_fixing": "gpt-oss:120b-cloud",
            "understanding": "gpt-oss:120b-cloud",
            "synthesis": "gpt-oss:120b-cloud",
            
            # Medium tasks - use Llama (fast, good enough)
            "planning": "llama3.2",
            "validation": "llama3.2",
            "interpretation": "llama3.2",
            
            # Simple tasks - use Llama (fast)
            "routing": "llama3.2",
            "analysis": "llama3.2"
        }
        return task_models.get(task, "llama3.2")
    
    def get_llm_for_task(self, task: str, temperature: float = 0.7) -> BaseChatModel:
        model = self.select_model_for_task(task)
        return self.get_llm(model, temperature)
