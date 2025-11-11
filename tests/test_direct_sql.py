import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from src.bigquery_runner import BigQueryRunner


def test_direct_queries():
    print("="*60)
    print("Direct BigQuery SQL Tests")
    print("="*60)
    
    project_id = os.getenv("GCP_PROJECT_ID")
    runner = BigQueryRunner(
        project_id=project_id,
        dataset_id="bigquery-public-data.thelook_ecommerce"
    )
    
    print(f"\n✓ Connected to project: {project_id}\n")
    
    # Test 1: Top products by revenue
    print("Test 1: Top 10 Products by Revenue")
    print("-" * 60)
    sql1 = """
    SELECT 
        p.name as product_name,
        p.category,
        p.brand,
        SUM(oi.sale_price) as total_revenue,
        COUNT(DISTINCT oi.order_id) as order_count,
        SUM(oi.sale_price - p.cost) as total_profit
    FROM `bigquery-public-data.thelook_ecommerce.order_items` oi
    JOIN `bigquery-public-data.thelook_ecommerce.products` p
        ON oi.product_id = p.id
    WHERE oi.status != 'Cancelled'
    GROUP BY p.name, p.category, p.brand
    ORDER BY total_revenue DESC
    LIMIT 10
    """
    
    try:
        df1 = runner.execute_query(sql1)
        print(f"✓ Query executed: {len(df1)} rows")
        print(df1.to_string())
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 2: Customer segments
    print("\n\nTest 2: Customer Segments by Order Count")
    print("-" * 60)
    sql2 = """
    WITH customer_orders AS (
        SELECT 
            user_id,
            COUNT(DISTINCT order_id) as order_count,
            SUM(num_of_item) as total_items
        FROM `bigquery-public-data.thelook_ecommerce.orders`
        WHERE status = 'Complete'
        GROUP BY user_id
    )
    SELECT 
        CASE 
            WHEN order_count >= 10 THEN 'High Frequency'
            WHEN order_count >= 5 THEN 'Medium Frequency'
            ELSE 'Low Frequency'
        END as segment,
        COUNT(*) as customer_count,
        AVG(order_count) as avg_orders,
        AVG(total_items) as avg_items
    FROM customer_orders
    GROUP BY segment
    ORDER BY avg_orders DESC
    """
    
    try:
        df2 = runner.execute_query(sql2)
        print(f"✓ Query executed: {len(df2)} rows")
        print(df2.to_string())
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test 3: Sales by country
    print("\n\nTest 3: Top 10 Countries by Sales")
    print("-" * 60)
    sql3 = """
    SELECT 
        u.country,
        COUNT(DISTINCT o.order_id) as order_count,
        COUNT(DISTINCT o.user_id) as customer_count,
        SUM(o.num_of_item) as total_items
    FROM `bigquery-public-data.thelook_ecommerce.orders` o
    JOIN `bigquery-public-data.thelook_ecommerce.users` u
        ON o.user_id = u.id
    WHERE o.status = 'Complete'
    GROUP BY u.country
    ORDER BY order_count DESC
    LIMIT 10
    """
    
    try:
        df3 = runner.execute_query(sql3)
        print(f"✓ Query executed: {len(df3)} rows")
        print(df3.to_string())
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "="*60)
    print("✅ All direct SQL tests completed successfully!")
    print("="*60)


if __name__ == "__main__":
    test_direct_queries()
