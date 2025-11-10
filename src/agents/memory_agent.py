from src.agents.base_agent import BaseAgent
from typing import Dict, List, Any


class MemoryAgent(BaseAgent):
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.conversation_memory = []
        self.vector_store = None
    
    async def initialize(self):
        from src.memory.vector_store import VectorStore
        from src.memory.conversation_memory import ConversationMemory
        
        memory_config = self.config.get("memory", {})
        
        self.conversation_memory_manager = ConversationMemory(
            max_history=memory_config.get("conversation_history_limit", 10)
        )
        
        try:
            self.vector_store = VectorStore(self.config)
            self.logger.info("Vector store initialized")
        except Exception as e:
            self.logger.warning(f"Vector store initialization failed: {e}")
            self.vector_store = None
    
    async def retrieve_context(
        self, 
        query: str, 
        limit: int = 5
    ) -> List[Dict]:
        context = []
        
        recent_history = self.conversation_memory_manager.get_recent(limit=3)
        context.extend(recent_history)
        
        if self.vector_store:
            try:
                memory_config = self.config.get("memory", {})
                threshold = memory_config.get("similarity_threshold", 0.7)
                
                similar_analyses = await self.vector_store.search(
                    query=query,
                    limit=limit,
                    threshold=threshold
                )
                context.extend(similar_analyses)
            except Exception as e:
                self.logger.error(f"Vector search failed: {e}")
        
        return context[:limit]
    
    async def store_analysis(
        self,
        query: str,
        insights: List[str],
        report: str,
        analysis_type: str = "unknown"
    ) -> str:
        from datetime import datetime
        
        self.conversation_memory_manager.add_exchange(
            user_message=query,
            assistant_message=report
        )
        
        if self.vector_store:
            try:
                analysis_data = {
                    "query": query,
                    "insights": insights,
                    "report": report,
                    "analysis_type": analysis_type,
                    "timestamp": datetime.now()
                }
                
                result = await self.vector_store.store(analysis_data)
                self.logger.info(f"Analysis stored in vector store: {result}")
                return result
            except Exception as e:
                self.logger.error(f"Failed to store in vector store: {e}")
                return ""
        
        return ""
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        context = await self.retrieve_context(
            query=state.get("user_query", ""),
            limit=self.config.get("memory", {}).get("max_context_items", 5)
        )
        
        return {
            "retrieved_context": context
        }
