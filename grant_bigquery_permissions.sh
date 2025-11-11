#!/bin/bash

echo "================================================"
echo "🔧 Granting BigQuery Permissions"
echo "================================================"

PROJECT_ID="test-task-opsfleet"
SERVICE_ACCOUNT="opsfleet-test@test-task-opsfleet.iam.gserviceaccount.com"

echo ""
echo "📊 Project: $PROJECT_ID"
echo "🔑 Service Account: $SERVICE_ACCOUNT"
echo ""

echo "1️⃣  Granting BigQuery Data Viewer role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/bigquery.dataViewer" \
  --quiet

echo ""
echo "2️⃣  Granting BigQuery Job User role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/bigquery.jobUser" \
  --quiet

echo ""
echo "3️⃣  Granting BigQuery Read Session User role..."
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT" \
  --role="roles/bigquery.readSessionUser" \
  --quiet

echo ""
echo "4️⃣  Enabling BigQuery API..."
gcloud services enable bigquery.googleapis.com --project=$PROJECT_ID --quiet

echo ""
echo "================================================"
echo "✅ Permissions granted successfully!"
echo "================================================"
echo ""
echo "🧪 Testing access..."
python setup_bigquery.py
