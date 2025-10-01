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
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(AGENT_DIR, "database")
SESSION_SERVICE_URI = f"sqlite:///{os.path.join(DATABASE_DIR, 'adk.db')}"
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080"]
SERVE_WEB_INTERFACE = True

API_KEY = os.getenv("CREDENTIALS")
if not API_KEY:
    raise RuntimeError("CREDENTIALS variable is not set")

# ----------------------------
# FastAPI app
# ----------------------------
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    session_service_uri=SESSION_SERVICE_URI,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

# ----------------------------
# API Key Middleware
# ----------------------------
class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Exempt OpenAPI/Swagger static paths but still protect API endpoints
        exempt_paths = []
        if any(request.url.path.startswith(p) for p in exempt_paths):
            return await call_next(request)

        key = request.headers.get("x-api-key")
        if key != API_KEY:
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)

        return await call_next(request)

app.add_middleware(APIKeyMiddleware)

# ----------------------------
# Swagger / ReDoc with API Key prompt
# ----------------------------
@app.get("/docs", include_in_schema=False)
@app.get("/docs/", include_in_schema=False)
def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="API Docs",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

@app.get("/redoc", include_in_schema=False)
@app.get("/redoc/", include_in_schema=False)
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
