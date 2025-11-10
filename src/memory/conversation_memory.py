from typing import List, Dict
from datetime import datetime


class ConversationMemory:
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.exchanges: List[Dict] = []
    
    def add_exchange(self, user_message: str, assistant_message: str):
        exchange = {
            "timestamp": datetime.now(),
            "user": user_message,
            "assistant": assistant_message
        }
        self.exchanges.append(exchange)
        
        if len(self.exchanges) > self.max_history:
            self.exchanges = self.exchanges[-self.max_history:]
    
    def get_recent(self, limit: int = 5) -> List[Dict]:
        return self.exchanges[-limit:]
    
    def get_context_string(self) -> str:
        context = []
        for exchange in self.exchanges[-5:]:
            context.append(f"User: {exchange['user']}")
            context.append(f"Assistant: {exchange['assistant']}")
        return "\n\n".join(context)
    
    def clear(self):
        self.exchanges = []
