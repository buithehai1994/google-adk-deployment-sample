# main_agent.py
import os
from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool
from dotenv import load_dotenv

from .memory_tools import Save_Memory_Tool, Query_Memory_Tool, Web_Search_Tool 

load_dotenv()
gemini_model = "gemini-2.0-flash"

# Demonstration of a root agent using the simplified tools
root_agent = LlmAgent(
    name="root_agent",
    model=gemini_model,
    tools=[Save_Memory_Tool, Query_Memory_Tool, Web_Search_Tool],
    instruction="""
    You are a memory-enabled assistant.

    Workflow:
    1. Save the user's initial query with `Save_Memory_Tool`.
    2. Search memory with `Query_Memory_Tool`.
    3. If not enough, use `Web_Search_Tool`.
    4. Save web search results to memory with `Save_Memory_Tool`.
    5. Answer the user.
    """
)
