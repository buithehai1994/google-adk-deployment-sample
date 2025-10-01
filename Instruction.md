# 🔐 Google Cloud Run Deployment Guide (Secured with API Key)

## Quick Deployment Checklist

Follow these steps for a secure deployment to Google Cloud Run.

---

## Step 1: Initial Google Cloud Setup

### 1.1 Authenticate with Google Cloud
```bash
gcloud auth login
```

**Your Actual Command:**
```cmd
D:\Job AI\AI Agent\google-adk-deployment-sample>gcloud auth login

Your browser has been opened to visit:
    https://accounts.google.com/o/oauth2/auth?response_type=code&client_id=...

You are now logged in as [haibt0206@gmail.com].
Your current project is [sage-tribute-317903].
```

This will open your browser for authentication.



### 1.2 Configure Your Project
```bash
gcloud config set project YOUR_PROJECT_ID
```

**Your Actual Command:**
```cmd
D:\Job AI\AI Agent\google-adk-deployment-sample>gcloud config set project sage-tribute-317903
Updated property [core/project].
```

Replace `YOUR_PROJECT_ID` with your actual project ID (e.g., `sage-tribute-317903`)

### 1.3 Set Default Account
```bash
gcloud config set account YOUR_EMAIL@gmail.com
```
**Your Actual Command:**
```cmd
D:\Job AI\AI Agent\google-adk-deployment-sample>gcloud config set account haibt0206@gmail.com

Updated property [core/account].
```

Replace with your Google Cloud account email.


### 1.4 Set Default Region
```bash
gcloud config set run/region us-central1
```

**Your Actual Command:**
```cmd
D:\Job AI\AI Agent\google-adk-deployment-sample>gcloud config set run/region us-central1
Updated property [run/region].
```

Or choose your preferred region.

---


## Step 2: Set Environment Variables

### For Windows (CMD)
```cmd
set GOOGLE_CLOUD_PROJECT=your-project-id
set GOOGLE_CLOUD_LOCATION=us-central1
set GOOGLE_GENAI_USE_VERTEXAI=true
set GCLOUD_API_KEY=your-secret-api-key
```

### For Linux/Mac (Bash)
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI="true"
export GCLOUD_API_KEY="your-secret-api-key"
```

**Your Actual Commands:**
```cmd
D:\Job AI\AI Agent\google-adk-deployment-sample>
set GOOGLE_CLOUD_PROJECT=sage-tribute-317903
set GOOGLE_CLOUD_LOCATION=us-central1
set GOOGLE_GENAI_USE_VERTEXAI=FALSE
set CREDENTIALS=AQ.Ab8RN6KUi1KOQRHIxFAQMFrhukCQdC6gjGr4ZydUJvFzm8quBg
set GCLOUD_API_KEY=%CREDENTIALS%  

REM Optional: Set to same value as CREDENTIALS for consistency with Instruction.md
```

**Important:** Notice that on Windows, you use `%VARIABLE%` to reference variables, NOT `$VARIABLE`

---

## Step 3: Navigate to Your Project Directory

```bash
cd path/to/your/project
```

**Your Actual Commands:**
```cmd
C:\Users\buith\AppData\Local\Google\Cloud SDK>cd D:\Job AI\AI Agent\google-adk-deployment-sample

C:\Users\buith\AppData\Local\Google\Cloud SDK>D:

D:\Job AI\AI Agent\google-adk-deployment-sample>
```

Ensure you're in the directory containing your `Dockerfile` or application code.

---
## Step 4: Deploy to Cloud Run (Secured)

⚠️ Do **NOT** use `--allow-unauthenticated`. This ensures the service is private.

### Windows (CMD)
```cmd
gcloud run deploy multitool-agent-service --source . --region %GOOGLE_CLOUD_LOCATION% --memory=2Gi --cpu=2 --timeout=300s --no-allow-unauthenticated --service-account=partner-sa@%GOOGLE_CLOUD_PROJECT%.iam.gserviceaccount.com --set-env-vars="GOOGLE_CLOUD_PROJECT=%GOOGLE_CLOUD_PROJECT%,GOOGLE_CLOUD_LOCATION=%GOOGLE_CLOUD_LOCATION%,GOOGLE_GENAI_USE_VERTEXAI=%GOOGLE_GENAI_USE_VERTEXAI%,CREDENTIALS=%CREDENTIALS%,GCLOUD_API_KEY=%GCLOUD_API_KEY%"
```

### Linux/Mac (Bash)
```bash
gcloud run deploy multitool-agent-service   --source .   --region $GOOGLE_CLOUD_LOCATION   --memory=2Gi   --cpu=2   --timeout=300s -no-allow-unauthenticated  --set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI,GCLOUD_API_KEY=$GCLOUD_API_KEY"
```

**Your Actual Successful Command:**
```cmd
D:\Job AI\AI Agent\google-adk-deployment-sample>gcloud run deploy multitool-agent-service --source . --region %GOOGLE_CLOUD_LOCATION% --memory=2Gi --cpu=2 --timeout=300s --no-allow-unauthenticated --service-account=partner-sa@%GOOGLE_CLOUD_PROJECT%.iam.gserviceaccount.com --set-env-vars="GOOGLE_CLOUD_PROJECT=%GOOGLE_CLOUD_PROJECT%,GOOGLE_CLOUD_LOCATION=%GOOGLE_CLOUD_LOCATION%,GOOGLE_GENAI_USE_VERTEXAI=%GOOGLE_GENAI_USE_VERTEXAI%,CREDENTIALS=%CREDENTIALS%,GCLOUD_API_KEY=%GCLOUD_API_KEY%"
Building using Dockerfile and deploying container to Cloud Run service [multitool-agent-service] in project [sage-tribute-317903] region [us-central1]
OK Building and deploying... Done.
  OK Uploading sources...
  OK Building Container... Logs are available at [https://console.cloud.google.com/cloud-build/builds;region=us-central1/900389be-09bd-47de-bc4a-436f1639501d?project=533078561742].
  OK Creating Revision...
  OK Routing traffic...
  OK Setting IAM Policy...
Done.
Service [multitool-agent-service] revision [multitool-agent-service-00001-tm8] has been deployed and is serving 100 percent of traffic.
Service URL: https://multitool-agent-service-533078561742.us-central1.run.app
```
---

## Step 5: Secure Cloud Run Permissions

1. Open [Cloud Run Console](https://console.cloud.google.com/run).  
2. Select your service → **Permissions** tab.  
3. Remove `allUsers → Cloud Run Invoker` (disables public access).  
4. (Optional) Add a specific **service account** with role `Cloud Run Invoker` if you want GCP-to-GCP calls.  

---

## Step 6: Enforce API Key in Your App

Example with **FastAPI**:

```python
from fastapi import FastAPI, Request, HTTPException
import os

app = FastAPI()
API_KEY = os.getenv("GOOGLE_API_KEY")

@app.middleware("http")
async def check_api_key(request: Request, call_next):
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await call_next(request)

@app.get("/hello")
def hello():
    return {"message": "Hello from secured Cloud Run!"}
```

---

## Step 7: Call the Secured API

- After successful deployment, you'll see output like:
```
Service [multitool-agent-service] revision [multitool-agent-service-00003-s2g] has been deployed and is serving 100 percent of traffic.
Service URL: https://multitool-agent-service-XXXXXX.us-central1.run.app
```

- Now every request must include the header:

```bash
curl -X GET "https://multitool-agent-service-xxxxxx.us-central1.run.app/hello"   -H "x-api-key: your-secret-api-key"
```

Unauthorized requests return `401 Unauthorized`.

---

## Step 8: Logs & Management

### View Logs
```bash
gcloud run services logs read multitool-agent-service --region us-central1
```

## Troubleshooting Common Issues

### Issue 1: "could not find source [temp_staging]"
**Your Error:**
```cmd
D:\Job AI\AI Agent\google-adk-deployment-sample>gcloud run deploy multitool-agent-service --source temp_staging --region us-central1 --project sage-tribute-317903 --cpu 2 --memory 4Gi --concurrency 10 --allow-unauthenticated

Deployment failed
ERROR: (gcloud.run.deploy) could not find source [temp_staging]
```

**Solution:** Use `--source .` to deploy from the current directory, not a non-existent folder.

---

### Issue 2: "The user-provided container failed to start"
**Your Error:**
```cmd
D:\Job AI\AI Agent\google-adk-deployment-sample>gcloud run deploy multitool-agent-service --source "." --region "us-central1" --project "sage-tribute-317903" --memory=1Gi --allow-unauthenticated

Deployment failed
ERROR: (gcloud.run.deploy) Revision 'multitool-agent-service-00001-wgs' is not ready and cannot serve traffic. The user-provided container failed to start and listen on the port defined provided by the PORT=8080 environment variable within the allocated timeout.
```

**Solution:** 
- Increase memory: `--memory=2Gi` or higher
- Increase timeout: `--timeout=300s`
- Increase CPU: `--cpu=2`
- Check your application logs in the provided Logs URL

---

### Issue 3: "Invalid value for property [api_endpoint_overrides/run]"
**Your Error:**
```cmd
D:\Job AI\AI Agent\google-adk-deployment-sample>gcloud run deploy multitool-agent-service --source temp_staging --region "$GOOGLE_CLOUD_LOCATION" --memory=1Gi --allow-unauthenticated

ERROR: (gcloud.run.deploy) Invalid value for property [api_endpoint_overrides/run]: The endpoint_overrides property must be an absolute URI beginning with http:// or https:// and ending with a trailing '/'. [https://$GOOGLE_CLOUD_LOCATION-run.googleapis.com/] is not a valid endpoint override.
```

**Solution:** 
- On Windows, use `%VARIABLE%` syntax, not `$VARIABLE`
- Linux/Mac uses `$VARIABLE`

**Your Wrong Command (Windows):**
```cmd
--region "$GOOGLE_CLOUD_LOCATION"  ❌ Wrong for Windows
```

**Your Correct Command (Windows):**
```cmd
--region %GOOGLE_CLOUD_LOCATION%   ✅ Correct for Windows
```

---

### Issue 4: "The following reserved env names were provided: PORT"
**Your Error:**
```cmd
D:\Job AI\AI Agent\google-adk-deployment-sample>gcloud run deploy multitool-agent-service --source . --region %GOOGLE_CLOUD_LOCATION% --memory=2Gi --cpu=2 --timeout=300s --allow-unauthenticated --set-env-vars="GOOGLE_CLOUD_PROJECT=%GOOGLE_CLOUD_PROJECT%,GOOGLE_CLOUD_LOCATION=%GOOGLE_CLOUD_LOCATION%,GOOGLE_GENAI_USE_VERTEXAI=%GOOGLE_GENAI_USE_VERTEXAI%,PORT=8080,GCLOUD_API_KEY=%GCLOUD_API_KEY%"

Deployment failed
ERROR: (gcloud.run.deploy) spec.template.spec.containers[0].env: The following reserved env names were provided: PORT. These values are automatically set by the system.
```

**Solution:** Remove `PORT=8080` from your `--set-env-vars`. Cloud Run sets this automatically.

---

### Issue 5: "Region should be specified as us-central1"
**Your Error:**
```cmd
D:\Job AI\AI Agent\google-adk-deployment-sample>set GOOGLE_CLOUD_LOCATION=us-central1-a

ERROR: (gcloud.run.deploy) INVALID_ARGUMENT: Request contains an invalid argument.
```

**Solution:** Use region name (us-central1), not zone name (us-central1-a)

**Wrong:**
```cmd
set GOOGLE_CLOUD_LOCATION=us-central1-a  ❌ This is a ZONE
```

**Correct:**
```cmd
set GOOGLE_CLOUD_LOCATION=us-central1    ✅ This is a REGION
```

---

### Issue 6: Environment variables not recognized
**Your Error:**
```cmd
D:\Job AI\AI Agent\google-adk-deployment-sample>echo %GOOGLE_CLOUD_PROJECT%
%GOOGLE_CLOUD_PROJECT%  ← Variable not set!
```

**Solution:** Make sure you've run the `set` commands to define your environment variables first.

---

## View Service Logs

```bash
gcloud run services logs read multitool-agent-service --region us-central1
```

---

## Delete Service

If you need to delete the service:
```bash
gcloud run services delete multitool-agent-service --region us-central1
```

---

## Quick Reference: One-Line Deploy

### Windows
```cmd
gcloud run deploy multitool-agent-service --source . --region us-central1 --memory=2Gi --cpu=2 --timeout=300s --allow-unauthenticated --set-env-vars="GOOGLE_CLOUD_PROJECT=your-project-id,GOOGLE_CLOUD_LOCATION=us-central1,GOOGLE_GENAI_USE_VERTEXAI=true,GCLOUD_API_KEY=your-key"
```

### Linux/Mac
```bash
gcloud run deploy multitool-agent-service --source . --region us-central1 --memory=2Gi --cpu=2 --timeout=300s --allow-unauthenticated --set-env-vars="GOOGLE_CLOUD_PROJECT=your-project-id,GOOGLE_CLOUD_LOCATION=us-central1,GOOGLE_GENAI_USE_VERTEXAI=true,GCLOUD_API_KEY=your-key"
```

---

---

✅ Your Cloud Run service is now **private** and secured by **API key authentication**.
