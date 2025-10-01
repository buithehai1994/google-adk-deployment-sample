import os
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from google.adk.cli.fast_api import get_fast_api_app
from starlette.middleware.base import BaseHTTPMiddleware 
from dotenv import load_dotenv

load_dotenv()

# ----------------------------
# Configuration
# ----------------------------

# Directory where this file is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE_DIR = os.path.join(AGENT_DIR, "database")

# Example session service URI (SQLite)
SESSION_SERVICE_URI = f"sqlite:///{os.path.join(DATABASE_DIR, 'adk.db')}"

# Allowed origins for CORS
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]

# Serve web interface or not
SERVE_WEB_INTERFACE = True

# API Key (must be set as an environment variable)
API_KEY = os.getenv("CREDENTIALS")
if not API_KEY:
    raise RuntimeError("CREDENTIALS variable is not set")

# ----------------------------
# Create FastAPI app
# ----------------------------

app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

# Disable default docs
app.docs_url = None
app.redoc_url = None
app.openapi_url = None

# ----------------------------
# API Key Middleware
# ----------------------------

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Allow docs routes through (they still work inside Swagger UI with API key)
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        key = request.headers.get("x-api-key")
        if key != API_KEY:
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)
        return await call_next(request)


# Add middleware to protect all endpoints
app.add_middleware(APIKeyMiddleware)

# ----------------------------
# Verify API Key dependency
# ----------------------------

def verify_api_key(request: Request):
    key = request.headers.get("x-api-key")
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

# ----------------------------
# Custom protected docs
# ----------------------------

@app.get("/docs", include_in_schema=False)
def custom_swagger_ui_html():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="API Docs")

@app.get("/redoc", include_in_schema=False)
def custom_redoc_html():
    return get_redoc_html(openapi_url="/openapi.json", title="API Docs")

@app.get("/openapi.json", include_in_schema=False)
def openapi_json():
    return JSONResponse(app.openapi())


# ----------------------------
# Run Uvicorn
# ----------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
