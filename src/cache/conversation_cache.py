"""
Conversation cache and history manager
"""
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib


class ConversationCache:
    """Manages query result caching and conversation history for a session"""
    
    def __init__(self, thread_id: str):
        self.thread_id = thread_id
        self.query_cache = {}  # Cache query results
        self.conversation_history = []  # Store conversation
        self.cache_hits = 0
        self.cache_misses = 0
    
    def _generate_cache_key(self, query: str, params: Dict = None) -> str:
        """Generate cache key from query and parameters"""
        cache_str = f"{query}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def get_cached_result(self, query: str, params: Dict = None) -> Optional[Dict]:
        """Get cached query result if available"""
        cache_key = self._generate_cache_key(query, params)
        
        if cache_key in self.query_cache:
            self.cache_hits += 1
            cached = self.query_cache[cache_key]
            print(f"[Cache HIT] Retrieved cached result for query (age: {cached['age']}s)")
            return cached['result']
        
        self.cache_misses += 1
        return None
    
    def cache_result(self, query: str, result: Dict, params: Dict = None):
        """Cache query result"""
        cache_key = self._generate_cache_key(query, params)
        
        self.query_cache[cache_key] = {
            'result': result,
            'timestamp': datetime.now(),
            'age': 0,
            'query': query
        }
        
        print(f"[Cache STORE] Cached result for query")
    
    def add_to_history(self, query: str, response: str, metadata: Dict = None):
        """Add query and response to conversation history"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'response': response,
            'metadata': metadata or {}
        }
        
        self.conversation_history.append(entry)
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get recent conversation history"""
        return self.conversation_history[-limit:]
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        
        return {
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'cached_queries': len(self.query_cache)
        }
    
    def clear_cache(self):
        """Clear all cached data"""
        self.query_cache.clear()
        print("[Cache CLEAR] All cached data cleared")
    
    def update_cache_ages(self):
        """Update age of cached items"""
        now = datetime.now()
        for cache_key in self.query_cache:
            cached = self.query_cache[cache_key]
            age = (now - cached['timestamp']).total_seconds()
            cached['age'] = int(age)
