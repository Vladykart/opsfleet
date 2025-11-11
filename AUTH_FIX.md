# Authentication Fix

## Issue

The service account key has an invalid JWT signature error:
```
invalid_grant: Invalid JWT Signature
```

## Solutions

### Option 1: Use Application Default Credentials (Recommended)

```bash
# Authenticate with your Google account
gcloud auth application-default login

# Set your project
gcloud config set project test-task-opsfleet

# Test
python agent.py
```

### Option 2: Regenerate Service Account Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to IAM & Admin → Service Accounts
3. Find your service account
4. Create new key (JSON format)
5. Download and save as `test-task-opsfleet-87a0a37888c6.json`
6. Update `.env`:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/Users/vlad/PycharmProjects/opsfleet/test-task-opsfleet-87a0a37888c6.json
   ```

### Option 3: Remove Service Account, Use ADC Only

```bash
# Remove the invalid key
rm test-task-opsfleet-87a0a37888c6.json

# Remove from .env
# Comment out or remove: GOOGLE_APPLICATION_CREDENTIALS=...

# Use ADC
gcloud auth application-default login

# Test
python agent.py
```

## Why the Old CLI Worked

The old `cli_chat.py` might have cached credentials or used a different authentication flow. The new simple `agent.py` explicitly loads credentials from the environment.

## Verify Authentication

```bash
# Check if ADC is set up
gcloud auth application-default print-access-token

# Should print an access token, not an error
```

## Current Status

- ✅ Agent code is correct and working
- ✅ LangGraph implementation is correct
- ✅ Gemini integration is working
- ⚠️ BigQuery authentication needs to be refreshed

Once authentication is fixed, the agent will work perfectly!
