from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import google.generativeai as genai
import boto3
import os
import httpx
from langsmith import traceable


class BaseAgent(ABC):
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.mcp_client = None
        self._setup_llm_clients()
    
    def _setup_llm_clients(self):
        llm_config = self.config.get("llm", {})
        
        self.use_ensemble = llm_config.get("use_ensemble", False)
        
        primary = llm_config.get("primary", {})
        secondary = llm_config.get("secondary", {})
        self.primary_provider = primary.get("provider", "ollama")
        
        if primary.get("provider") == "ollama" or self.primary_provider == "ollama":
            self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
            self.ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
            self.logger.info(f"Ollama configured: {self.ollama_host} with model {self.ollama_model}")
        
        if primary.get("provider") == "google" or secondary.get("provider") == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                model_name = secondary.get("model") or primary.get("model", "gemini-2.5-flash")
                self.gemini_model = genai.GenerativeModel(model_name=model_name)
                self.logger.info(f"Gemini configured: {model_name}")
            else:
                self.logger.warning("GOOGLE_API_KEY not set")
                self.gemini_model = None
        else:
            self.gemini_model = None
        
        fallback = llm_config.get("fallback", {})
        if fallback.get("provider") == "aws_bedrock":
            try:
                self.bedrock_client = boto3.client(
                    "bedrock-runtime",
                    region_name=os.getenv("AWS_REGION", "us-east-1")
                )
            except Exception as e:
                self.logger.warning(f"Failed to initialize Bedrock client: {e}")
                self.bedrock_client = None
        else:
            self.bedrock_client = None
        
        langsmith_key = os.getenv("LANGSMITH_API_KEY")
        if langsmith_key:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_PROJECT"] = "bigquery-data-analysis"
            self.logger.info("LangSmith tracing enabled")
    
    @traceable(name="llm_call")
    async def _call_llm(
        self, 
        prompt: str, 
        temperature: float = 0.1,
        max_tokens: int = 2048
    ) -> str:
        if self.use_ensemble and hasattr(self, 'ollama_host') and self.gemini_model:
            self.logger.info("Using ensemble mode: Ollama + Gemini")
            return await self._call_ensemble(prompt, temperature, max_tokens)
        
        if self.primary_provider == "ollama":
            try:
                return await self._call_ollama(prompt, temperature, max_tokens)
            except Exception as e:
                self.logger.error(f"Ollama call failed: {e}")
                if self.gemini_model:
                    self.logger.info("Falling back to Gemini")
                    return await self._call_gemini(prompt, temperature, max_tokens)
                raise
        
        try:
            if self.gemini_model:
                return await self._call_gemini(prompt, temperature, max_tokens)
            else:
                raise Exception("No LLM client available")
        except Exception as e:
            self.logger.error(f"Primary LLM call failed: {e}")
            if hasattr(self, 'ollama_host'):
                self.logger.info("Falling back to Ollama")
                return await self._call_ollama(prompt, temperature, max_tokens)
            if self.bedrock_client:
                return await self._call_bedrock(prompt, temperature, max_tokens)
            raise
    
    @traceable(name="ensemble_call")
    async def _call_ensemble(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 2048
    ) -> str:
        import asyncio
        
        try:
            ollama_task = self._call_ollama(prompt, temperature, max_tokens)
            gemini_task = self._call_gemini(prompt, temperature, max_tokens)
            
            results = await asyncio.gather(ollama_task, gemini_task, return_exceptions=True)
            
            ollama_result = results[0] if not isinstance(results[0], Exception) else None
            gemini_result = results[1] if not isinstance(results[1], Exception) else None
            
            if ollama_result and gemini_result:
                if len(ollama_result) > len(gemini_result):
                    self.logger.info("Ensemble: Using Ollama result (longer)")
                    return ollama_result
                else:
                    self.logger.info("Ensemble: Using Gemini result (longer)")
                    return gemini_result
            elif ollama_result:
                self.logger.info("Ensemble: Only Ollama succeeded")
                return ollama_result
            elif gemini_result:
                self.logger.info("Ensemble: Only Gemini succeeded")
                return gemini_result
            else:
                raise Exception("Both Ollama and Gemini failed in ensemble mode")
        except Exception as e:
            self.logger.error(f"Ensemble call failed: {e}")
            raise
    
    async def _call_gemini(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 2048
    ) -> str:
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        response = self.gemini_model.generate_content(
            prompt,
            generation_config=generation_config
        )
        if response.candidates and len(response.candidates) > 0:
            candidate = response.candidates[0]
            if candidate.content and candidate.content.parts:
                return candidate.content.parts[0].text
            else:
                raise Exception(f"No content in response. Finish reason: {candidate.finish_reason}")
        else:
            raise Exception("No candidates in response")
    
    async def _call_ollama(
        self,
        prompt: str,
        temperature: float = 0.1,
        max_tokens: int = 2048
    ) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": self.ollama_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                        "num_predict": max_tokens
                    }
                }
            )
            response.raise_for_status()
            result = response.json()
            return result["response"]
    
    async def _call_bedrock(
        self, 
        prompt: str, 
        temperature: float = 0.1,
        max_tokens: int = 2048
    ) -> str:
        try:
            import json
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
            response = self.bedrock_client.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body=body
            )
            response_body = response["body"].read()
            result = json.loads(response_body)
            return result["content"][0]["text"]
        except Exception as e:
            self.logger.error(f"Bedrock call failed: {e}")
            raise
    
    @abstractmethod
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        pass
    
    async def initialize(self):
        pass
