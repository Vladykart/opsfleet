"""
Database storage for conversation history
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
import json


class ConversationHistoryDB:
    """Stores conversation history in database"""
    
    def __init__(self, db_connection):
        self.db = db_connection
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create tables if they don't exist"""
        # This would use your existing database
        # For now, we'll use in-memory storage
        self.conversations = []
    
    def save_conversation(
        self, 
        thread_id: str, 
        query: str, 
        response: str,
        metadata: Dict = None
    ):
        """Save conversation entry to database"""
        entry = {
            'thread_id': thread_id,
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response,
            'metadata': json.dumps(metadata or {}),
            'session_id': thread_id
        }
        
        self.conversations.append(entry)
        print(f"[DB] Saved conversation entry for thread {thread_id}")
    
    def get_thread_history(
        self, 
        thread_id: str, 
        limit: int = 10
    ) -> List[Dict]:
        """Get conversation history for a thread"""
        thread_convos = [
            c for c in self.conversations 
            if c['thread_id'] == thread_id
        ]
        
        return thread_convos[-limit:]
    
    def get_all_threads(self) -> List[str]:
        """Get all thread IDs"""
        return list(set(c['thread_id'] for c in self.conversations))
    
    def clear_thread(self, thread_id: str):
        """Clear history for a specific thread"""
        self.conversations = [
            c for c in self.conversations 
            if c['thread_id'] != thread_id
        ]
        print(f"[DB] Cleared history for thread {thread_id}")
