import os
import json
from dotenv import load_dotenv

load_dotenv()


def check_service_account():
    print("="*60)
    print("🔍 Checking Service Account Configuration")
    print("="*60)
    
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    project_id = os.getenv("GCP_PROJECT_ID")
    
    print(f"\n📁 Credentials Path: {creds_path}")
    print(f"📊 Project ID: {project_id}")
    
    if not creds_path or not os.path.exists(creds_path):
        print("\n❌ Service account file not found!")
        return False
    
    with open(creds_path, 'r') as f:
        creds = json.load(f)
    
    print(f"\n✅ Service Account Details:")
    print(f"   Email: {creds.get('client_email')}")
    print(f"   Project: {creds.get('project_id')}")
    print(f"   Type: {creds.get('type')}")
    
    return True


def test_bigquery_access():
    print("\n" + "="*60)
    print("🧪 Testing BigQuery Access")
    print("="*60)
    
    try:
        from google.cloud import bigquery
        
        project_id = os.getenv("GCP_PROJECT_ID")
        client = bigquery.Client(project=project_id)
        
        print(f"\n✅ BigQuery client initialized")
        print(f"   Project: {client.project}")
        
        print("\n📋 Testing public dataset access...")
        query = """
        SELECT 
            name, 
            SUM(number) as total
        FROM `bigquery-public-data.usa_names.usa_1910_current`
        WHERE year = 2020
        GROUP BY name
        ORDER BY total DESC
        LIMIT 5
        """
        
        print("   Running test query on public dataset...")
        query_job = client.query(query)
        results = query_job.result()
        
        print("\n✅ Query successful! Top 5 names in 2020:")
        for row in results:
            print(f"   {row.name}: {row.total:,}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ BigQuery access failed:")
        print(f"   Error: {str(e)}")
        
        if "403" in str(e):
            print("\n💡 Permission Issue Detected!")
            print("   Your service account needs BigQuery permissions.")
            return False
        elif "404" in str(e):
            print("\n💡 Project or dataset not found.")
            return False
        else:
            print("\n💡 Unknown error occurred.")
            return False


def print_setup_instructions():
    print("\n" + "="*60)
    print("📚 BigQuery Setup Instructions")
    print("="*60)
    
    project_id = os.getenv("GCP_PROJECT_ID")
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    if creds_path and os.path.exists(creds_path):
        with open(creds_path, 'r') as f:
            creds = json.load(f)
            service_account_email = creds.get('client_email')
    else:
        service_account_email = "YOUR_SERVICE_ACCOUNT_EMAIL"
    
    print(f"""
🔧 Required Permissions for Service Account:

1. Go to Google Cloud Console:
   https://console.cloud.google.com/iam-admin/iam?project={project_id}

2. Find your service account:
   {service_account_email}

3. Click "Edit" (pencil icon) and add these roles:
   ✓ BigQuery Data Viewer
   ✓ BigQuery Job User
   ✓ BigQuery Read Session User (for Storage API)

4. Alternative: Use gcloud command:
   
   gcloud projects add-iam-policy-binding {project_id} \\
     --member="serviceAccount:{service_account_email}" \\
     --role="roles/bigquery.dataViewer"
   
   gcloud projects add-iam-policy-binding {project_id} \\
     --member="serviceAccount:{service_account_email}" \\
     --role="roles/bigquery.jobUser"
   
   gcloud projects add-iam-policy-binding {project_id} \\
     --member="serviceAccount:{service_account_email}" \\
     --role="roles/bigquery.readSessionUser"

5. Enable BigQuery API:
   https://console.cloud.google.com/apis/library/bigquery.googleapis.com?project={project_id}

📖 Documentation:
   - BigQuery Client Libraries: https://cloud.google.com/bigquery/docs/reference/libraries
   - Authentication: https://cloud.google.com/docs/authentication/getting-started
   - Free Tier: 1TB queries/month free

💰 Free Tier Benefits:
   ✓ 1TB of query processing per month
   ✓ 10GB of storage per month
   ✓ Perfect for this challenge!
""")


def main():
    print("\n🚀 BigQuery Access Setup Tool\n")
    
    if not check_service_account():
        print_setup_instructions()
        return
    
    success = test_bigquery_access()
    
    if not success:
        print_setup_instructions()
        print("\n⚠️  After granting permissions, run this script again to verify.")
    else:
        print("\n" + "="*60)
        print("🎉 BigQuery Access Configured Successfully!")
        print("="*60)
        print("\n✅ You can now:")
        print("   1. Query public datasets")
        print("   2. Run the data analysis agent")
        print("   3. Use 1TB of free queries per month")
        print("\n💡 Next step:")
        print("   python build_multi_agent_system.py")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
