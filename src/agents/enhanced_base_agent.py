from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from src.model_router import ModelRouter

logger = logging.getLogger(__name__)


class EnhancedBaseAgent(ABC):
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_router = ModelRouter()
        self.mcp_client = None
        
    def get_llm_for_task(self, task: str, temperature: float = 0.7):
        return self.model_router.get_llm_for_task(task, temperature)
    
    def get_llm(self, model_name: str, temperature: float = 0.7, max_tokens: Optional[int] = None):
        return self.model_router.get_llm(model_name, temperature, max_tokens)
    
    async def initialize(self):
        logger.info(f"Initializing {self.__class__.__name__}")
    
    @abstractmethod
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        pass
