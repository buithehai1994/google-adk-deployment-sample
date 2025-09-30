import os
import sys
import uvicorn
from fastapi import FastAPI
from google.adk.cli.fast_api import get_fast_api_app
from dotenv import load_dotenv

# For MCP server
import asyncio
import json
from mcp import types as mcp_types
from mcp.server.lowlevel import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from google.adk.tools.function_tool import FunctionTool
from google.adk.tools.mcp_tool.conversion_utils import adk_to_mcp_tool_type
from google.adk.tools.openapi_tool.openapi_spec_parser.rest_api_tool import RestApiTool


load_dotenv() # Load environment variables from .env

# Set up paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# AGENT_DIR should point to the parent directory of 'my_rag_agent'
AGENT_DIR = os.path.join(BASE_DIR, "adk") 
DATABASE_DIR = os.path.join(BASE_DIR, "adk","database") 

# Example session service URI (e.g., SQLite)
SESSION_SERVICE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'sessions.db')}"

# Example allowed origins for CORS
ALLOWED_ORIGINS = ["http://localhost", "http://localhost:8080", "*"]
# Set web=True if you intend to serve a web interface, False otherwise
SERVE_WEB_INTERFACE = True


# Create the FastAPI app using ADK's helper
# This helper automatically sets up routes for your ADK agents.
app: FastAPI = get_fast_api_app(
    agents_dir=AGENT_DIR,
    allow_origins=["*"],  # Be more restrictive in production, e.g., ["http://localhost:4200"] for Angular
    web=True,  # Enable the ADK Web UI at /dev-ui
)

# Add custom endpoints
@app.get("/health")
async def health_check():
    """Simple health check endpoint."""
    return {"status": "healthy"}

@app.get("/agent-info")
async def agent_info():
    """Provide information about the configured root agent."""
    # Dynamically import the root_agent from your specific agent path
    try:
        # Import the module
        agent_module = __import__("agents.my_rag_agent", fromlist=["root_agent"])
        # Access the root_agent from the imported module
        current_root_agent = agent_module.root_agent

        tool_names = []
        # Since root_agent is a SequentialAgent, its tools are its sub_agents' tools
        # or it might have its own tools if directly assigned.
        # For this setup, we'll try to get tools from its sub_agents.
        if hasattr(current_root_agent, 'sub_agents'):
            for sub_agent in current_root_agent.sub_agents:
                if hasattr(sub_agent, 'tools'):
                    for tool in sub_agent.tools:
                        tool_names.append(tool.name)
        elif hasattr(current_root_agent, 'tools'):
             for tool in current_root_agent.tools:
                 tool_names.append(tool.name)

        return {
            "agent_name": current_root_agent.name,
            "description": current_root_agent.description,
            # SequentialAgent itself doesn't have a model directly, its sub_agents do.
            # You might want to list sub-agent models if needed.
            "model_info": "See sub-agents for model details",
            "sub_agents": [sa.name for sa in current_root_agent.sub_agents],
            "tools": sorted(list(set(tool_names))) # Get unique tool names
        }
    except Exception as e:
        return {"error": f"Could not load agent info: {e}"}, 500



# --- Main execution block ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ADK Agent Server")
    args = parser.parse_args()

    print("Starting Web server mode on http://0.0.0.0:9999...")
    print("ADK Web UI available at http://localhost:9999/dev-ui")
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=9999, 
        reload=False  # Set to True during development for auto-reloading
    )