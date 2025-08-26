
import asyncio
import json
import time
import re
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse, PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import AsyncGenerator, List, Optional
import os
from dotenv import load_dotenv
try:
    # Optional import for YouTube publishing workflow
    from publishing_agent import app as youtube_publishing_app
except Exception:
    youtube_publishing_app = None

try:
    # Optional import for YouTube comments analysis workflow
    from analysis_agent import build_graph as build_analysis_graph
    analysis_app = build_analysis_graph()
except Exception:
    analysis_app = None

# Load environment variables
load_dotenv()

# LLM/Workflow imports
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from ideation_workflow_alpha import (
    IdeasList,
    Idea as IdeaModel,
    draft_linkedin_post as workflow_draft_linkedin_post,
    draft_youtube_script as workflow_draft_youtube_script,
    upload_media_to_linkedin as workflow_upload_media_to_linkedin,
    publish_to_linkedin as workflow_publish_to_linkedin,
    AgentState,
)

# Note: We'll import the workflow functions directly when needed
# from ideation_workflow_alpha import app as ideation_app, AgentState

# --- FastAPI App Initialization ---
app_fastapi = FastAPI(
    title="Content Ideation Agent API",
    description="An API for generating content ideas and publishing to LinkedIn/YouTube",
    version="1.0.0"
)

# Add CORS middleware
app_fastapi.add_middleware(
    CORSMiddleware,
    allow_origins=["*", "http://127.0.0.1:5501", "http://localhost:5501"],  # Allow live server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Request/Response Models ---
class IdeationRequest(BaseModel):
    user_niche: str
    platform_choice: str
    media_url: Optional[str] = None

class ContentIdea(BaseModel):
    title: str
    summary: str

class IdeationResponse(BaseModel):
    ideas: List[ContentIdea]
    platform: str
    niche: str

class PostDraftRequest(BaseModel):
    selected_idea: ContentIdea
    platform: str
    niche: str
    media_url: Optional[str] = None

class PostDraftResponse(BaseModel):
    post_draft: str
    platform: str

class PublishRequest(BaseModel):
    post_draft: str
    platform: str
    media_url: Optional[str] = None

class PublishResponse(BaseModel):
    success: bool
    message: str
    post_id: Optional[str] = None

class YouTubePublishInput(BaseModel):
    video_link: str
    is_clip: bool

# --- Utilities ---
def _make_json_safe(value):
    """Recursively convert Pydantic models and complex types to JSON-safe structures."""
    try:
        from pydantic import BaseModel as _PydBase
    except Exception:
        _PydBase = BaseModel  # fallback

    if isinstance(value, _PydBase):
        try:
            return value.model_dump()
        except Exception:
            # pydantic v1 fallback
            return value.dict()
    if isinstance(value, dict):
        return {k: _make_json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_make_json_safe(v) for v in value]
    return value

class YouTubeAnalysisInput(BaseModel):
    video_link: str

class SponsorshipInput(BaseModel):
    niche: str

# --- API Endpoints ---

@app_fastapi.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Content Ideation Agent API",
        "version": "1.0.0",
        "endpoints": {
            "POST /api/generate-ideas": "Generate content ideas",
            "POST /api/draft-post": "Draft a post/script",
            "POST /api/publish": "Publish content",
            "GET /api/health": "Health check"
        }
    }

@app_fastapi.get("/api/health")
async def health_check():
    """Health check endpoint"""
    print("Health check endpoint called")
    return {"status": "healthy", "service": "Content Ideation Agent"}

@app_fastapi.post("/api/generate-ideas")
async def generate_ideas(request: IdeationRequest):
    """Generate content ideas based on niche and platform"""
    print(f"Received request: {request}")
    try:
        # Create initial state
        initial_state = {
            "user_niche": request.user_niche,
            "platform_choice": request.platform_choice,
            "media_url": request.media_url,
            "content_ideas": None,
            "selected_idea": None,
            "post_draft": None,
            "script_draft": None,
            "user_input": "",
            "error": None,
            "media_asset_urn": None
        }
        
        print(f"Processing request for niche: {request.user_niche}, platform: {request.platform_choice}")
        
        # Use LLM to generate ideas
        llm = ChatGroq(model="llama3-8b-8192", temperature=0.5)
        parser = JsonOutputParser(pydantic_object=IdeasList)
        prompt = PromptTemplate(
            template="""
            You are a content trend analyst for {platform}.
            Based on the niche: {user_niche}, generate 5 highly engaging content ideas.
            Return ONLY a JSON object that adheres strictly to the following schema. Do NOT include any conversational text, code block syntax, or any other formatting.
            
            {format_instructions}
            """,
            input_variables=["user_niche", "platform"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt | llm | parser
        ideas_dict = chain.invoke({"user_niche": request.user_niche, "platform": request.platform_choice})

        ideas_model = IdeasList.model_validate(ideas_dict)
        ideas = [
            {"title": idea.title, "summary": idea.summary}
            for idea in ideas_model.ideas
        ]
        
        print(f"Generated {len(ideas)} ideas")
        
        response = {
            "ideas": ideas,
            "platform": request.platform_choice,
            "niche": request.user_niche
        }
        
        print(f"Returning response: {response}")
        return response
        
    except Exception as e:
        print(f"Error in generate_ideas: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating ideas: {str(e)}")

@app_fastapi.post("/api/draft-post")
async def draft_post(request: PostDraftRequest):
    """Draft a post or script based on selected idea"""
    try:
        if request.platform == "linkedin":
            # Use workflow function to draft LinkedIn post via LLM
            state: AgentState = {
                "user_niche": request.niche,
                "platform_choice": "linkedin",
                "content_ideas": None,
                "selected_idea": IdeaModel(title=request.selected_idea.title, summary=request.selected_idea.summary),
                "post_draft": None,
                "script_draft": None,
                "user_input": "",
                "error": None,
                "media_url": request.media_url,
                "media_asset_urn": None,
            }
            new_state = workflow_draft_linkedin_post(state)
            if new_state.get("error"):
                raise HTTPException(status_code=500, detail=new_state["error"])
            post_draft = new_state.get("post_draft") or ""
        else:
            # Use workflow function to draft YouTube script via LLM
            state: AgentState = {
                "user_niche": request.niche,
                "platform_choice": "youtube",
                "content_ideas": None,
                "selected_idea": IdeaModel(title=request.selected_idea.title, summary=request.selected_idea.summary),
                "post_draft": None,
                "script_draft": None,
                "user_input": "",
                "error": None,
                "media_url": request.media_url,
                "media_asset_urn": None,
            }
            new_state = workflow_draft_youtube_script(state)
            if new_state.get("error"):
                raise HTTPException(status_code=500, detail=new_state["error"])
            post_draft = new_state.get("script_draft") or ""
        
        return {
            "post_draft": post_draft,
            "platform": request.platform
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error drafting post: {str(e)}")

@app_fastapi.post("/api/publish")
async def publish_content(request: PublishRequest):
    """Publish content to the selected platform"""
    try:
        if request.platform == "linkedin":
            # Build state and optionally upload media, then publish
            state: AgentState = {
                "user_niche": "",
                "platform_choice": "linkedin",
                "content_ideas": None,
                "selected_idea": None,
                "post_draft": request.post_draft,
                "script_draft": None,
                "user_input": "",
                "error": None,
                "media_url": request.media_url,
                "media_asset_urn": None,
            }

            if request.media_url:
                state = workflow_upload_media_to_linkedin(state)
                if state.get("error"):
                    raise HTTPException(status_code=500, detail=state["error"])

            state = workflow_publish_to_linkedin(state)
            if state.get("error"):
                raise HTTPException(status_code=500, detail=state["error"])

            message = "Successfully published to LinkedIn"
            post_id = None
        else:
            # For YouTube, we only return script (no API integration here)
            message = "YouTube script prepared (no direct publish integration)"
            post_id = None

        return {
            "success": True,
            "message": message,
            "post_id": post_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing content: {str(e)}")

# --- FIX: New endpoint to handle the OAuth 2.0 callback ---
@app_fastapi.get("/callback")
async def callback(request: Request):
    """
    Receives the authorization code from LinkedIn and prints it to the console.
    """
    code = request.query_params.get("code")
    state = request.query_params.get("state")
    
    if code:
        print("\n" + "="*50)
        print("Received Authorization Code from LinkedIn!")
        print(f"Code: {code}")
        print(f"State: {state}")
        print("="*50 + "\n")
        return PlainTextResponse("Authorization successful! You can now copy the code from the server's terminal.")
    else:
        return PlainTextResponse("Error: No authorization code received.")

# --- Static Files for Frontend ---
# Create a static directory for the frontend
os.makedirs("static", exist_ok=True)
app_fastapi.mount("/static", StaticFiles(directory="static"), name="static")

# --- YouTube Publishing Agent Integration ---
@app_fastapi.post("/api/youtube/publish")
async def youtube_publish(input: YouTubePublishInput):
    """Stream the YouTube publishing workflow (download → optional clips → upload)."""
    if youtube_publishing_app is None:
        raise HTTPException(status_code=500, detail="YouTube publishing agent not available")

    initial_state = {
        "video_url": input.video_link,
        "user_wants_clips": input.is_clip,
        "video_file_path": None,
        "transcript": None,
        "clips": [],
        "validation_passed": False,
        "publish_clips": True,
        "error": None,
    }

    async def stream_results() -> AsyncGenerator:
        async for state_update in youtube_publishing_app.astream(initial_state):
            safe_update = _make_json_safe(state_update)
            yield f"data: {json.dumps(safe_update)}\n\n"

    return StreamingResponse(stream_results(), media_type="text/event-stream")

# --- YouTube Comments Analysis Integration ---
@app_fastapi.post("/api/youtube/analyze")
async def youtube_analyze(input: YouTubeAnalysisInput):
    """Analyze YouTube comments for a single video URL and return a report."""
    if analysis_app is None:
        raise HTTPException(status_code=500, detail="YouTube analysis agent not available")

    initial_state = {"video_url": input.video_link}
    # Provide a simple thread id for stateful runs (InMemorySaver requires it)
    config = {"configurable": {"thread_id": f"yt-analysis-{hash(input.video_link) & 0xffff}"}}

    try:
        final_state = analysis_app.invoke(initial_state, config=config)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    report = final_state.get("report") if isinstance(final_state, dict) else None
    if not report:
        raise HTTPException(status_code=500, detail="Analysis produced no report")

    return {"report": report}

# --- Test Endpoint ---
@app_fastapi.get("/api/sponsorship/test")
async def sponsorship_test():
    """Test endpoint to verify sponsorship functionality."""
    return {
        "message": "Sponsorship endpoint is working!",
        "available_endpoints": [
            "POST /api/sponsorship/send - Send sponsorship emails",
            "GET /api/sponsorship/test - This test endpoint"
        ],
        "example_request": {
            "niche": "marketing_mails"
        }
    }

# --- Sponsorship Agent Integration ---
@app_fastapi.post("/api/sponsorship/send")
async def sponsorship_send(input: SponsorshipInput):
    """Send sponsorship emails to companies in a specific niche from assets.json."""
    
    print(f"DEBUG: Requested niche: {input.niche}")
    
    # Read emails from assets.json for the specified niche
    try:
        with open('assets.json', 'r', encoding='utf-8') as f:
            assets_data = json.load(f)
            print(f"DEBUG: Assets data keys: {list(assets_data.keys())}")
            
            if input.niche not in assets_data:
                available_niches = list(assets_data.keys())
                raise HTTPException(
                    status_code=404, 
                    detail=f"Niche '{input.niche}' not found. Available niches: {available_niches}"
                )
            
            emails = assets_data[input.niche]
            print(f"DEBUG: Found emails: {emails}")
            
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="assets.json file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid assets.json format")

    if not emails:
        raise HTTPException(status_code=404, detail=f"No emails found for niche: {input.niche}")

    try:
        # Step 1: Draft the sponsorship email using LLM
        print("Drafting sponsorship email...")
        llm = ChatGroq(model="llama3-8b-8192")
        
        draft_prompt = PromptTemplate.from_template(
            """
            You are an expert ghostwriter for a social media influencer. Your task is to draft a professional, concise, and compelling sponsorship email.
            Here is the influencer's data:
            - Niche: {niche}
            - YouTube Subscribers: 55000
            - Instagram Followers: 15000
            - LinkedIn Followers: 8000
            - YouTube Profile: youtube.com/mytechchannel
            - Instagram Profile: instagram.com/mytechchannel
            - LinkedIn Profile: linkedin.com/in/mytechchannel
            
            Draft a short email suitable for a marketing department. The tone should be friendly yet professional. 
            Clearly state the influencer's niche, audience size, and a brief value proposition. 
            Do not include a subject line or a salutation (e.g., "Hi,"). 
            End with "Best regards," followed by "Influencer's Name".
            
            Draft:
            """
        )
        
        chain = draft_prompt | llm
        email_content = chain.invoke({"niche": input.niche}).content
        print(f"Email drafted: {email_content[:100]}...")
        
        # Step 2: Send the emails using SMTP
        print(f"Sending emails to {len(emails)} recipients...")
        email_address = os.environ.get('EMAIL_ADDRESS')
        email_password = os.environ.get('EMAIL_PASSWORD')

        if not email_address or not email_password:
            raise HTTPException(status_code=500, detail="EMAIL_ADDRESS or EMAIL_PASSWORD environment variable not set.")

        msg = MIMEMultipart()
        msg["From"] = email_address
        msg["To"] = ", ".join(emails)
        msg["Subject"] = 'Sponsorship Inquiry'
        msg.attach(MIMEText(email_content, "plain"))

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_address, email_password.replace(" ", ""))
        server.sendmail(email_address, emails, msg.as_string())
        server.quit()
        
        print("Emails sent successfully!")
        
        return {
            "success": True,
            "niche": input.niche,
            "emails_found": len(emails),
            "emails_sent": emails,
            "email_content": email_content,
            "message": f"Successfully sent emails to {len(emails)} recipients."
        }
        
    except Exception as e:
        print(f"Error in sponsorship workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Sponsorship workflow failed: {str(e)}")

# Create the app instance
app = app_fastapi

if __name__ == "__main__":
    import uvicorn
    print("Starting Content Ideation Agent API Server...")
    print("Server will be available at:")
    print("  - Local: http://127.0.0.1:8000")
    print("  - Network: http://0.0.0.0:8000")
    print("  - Frontend: http://127.0.0.1:8000/static/")
    print("  - API Docs: http://127.0.0.1:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    uvicorn.run(
        "server:app", 
        host="0.0.0.0", 
        port=8000,
        log_level="info",
        access_log=True,
        reload=False
    )
