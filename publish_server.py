
import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse, PlainTextResponse
from pydantic import BaseModel
from typing import AsyncGenerator

# NOTE: This assumes your LangGraph code is saved in a file named
# 'publishing_workflow.py' and contains the compiled 'app' variable
# and the 'GraphState' class.
from publishing_workflow_alpha import app, GraphState

# --- FastAPI App Initialization ---
app_fastapi = FastAPI(
    title="LangGraph Video Clipper Agent",
    description="An API to process a video and generate viral clips.",
    version="1.0.0"
)

# --- API Request Body Model ---
# This Pydantic model defines the structure of the incoming request body.
class ApiInput(BaseModel):
    video_url: str
    is_clip: bool  # Corresponds to 'user_wants_clips' in the LangGraph state

# --- API Endpoint ---
@app_fastapi.post("/invoke-workflow")
async def invoke_workflow(input: ApiInput):
    """
    Invokes the LangGraph workflow and streams the state updates back to the client.
    
    Args:
        input (ApiInput): The input data for the workflow, including the video URL
                          and whether or not to generate clips.
    """
    # Create the initial state for the LangGraph workflow from the API input.
    initial_state = {
        "video_url": input.video_url,
        "user_wants_clips": input.is_clip,
        "video_file_path": None,
        "transcript": None,
        "clips": [],
        "validation_passed": False,
        "publish_clips": True,
        "error": None
    }

    # Define an async generator to stream the results from LangGraph.
    async def stream_results() -> AsyncGenerator:
        # The 'astream' method is used for asynchronous streaming from the graph.
        async for state_update in app.astream(initial_state):
            # Format each state update as a JSON object for the client.
            # The 'data: ' prefix and '\n\n' suffix are crucial for
            # Server-Sent Events (SSE) which allows real-time streaming.
            yield f"data: {json.dumps(state_update)}\n\n"

    # Return a StreamingResponse with the generator.
    return StreamingResponse(stream_results(), media_type="text/event-stream")
