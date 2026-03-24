import os
import asyncio

# Force ADK to use Vertex AI (Application Default Credentials) instead of Gemini API key
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "aimlexplore")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "true")

from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

async def main():
    project_id = os.environ.get("PROJECT_ID", "aimlexplore")
    location = os.environ.get("LOCATION", "us")
    collection_id = os.environ.get("COLLECTION_ID", "default_collection")
    datastore_id = os.environ.get("DATASTORE_ID", "test_1774333509084")

    # Point the tool to your automated Data Store
    search_tool = VertexAiSearchTool(
        data_store_id=f"projects/{project_id}/locations/{location}/collections/{collection_id}/dataStores/{datastore_id}"
    )

    # Initialize the agent
    my_agent = Agent(
        name="DocumentAssistant",
        model="gemini-2.0-flash",
        tools=[search_tool],
        instruction=(
            "You are a document assistant. You MUST always use the vertex_ai_search tool "
            "to look up information before answering any question. Never say you cannot "
            "access documents — always search first, then summarize what you find."
        )
    )

    # Set up runner and session
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="document_assistant",
        user_id="user1",
        session_id="session1"
    )

    runner = Runner(
        agent=my_agent,
        app_name="document_assistant",
        session_service=session_service
    )

    # Send a query
    query = "Summarize the content of the uploaded PDF document."
    print(f"Querying agent with: '{query}'\n")

    message = types.Content(role="user", parts=[types.Part(text=query)])

    async for event in runner.run_async(
        user_id="user1",
        session_id="session1",
        new_message=message
    ):
        if event.is_final_response():
            print("--- Response ---")
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        print(part.text)
            else:
                print("[No text content in response. Raw event:]")
                print(event)

if __name__ == "__main__":
    asyncio.run(main())
