import os

# Force ADK to use Vertex AI (Application Default Credentials) instead of Gemini API key
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "aimlexplore")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")

from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool

project_id = os.environ.get("PROJECT_ID", "aimlexplore")
location = os.environ.get("LOCATION", "us")
collection_id = os.environ.get("COLLECTION_ID", "default_collection")
datastore_id = os.environ.get("DATASTORE_ID", "test_1774333509084")

# Point the tool to your Vertex AI Search Data Store
search_tool = VertexAiSearchTool(
    data_store_id=(
        f"projects/{project_id}/locations/{location}"
        f"/collections/{collection_id}/dataStores/{datastore_id}"
    )
)

# ADK web framework requires a module-level `root_agent` variable
root_agent = Agent(
    name="DocumentAssistant",
    model="gemini-2.0-flash",
    tools=[search_tool],
    instruction=(
        "You are a document assistant with access to a Vertex AI Search data store. "
        "You MUST always use the vertex_ai_search tool to look up information before "
        "answering any question. Search the data store first, then provide a clear, "
        "well-cited answer based on the retrieved chunks. If nothing is found, say so."
    )
)
