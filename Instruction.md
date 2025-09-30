# Google Cloud Run Deployment Guide

## Quick Deployment Checklist

Complete these steps in order for a successful deployment to Google Cloud Run.

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

### 1.3 Set Your Account
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
set GCLOUD_API_KEY=your-api-key-here
```

**Your Actual Commands:**
```cmd
D:\Job AI\AI Agent\google-adk-deployment-sample>set GOOGLE_CLOUD_PROJECT=sage-tribute-317903

D:\Job AI\AI Agent\google-adk-deployment-sample>set GOOGLE_CLOUD_LOCATION=us-central1

D:\Job AI\AI Agent\google-adk-deployment-sample>echo %GOOGLE_CLOUD_PROJECT%
sage-tribute-317903
```

**Important:** Notice that on Windows, you use `%VARIABLE%` to reference variables, NOT `$VARIABLE`

### For Linux/Mac (Bash)
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI="true"
export GCLOUD_API_KEY="your-api-key-here"
```

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

## Step 4: Deploy to Cloud Run

### For Windows (CMD)
```cmd
gcloud run deploy multitool-agent-service ^
  --source . ^
  --region %GOOGLE_CLOUD_LOCATION% ^
  --memory=2Gi ^
  --cpu=2 ^
  --timeout=300s ^
  --allow-unauthenticated ^
  --set-env-vars="GOOGLE_CLOUD_PROJECT=%GOOGLE_CLOUD_PROJECT%,GOOGLE_CLOUD_LOCATION=%GOOGLE_CLOUD_LOCATION%,GOOGLE_GENAI_USE_VERTEXAI=%GOOGLE_GENAI_USE_VERTEXAI%,GCLOUD_API_KEY=%GCLOUD_API_KEY%"
```

**Your Actual Successful Command:**
```cmd
D:\Job AI\AI Agent\google-adk-deployment-sample>gcloud run deploy multitool-agent-service --source . --region %GOOGLE_CLOUD_LOCATION% --memory=2Gi --cpu=2 --timeout=300s --allow-unauthenticated --set-env-vars="GOOGLE_CLOUD_PROJECT=%GOOGLE_CLOUD_PROJECT%,GOOGLE_CLOUD_LOCATION=%GOOGLE_CLOUD_LOCATION%,GOOGLE_GENAI_USE_VERTEXAI=%GOOGLE_GENAI_USE_VERTEXAI%,GCLOUD_API_KEY=%GCLOUD_API_KEY%"

Building using Dockerfile and deploying container to Cloud Run service [multitool-agent-service] in project [sage-tribute-317903] region [us-central1]
OK Building and deploying... Done.
  OK Uploading sources...
  OK Building Container... Logs are available at [https://console.cloud.google.com/cloud-build/builds;region=us-central1/190a683a-e8b2-43af-925d-4219534f0be4?project=533078561742].
  OK Creating Revision...
  OK Routing traffic...
  OK Setting IAM Policy...
Done.
Service [multitool-agent-service] revision [multitool-agent-service-00003-s2g] has been deployed and is serving 100 percent of traffic.
Service URL: https://multitool-agent-service-533078561742.us-central1.run.app
```

### For Linux/Mac (Bash)
```bash
gcloud run deploy multitool-agent-service \
  --source . \
  --region $GOOGLE_CLOUD_LOCATION \
  --memory=2Gi \
  --cpu=2 \
  --timeout=300s \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=$GOOGLE_CLOUD_PROJECT,GOOGLE_CLOUD_LOCATION=$GOOGLE_CLOUD_LOCATION,GOOGLE_GENAI_USE_VERTEXAI=$GOOGLE_GENAI_USE_VERTEXAI,GCLOUD_API_KEY=$GCLOUD_API_KEY"
```

---

## Step 5: Verify Deployment

After successful deployment, you'll see output like:
```
Service [multitool-agent-service] revision [multitool-agent-service-00003-s2g] has been deployed and is serving 100 percent of traffic.
Service URL: https://multitool-agent-service-XXXXXX.us-central1.run.app
```

Test your service by visiting the Service URL.

---

## Command Parameters Explained

| Parameter | Description |
|-----------|-------------|
| `--source .` | Deploy from current directory |
| `--region` | Google Cloud region (e.g., us-central1) |
| `--memory=2Gi` | Allocate 2GB of memory |
| `--cpu=2` | Allocate 2 CPU cores |
| `--timeout=300s` | Set timeout to 300 seconds (5 minutes) |
| `--allow-unauthenticated` | Allow public access without authentication |
| `--set-env-vars` | Set environment variables for your application |

---

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

## Update Existing Service

To update an already deployed service, simply run the same deploy command again. Cloud Run will create a new revision and route traffic to it.

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

## Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference/run/deploy)
- [Cloud Run Troubleshooting](https://cloud.google.com/run/docs/troubleshooting)

---

**Last Updated:** September 30, 2025