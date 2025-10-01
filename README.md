# Google Cloud Run Deployment Instructions

A clean, step-by-step guide to deploy your application to Google Cloud Run.

---

## Prerequisites

- Google Cloud account with billing enabled
- gcloud CLI installed
- Application with Dockerfile in your project directory

---

## Step 1: Authenticate and Configure Google Cloud

### 1.1 Login to Google Cloud
```bash
gcloud auth login
```

### 1.2 Set Your Project
```bash
gcloud config set project YOUR_PROJECT_ID
```

### 1.3 Set Your Account
```bash
gcloud config set account YOUR_EMAIL@gmail.com
```

### 1.4 Set Default Region
```bash
gcloud config set run/region us-central1
```


### 1.5 Set IAM
gcloud projects add-iam-policy-binding sage-tribute-317903 --member="serviceAccount:partner-sa@sage-tribute-317903.iam.gserviceaccount.com" --role=roles/datastore.user

### 1.6 Verify Configuration
```bash
gcloud config list
```

---

## Step 2: Set Environment Variables

### Windows (CMD)
```cmd
set GOOGLE_CLOUD_PROJECT=your-project-id
set GOOGLE_CLOUD_LOCATION=us-central1
set GOOGLE_GENAI_USE_VERTEXAI=true
set GCLOUD_API_KEY=your-api-key
```

### Linux/Mac (Bash)
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI="true"
export GCLOUD_API_KEY="your-api-key"
```

---

## Step 3: Navigate to Project Directory

```bash
cd path/to/your/project
```

Ensure you're in the directory containing your `Dockerfile`.

---

## Step 4: Deploy to Cloud Run

### Windows (CMD) - Single Line
```cmd
gcloud run deploy multitool-agent-service --source . --region %GOOGLE_CLOUD_LOCATION% --memory=2Gi --cpu=2 --timeout=300s --no-allow-unauthenticated --service-account=partner-sa@%GOOGLE_CLOUD_PROJECT%.iam.gserviceaccount.com --set-env-vars="GOOGLE_CLOUD_PROJECT=%GOOGLE_CLOUD_PROJECT%,GOOGLE_CLOUD_LOCATION=%GOOGLE_CLOUD_LOCATION%,GOOGLE_GENAI_USE_VERTEXAI=%GOOGLE_GENAI_USE_VERTEXAI%,CREDENTIALS=%CREDENTIALS%,GCLOUD_API_KEY=%GCLOUD_API_KEY%"
```


### Windows (CMD) - Multi-Line
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

### Linux/Mac (Bash)
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

## Step 5: Access Your Deployed Service

After successful deployment, you'll receive a service URL:
```
Service URL: https://multitool-agent-service-XXXXXX.us-central1.run.app
```

Visit this URL to access your deployed application.

---

## Command Parameters Reference

| Parameter | Value | Description |
|-----------|-------|-------------|
| Service Name | `multitool-agent-service` | Name of your Cloud Run service |
| `--source` | `.` | Deploy from current directory |
| `--region` | `us-central1` | Google Cloud region |
| `--memory` | `2Gi` | Memory allocation (2GB) |
| `--cpu` | `2` | CPU cores allocation |
| `--timeout` | `300s` | Request timeout (5 minutes) |
| `--allow-unauthenticated` | - | Allow public access |
| `--set-env-vars` | `KEY=VALUE,...` | Environment variables |

---

## Available Regions

Common regions you can use:
- `us-central1` (Iowa)
- `us-east1` (South Carolina)
- `us-west1` (Oregon)
- `europe-west1` (Belgium)
- `asia-southeast1` (Singapore)

[Full list of regions](https://cloud.google.com/run/docs/locations)

---

## Update Existing Deployment

To update an already deployed service, run the same deploy command. Cloud Run will:
1. Build a new container image
2. Create a new revision
3. Gradually shift traffic to the new revision

---

## Useful Management Commands

### View Service Details
```bash
gcloud run services describe multitool-agent-service --region us-central1
```

### View Service Logs
```bash
gcloud run services logs read multitool-agent-service --region us-central1
```

### List All Services
```bash
gcloud run services list
```

### Delete Service
```bash
gcloud run services delete multitool-agent-service --region us-central1
```

### View Active Configuration
```bash
gcloud config list
```

### Check Authentication Status
```bash
gcloud auth list
```

---

## Critical Rules to Remember

### ✅ DO
- Use `--source .` for current directory
- Use region names like `us-central1`
- Use `%VARIABLE%` on Windows, `$VARIABLE` on Linux/Mac
- Allocate sufficient memory (minimum 2Gi recommended)
- Set timeout to 300s or higher for slower startups
- Include all required environment variables

### ❌ DON'T
- Use non-existent source directories like `temp_staging`
- Use zone names like `us-central1-a` (zones, not regions)
- Mix Windows and Linux variable syntax
- Set the `PORT` environment variable (auto-set by Cloud Run)
- Use insufficient memory causing container startup failures

---

## Quick Deployment Template

Copy and modify this template for your deployments:

```bash
# Set variables (Windows: use 'set', Linux/Mac: use 'export')
set GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
set GOOGLE_CLOUD_LOCATION=YOUR_REGION
set GOOGLE_GENAI_USE_VERTEXAI=true
set GCLOUD_API_KEY=YOUR_API_KEY

# Navigate to project
cd path/to/your/project

# Deploy (Windows: use %, Linux/Mac: use $)
gcloud run deploy YOUR_SERVICE_NAME ^
  --source . ^
  --region %GOOGLE_CLOUD_LOCATION% ^
  --memory=2Gi ^
  --cpu=2 ^
  --timeout=300s ^
  --allow-unauthenticated ^
  --set-env-vars="GOOGLE_CLOUD_PROJECT=%GOOGLE_CLOUD_PROJECT%,GOOGLE_CLOUD_LOCATION=%GOOGLE_CLOUD_LOCATION%,GOOGLE_GENAI_USE_VERTEXAI=%GOOGLE_GENAI_USE_VERTEXAI%,GCLOUD_API_KEY=%GCLOUD_API_KEY%"
```
Example: gcloud run deploy multitool-agent-service --source . --region %GOOGLE_CLOUD_LOCATION% --memory=2Gi --cpu=2 --timeout=300s --no-allow-unauthenticated --service-account=partner-sa@%GOOGLE_CLOUD_PROJECT%.iam.gserviceaccount.com --set-env-vars="GOOGLE_CLOUD_PROJECT=%GOOGLE_CLOUD_PROJECT%,GOOGLE_CLOUD_LOCATION=%GOOGLE_CLOUD_LOCATION%,GOOGLE_GENAI_USE_VERTEXAI=%GOOGLE_GENAI_USE_VERTEXAI%,GCLOUD_API_KEY=%GCLOUD_API_KEY%"

---

## Support Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [gcloud CLI Reference](https://cloud.google.com/sdk/gcloud/reference/run)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Troubleshooting Guide](https://cloud.google.com/run/docs/troubleshooting)

---

**Ready to deploy?** Follow the steps above in order, and your service will be live in minutes! 🚀