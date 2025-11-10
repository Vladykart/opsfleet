import weaviate
from typing import List, Dict, Optional
import os
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    
    def __init__(self, config: Dict):
        weaviate_url = os.getenv("WEAVIATE_URL", "http://localhost:8080")
        
        self.client = weaviate.Client(url=weaviate_url)
        self._ensure_schema()
    
    def _ensure_schema(self):
        schema = {
            "class": "EcommerceAnalysis",
            "description": "E-commerce data analysis results",
            "properties": [
                {
                    "name": "query",
                    "dataType": ["text"],
                    "description": "User's analysis query"
                },
                {
                    "name": "insights",
                    "dataType": ["text[]"],
                    "description": "Generated insights"
                },
                {
                    "name": "report",
                    "dataType": ["text"],
                    "description": "Full analysis report"
                },
                {
                    "name": "analysisType",
                    "dataType": ["string"],
                    "description": "Type of analysis performed"
                },
                {
                    "name": "timestamp",
                    "dataType": ["date"]
                }
            ],
            "vectorizer": "text2vec-transformers"
        }
        
        if not self.client.schema.exists("EcommerceAnalysis"):
            self.client.schema.create_class(schema)
            logger.info("Created Weaviate schema for EcommerceAnalysis")
    
    async def store(self, analysis: Dict) -> str:
        data_object = {
            "query": analysis["query"],
            "insights": analysis["insights"],
            "report": analysis["report"],
            "analysisType": analysis.get("analysis_type", "unknown"),
            "timestamp": analysis["timestamp"].isoformat()
        }
        
        result = self.client.data_object.create(
            data_object=data_object,
            class_name="EcommerceAnalysis"
        )
        
        return result
    
    async def search(
        self, 
        query: str, 
        limit: int = 5, 
        threshold: float = 0.7, 
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        
        result = (
            self.client.query
            .get("EcommerceAnalysis", ["query", "insights", "report", "analysisType", "timestamp"])
            .with_near_text({"concepts": [query], "certainty": threshold})
            .with_limit(limit)
        )
        
        if filters:
            where_filter = self._build_where_filter(filters)
            result = result.with_where(where_filter)
        
        response = result.do()
        
        if "data" in response and "Get" in response["data"]:
            return response["data"]["Get"].get("EcommerceAnalysis", [])
        
        return []
    
    def _build_where_filter(self, filters: Dict) -> Dict:
        where_conditions = []
        
        for key, value in filters.items():
            where_conditions.append({
                "path": [key],
                "operator": "Equal",
                "valueString": value
            })
        
        if len(where_conditions) == 1:
            return where_conditions[0]
        
        return {
            "operator": "And",
            "operands": where_conditions
        }
