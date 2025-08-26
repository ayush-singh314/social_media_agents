# ================================================================
# LangGraph Agentic Workflow for Video Content Creation
# This script defines a state machine to automate the process of
# downloading a video, finding viral clips with an LLM,
# validating the results, and publishing them to YouTube.
# ================================================================

import os
import subprocess
import httplib2
from dotenv import load_dotenv
from typing import List, TypedDict, Union
from pydantic import BaseModel, Field
from faster_whisper import WhisperModel
from langchain_groq import ChatGroq
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langgraph.graph import StateGraph, END

# YouTube API imports
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

# ===================== Pydantic Schema =====================
class ClipSegment(BaseModel):
    """A segment of a video to be clipped."""
    start_sec: float = Field(..., description="The start time of the clip in seconds.")
    duration_sec: float = Field(..., description="The duration of the clip in seconds.")
    caption: str = Field(..., description="A short, catchy caption for the clip.")

class ViralClips(BaseModel):
    """A list of viral video clips extracted from a transcript."""
    clips: List[ClipSegment] = Field(..., description="A list of 3 high-impact video clips.")

# ===================== LangGraph State =====================
# The state is a central source of truth for all nodes in the graph.
class GraphState(TypedDict):
    """Represents the state of our graph."""
    video_url: str
    video_file_path: str
    transcript: str
    clips: List[ClipSegment]
    validation_passed: bool
    publish_clips: bool
    user_wants_clips: bool
    error: Union[str, None]

# ===================== Load Environment Variables =====================
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# ===================== YouTube API Configuration =====================
CLIENT_SECRETS_FILE = "client_secret.json" 
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl"
]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

# ===================== Node Functions =====================

# 1. Download Video Node
def download_video(state: GraphState):
    print("Executing download_video node...")
    video_url = state["video_url"]
    output_file = "downloaded_video.mp4" # Temp file name
    try:
        subprocess.run([
            "yt-dlp", "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "-o", output_file, video_url
        ], check=True)
        print(f"Video downloaded to {output_file}.")
        return {**state, "video_file_path": output_file}
    except subprocess.CalledProcessError as e:
        print("Video download failed:", e)
        return {**state, "error": "Video download failed."}
    except FileNotFoundError as e:
        print("Download executable not found. Did you install yt-dlp?", e)
        return {**state, "error": "Download executable not found."}


# 2. Get User Validation Node
def get_user_validation(state: GraphState):
    print("Executing get_user_validation node...")
    # This node now simply reads the value from the initial state passed by the API.
    user_decision = state.get("user_wants_clips", False)
    print(f"User decision: Publish clips = {user_decision}")
    return {**state, "user_wants_clips": user_decision}


# 3. Transcribe and Clip Agent Node
def clip_video_agent(state: GraphState):
    print("Executing clip_video_agent node...")
    video_file = state["video_file_path"]

    # Transcribe the video
    try:
        model = WhisperModel("base")
        segments, _ = model.transcribe(video_file)
        full_transcript = " ".join([seg.text for seg in segments])
        print("Transcription complete.")
    except Exception as e:
        print("Transcription failed:", e)
        return {**state, "error": "Transcription failed."}
    
    # Extract impactful clips with LLM
    try:
        llm = ChatGroq(model="llama3-8b-8192", temperature=0.3)
        parser = JsonOutputParser(pydantic_object=ViralClips)

        prompt_template = PromptTemplate(
            template="""
            You are a video editor AI. Given the following transcript, return exactly 3 impactful segments for viral videos.
            Each clip should be between 20 and 40 seconds long.
            Return a JSON object adhering strictly to these instructions: {format_instructions}
            
            Transcript: {transcript}
            """,
            input_variables=["transcript"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt_template | llm | parser
        llm_output_dict = chain.invoke({"transcript": full_transcript[:1000]})
        
        viral_clips_object = ViralClips.model_validate(llm_output_dict)
        print("Clips generated by LLM.")
        return {**state, "transcript": full_transcript, "clips": viral_clips_object.clips}
    except Exception as e:
        print("LLM clipping agent failed:", e)
        return {**state, "error": "LLM clipping agent failed."}

# 4. Validation Node
def validate_clips(state: GraphState):
    print("Executing validate_clips node...")
    if state.get("clips") and len(state["clips"]) > 0:
        print("Clips validated successfully.")
        return {**state, "validation_passed": True}
    else:
        print("Clip validation failed. No clips to publish.")
        return {**state, "validation_passed": False}

# 5. Publish to YouTube Node (Handles both raw and clips)
def publish_to_youtube(state: GraphState):
    print("Executing publish_to_youtube node...")
    try:
        youtube_service = get_authenticated_service()
        
        # Publish the original video if clips are not requested or if clips are requested, too.
        if not state["user_wants_clips"] or (state["user_wants_clips"] and state["clips"]):
            print("Publishing raw video...")
            upload_to_youtube_api(
                youtube_service,
                state["video_file_path"],
                title="Raw Video Upload",
                description="This is a raw video uploaded directly from the workflow.",
                tags=["raw", "video", "upload", "automation"]
            )
        
        # If the user wants clips and they were successfully generated, publish them.
        if state["user_wants_clips"] and state["clips"]:
            print("Publishing generated clips...")
            for i, clip in enumerate(state["clips"], 1):
                output_file = f"clip_{i}_vertical.mp4"
                # Clip the video locally
                clip_video(state["video_file_path"], clip.start_sec, clip.start_sec + clip.duration_sec, output_file, aspect_ratio="9:16")

                # Upload the generated clip
                upload_to_youtube_api(
                    youtube_service,
                    output_file,
                    title=f"Viral Clip #{i} - {clip.caption}",
                    description=f"This short clip was automatically generated. \n\n#Shorts #YouTubeShorts #Viral",
                    tags=["viral", "shorts", "ai", "content creation"]
                )
        
        return {**state, "error": None}
    except Exception as e:
        print("YouTube publishing failed:", e)
        return {**state, "error": "YouTube publishing failed."}

# --- Auxiliary Functions (reused from previous conversations) ---
def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_local_server(port=0)
    return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)

def upload_to_youtube_api(youtube_client, video_file, title, description, tags, privacy_status="public"):
    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "28"
        },
        "status": {
            "privacyStatus": privacy_status
        }
    }
    media_body = MediaFileUpload(video_file, chunksize=-1, resumable=True)
    try:
        insert_request = youtube_client.videos().insert(part=",".join(body.keys()), body=body, media_body=media_body)
        response = insert_request.execute()
        print(f"Video uploaded to YouTube! Video ID: {response['id']}")
    except HttpError as e:
        print(f"An HTTP error occurred: {e.resp.status}, {e.content}")

def clip_video(video_file: str, start: float, end: float, output_file: str, aspect_ratio: str = None):
    command = [
        r"C:\ffmpeg-2025-08-18-git-0226b6fb2c-full_build\bin\ffmpeg.exe",
        "-i", video_file,
        "-ss", str(start),
        "-to", str(end)
    ]
    if aspect_ratio == "9:16":
        command.extend(["-vf", "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"])
        command.extend(["-c:v", "libx264", "-c:a", "aac"])
    else:
        command.extend(["-c", "copy"])
    command.append(output_file)
    try:
        subprocess.run(command, check=True, capture_output=True)
        print(f"Clip saved successfully: {output_file}")
    except subprocess.CalledProcessError as e:
        print("FFmpeg error:", e.stderr.decode())

# ===================== Graph Definition =====================
workflow = StateGraph(GraphState)

# Define the nodes for our workflow
workflow.add_node("download", download_video)
workflow.add_node("get_validation", get_user_validation)
workflow.add_node("clip_agent", clip_video_agent)
workflow.add_node("publish_to_youtube", publish_to_youtube)

# Set the entry point of the graph
workflow.set_entry_point("download")

# Define the edges (the flow of the graph)
workflow.add_edge("download", "get_validation")

# Add conditional logic based on user's choice
workflow.add_conditional_edges(
    "get_validation",
    # This function determines the next step based on the state.
    lambda state: "clip_agent" if state.get("user_wants_clips") else "publish_to_youtube",
    {
        "clip_agent": "clip_agent",
        "publish_to_youtube": "publish_to_youtube"
    }
)

workflow.add_edge("clip_agent", "publish_to_youtube")
workflow.add_edge("publish_to_youtube", END)

# Compile the graph
app = workflow.compile()

# ===================== Main Execution (Commented Out for API Use) =====================
# if __name__ == "__main__":
#     initial_state = {
#         "video_url": "https://drive.google.com/uc?export=download&id=1Pa9R7L2uB_vakExCnwRNhi3GM-peTK28",
#         "video_file_path": None,
#         "transcript": None,
#         "clips": [],
#         "validation_passed": False,
#         "publish_clips": True,
#         "user_wants_clips": True,
#         "error": None
#     }
#     
#     should_clip = True # or False
#
#     initial_state["user_wants_clips"] = should_clip
#     
#     print("Starting content creation workflow...")
#     for s in app.stream(initial_state):
#         print(s)
