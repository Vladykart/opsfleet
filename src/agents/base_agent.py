from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
import google.generativeai as genai
import boto3
import os


class BaseAgent(ABC):
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.mcp_client = None
        self._setup_llm_clients()
    
    def _setup_llm_clients(self):
        llm_config = self.config.get("llm", {})
        
        primary = llm_config.get("primary", {})
        if primary.get("provider") == "google":
            api_key = os.getenv("GOOGLE_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel(
                    model_name=primary.get("model", "gemini-1.5-pro")
                )
            else:
                self.logger.warning("GOOGLE_API_KEY not set")
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
    
    async def _call_llm(
        self, 
        prompt: str, 
        temperature: float = 0.1,
        max_tokens: int = 2048
    ) -> str:
        try:
            if self.gemini_model:
                generation_config = {
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
                response = self.gemini_model.generate_content(
                    prompt,
                    generation_config=generation_config
                )
                return response.text
            else:
                raise Exception("No LLM client available")
        except Exception as e:
            self.logger.error(f"Gemini call failed: {e}")
            if self.bedrock_client:
                return await self._call_bedrock(prompt, temperature, max_tokens)
            raise
    
    async def _call_bedrock(
        self, 
        prompt: str, 
        temperature: float = 0.1,
        max_tokens: int = 2048
    ) -> str:
        try:
            response = self.bedrock_client.invoke_model(
                modelId="anthropic.claude-3-sonnet-20240229-v1:0",
                body={
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                }
            )
            response_body = response["body"].read()
            import json
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
