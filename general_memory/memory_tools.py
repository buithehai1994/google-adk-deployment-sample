# memory_tools.py
import os
from pathlib import Path
from typing import List, Dict, Any, Union

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools import google_search

from .memory_service import setup_embedding_service  # Import from the new service file

gemini_model = "gemini-2.0-flash"


class MemoryTool:
    """A general-purpose tool to manage an agent's memory."""
    def __init__(self):
        db_dir = Path("./database")
        db_dir.mkdir(exist_ok=True)
        db_path = db_dir / "adk.db"
        self._session_service = setup_embedding_service(db_path)

    def _format_search_results(self, search_result: Union[List[Dict[str, Any]], str], query: str) -> str:
        """Helper to format search results for agent consumption."""
        if isinstance(search_result, str):
            return search_result
        if not search_result:
            return "No relevant memories found."

        formatted_results = [
            f"- [Similarity: {res['similarity']:.3f}] ({res.get('timestamp', 'Unknown')}): {res['content']}"
            for res in search_result
        ]
        response = f"Found {len(search_result)} relevant memories for query '{query}':\n"
        response += "\n".join(formatted_results)
        return response

    def save(self, text: str) -> str:
        """Saves any text (user query or agent response) to the memory database.
        
        Args:
            text: The text to be saved.
        
        Returns:
            A string indicating success or failure.
        """
        if not text or not text.strip():
            return "Cannot save empty or invalid text."
        
        result = self._session_service.embed_and_save(text)
        return "Text successfully saved to memory." if "Saved:" in result else result

    def query(self, query_text: str) -> str:
        """Queries memory for relevant entries based on the provided text.
        
        Args:
            query_text: The text to query the memory with.
        
        Returns:
            A formatted string of relevant memories or a status message.
        """
        if not query_text or not query_text.strip():
            return "Cannot query with empty or invalid text."
        
        query_embedding = self._session_service.embed_text(query_text, "RETRIEVAL_QUERY")
        search_result = self._session_service.search_similar(query_embedding, k=3)
        return self._format_search_results(search_result, query_text)

# Instantiate the single, reusable memory tool
memory_class = MemoryTool()

def memory_query(text: str) -> str:
    """
    Searches the agent's memory for relevant information.
    
    Args:
        text: The text query used to search the memory.
    
    Returns:
        A formatted string of relevant memories found.
    """
    return memory_class.query(text)

def memory_save(text: str) -> str:
    """
    Saves a text string to the agent's memory for future use.
    
    Args:
        text: The text string to save.
    
    Returns:
        A string confirming the save operation or an error message.
    """
    return memory_class.save(text)

# Agents / Tools

# Web search agent
search_agent = LlmAgent(
    name="Google_Search_agent",
    model=gemini_model,
    tools=[google_search],
    instruction="Use 'Google Search' to find relevant online information."
)
Web_Search_Tool = AgentTool(search_agent)

# Memory tools as agents
Save_Memory_Tool = AgentTool(
    agent=LlmAgent(
        name="Save_Memory_Manager",
        model=gemini_model,
        tools=[memory_save],
        instruction="Use memory_save tool to save both user queries and agent responses to memory."
    )
)

Query_Memory_Tool = AgentTool(
    agent=LlmAgent(
        name="Query_Memory_Manager",
        model=gemini_model,
        tools=[memory_query],
        instruction="Use memory_query tool to search memory for relevant information based on a query."
    )
)