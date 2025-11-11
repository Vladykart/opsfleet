"""
Schema Analysis Layer
Fetches, analyzes, and caches database schema information
"""
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()

project_id = os.getenv("GCP_PROJECT_ID")
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

if credentials_path and os.path.exists(credentials_path):
    from google.oauth2 import service_account
    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    bq_client = bigquery.Client(project=project_id, credentials=credentials)
else:
    bq_client = bigquery.Client(project=project_id)


@dataclass
class ColumnInfo:
    """Column metadata"""
    name: str
    type: str
    mode: str
    description: Optional[str] = None


@dataclass
class TableInfo:
    """Table metadata with analysis"""
    name: str
    full_name: str
    columns: List[ColumnInfo]
    row_count: Optional[int] = None
    size_bytes: Optional[int] = None
    created: Optional[datetime] = None
    modified: Optional[datetime] = None
    description: Optional[str] = None


class SchemaAnalyzer:
    """Analyze and cache database schema"""
    
    def __init__(self, dataset: str = "bigquery-public-data.thelook_ecommerce"):
        self.dataset = dataset
        self.cache: Dict[str, TableInfo] = {}
        self.last_refresh: Optional[datetime] = None
        
    def fetch_table_schema(self, table_name: str) -> TableInfo:
        """Fetch detailed schema for a table"""
        full_table_name = f"{self.dataset}.{table_name}"
        
        # Check cache
        if table_name in self.cache:
            return self.cache[table_name]
        
        try:
            # Get table reference
            table_ref = bigquery.TableReference.from_string(full_table_name)
            table = bq_client.get_table(table_ref)
            
            # Extract column information
            columns = []
            for field in table.schema:
                columns.append(ColumnInfo(
                    name=field.name,
                    type=field.field_type,
                    mode=field.mode,
                    description=field.description
                ))
            
            # Create table info
            table_info = TableInfo(
                name=table_name,
                full_name=full_table_name,
                columns=columns,
                row_count=table.num_rows,
                size_bytes=table.num_bytes,
                created=table.created,
                modified=table.modified,
                description=table.description
            )
            
            # Cache it
            self.cache[table_name] = table_info
            
            return table_info
            
        except Exception as e:
            print(f"Error fetching schema for {table_name}: {e}")
            return None
    
    def fetch_all_tables(self) -> Dict[str, TableInfo]:
        """Fetch schema for all tables in dataset"""
        tables = ["users", "products", "orders", "order_items"]
        
        for table_name in tables:
            self.fetch_table_schema(table_name)
        
        self.last_refresh = datetime.now()
        return self.cache
    
    def analyze_table(self, table_name: str) -> Dict[str, Any]:
        """Analyze a table and provide insights"""
        table_info = self.fetch_table_schema(table_name)
        
        if not table_info:
            return {"error": f"Table {table_name} not found"}
        
        # Analyze columns
        column_types = {}
        for col in table_info.columns:
            col_type = col.type
            column_types[col_type] = column_types.get(col_type, 0) + 1
        
        # Calculate size in MB
        size_mb = table_info.size_bytes / (1024 * 1024) if table_info.size_bytes else 0
        
        analysis = {
            "table_name": table_info.name,
            "full_name": table_info.full_name,
            "row_count": table_info.row_count,
            "size_mb": round(size_mb, 2),
            "column_count": len(table_info.columns),
            "column_types": column_types,
            "created": table_info.created.isoformat() if table_info.created else None,
            "modified": table_info.modified.isoformat() if table_info.modified else None,
            "columns": [
                {
                    "name": col.name,
                    "type": col.type,
                    "mode": col.mode,
                    "description": col.description or "No description"
                }
                for col in table_info.columns
            ]
        }
        
        return analysis
    
    def get_relationships(self) -> Dict[str, List[str]]:
        """Identify relationships between tables"""
        relationships = {
            "users": [
                "orders.user_id → users.id",
                "order_items.user_id → users.id"
            ],
            "products": [
                "order_items.product_id → products.id"
            ],
            "orders": [
                "order_items.order_id → orders.order_id"
            ],
            "order_items": [
                "order_items.user_id → users.id",
                "order_items.product_id → products.id",
                "order_items.order_id → orders.order_id"
            ]
        }
        return relationships
    
    def get_sample_queries(self, table_name: str) -> List[str]:
        """Generate sample queries for a table"""
        samples = {
            "users": [
                f"SELECT COUNT(*) as total_users FROM `{self.dataset}.users`",
                f"SELECT country, COUNT(*) as user_count FROM `{self.dataset}.users` GROUP BY country ORDER BY user_count DESC LIMIT 10",
                f"SELECT * FROM `{self.dataset}.users` LIMIT 5"
            ],
            "products": [
                f"SELECT COUNT(*) as total_products FROM `{self.dataset}.products`",
                f"SELECT category, COUNT(*) as product_count FROM `{self.dataset}.products` GROUP BY category ORDER BY product_count DESC",
                f"SELECT name, retail_price FROM `{self.dataset}.products` ORDER BY retail_price DESC LIMIT 10"
            ],
            "orders": [
                f"SELECT COUNT(*) as total_orders FROM `{self.dataset}.orders`",
                f"SELECT status, COUNT(*) as order_count FROM `{self.dataset}.orders` GROUP BY status",
                f"SELECT * FROM `{self.dataset}.orders` ORDER BY created_at DESC LIMIT 5"
            ],
            "order_items": [
                f"SELECT COUNT(*) as total_items FROM `{self.dataset}.order_items`",
                f"SELECT SUM(sale_price) as total_revenue FROM `{self.dataset}.order_items`",
                f"SELECT * FROM `{self.dataset}.order_items` LIMIT 5"
            ]
        }
        return samples.get(table_name, [])
    
    def get_summary(self) -> Dict[str, Any]:
        """Get overall database summary"""
        if not self.cache:
            self.fetch_all_tables()
        
        total_rows = sum(t.row_count or 0 for t in self.cache.values())
        total_size = sum(t.size_bytes or 0 for t in self.cache.values())
        
        summary = {
            "dataset": self.dataset,
            "table_count": len(self.cache),
            "total_rows": total_rows,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "last_refresh": self.last_refresh.isoformat() if self.last_refresh else None,
            "tables": {
                name: {
                    "rows": info.row_count,
                    "columns": len(info.columns),
                    "size_mb": round(info.size_bytes / (1024 * 1024), 2) if info.size_bytes else 0
                }
                for name, info in self.cache.items()
            }
        }
        
        return summary


# Global instance
schema_analyzer = SchemaAnalyzer()


def get_schema_info(table_name: Optional[str] = None) -> Dict[str, Any]:
    """Get schema information for display"""
    if table_name:
        return schema_analyzer.analyze_table(table_name)
    else:
        return schema_analyzer.get_summary()


def get_relationships() -> Dict[str, List[str]]:
    """Get table relationships"""
    return schema_analyzer.get_relationships()


def get_sample_queries(table_name: str) -> List[str]:
    """Get sample queries for a table"""
    return schema_analyzer.get_sample_queries(table_name)


if __name__ == "__main__":
    print("🔍 Schema Analyzer\n")
    print("="*60)
    
    # Fetch all schemas
    print("\n📊 Fetching database schema...")
    schema_analyzer.fetch_all_tables()
    
    # Show summary
    print("\n📈 Database Summary:")
    summary = schema_analyzer.get_summary()
    print(f"Dataset: {summary['dataset']}")
    print(f"Tables: {summary['table_count']}")
    print(f"Total Rows: {summary['total_rows']:,}")
    print(f"Total Size: {summary['total_size_mb']} MB")
    
    # Analyze each table
    for table_name in ["users", "products", "orders", "order_items"]:
        print(f"\n{'='*60}")
        print(f"📋 Table: {table_name}")
        print(f"{'='*60}")
        
        analysis = schema_analyzer.analyze_table(table_name)
        print(f"Rows: {analysis['row_count']:,}")
        print(f"Size: {analysis['size_mb']} MB")
        print(f"Columns: {analysis['column_count']}")
        
        print("\nColumns:")
        for col in analysis['columns'][:5]:  # Show first 5
            print(f"  - {col['name']} ({col['type']}) - {col['description']}")
        
        print("\nSample Queries:")
        for query in schema_analyzer.get_sample_queries(table_name)[:2]:
            print(f"  • {query}")
    
    # Show relationships
    print(f"\n{'='*60}")
    print("🔗 Table Relationships:")
    print(f"{'='*60}")
    relationships = schema_analyzer.get_relationships()
    for table, rels in relationships.items():
        print(f"\n{table}:")
        for rel in rels:
            print(f"  → {rel}")
    
    print("\n✅ Schema analysis complete!")
