# All code is self-contained and runnable within this block.
# Remember to install the required libraries:
# pip install langchain langchain-community langchain-core langgraph 'pydantic<2' langchain-groq langchain-openai google-api-python-client

# --- 1. Import necessary libraries ---
import os
import re
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, AnyMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_groq import ChatGroq
# from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import time
from googleapiclient.discovery import build # New import for the YouTube API

# --- 2. Set API Keys and Environment Variables ---
# The following variables have been set based on your request.
os.environ['GROQ_API_KEY'] = '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'
os.environ['LANGCHAIN_API_KEY'] = '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'
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_PROJECT'] = 'simple_bot'
os.environ['OPENAI_API_KEY'] = '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'
os.environ['CLIENT_ID'] = '77wzb7dwjnk4u8'
os.environ['YOUTUBE_API_KEY'] = 'AIzaSyDDxAGDypbUqpvqfZ34hP-rxF6B-b8JiZM'


# --- 3. Define the Agent's State ---
# This is the shared data that flows through our graph.
# 'messages' will store the conversation history.
# 'video_url' will be the initial input.
# 'comments' will store the list of fetched comments.
# 'analysis' will store the LLM's structured analysis of the comments.
# 'report' will store the final summary report.
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    video_url: str
    comments: str
    analysis: str
    report: str

# --- 4. Define the Tools (Nodes that perform actions) ---

@tool
def youtube_comment_fetcher(video_url: str) -> str:
    """
    A tool to fetch real comments from a YouTube video using the YouTube Data API.

    Args:
        video_url: The URL of the YouTube video to fetch comments from.

    Returns:
        A formatted string containing the fetched comments, or an error message.
    """
    # 1. Extract the video ID from the URL
    video_id_match = re.search(r"v=([a-zA-Z0-9_-]{11})", video_url)
    if not video_id_match:
        return "Error: Invalid YouTube video URL."
    video_id = video_id_match.group(1)

    # 2. Get the API key from environment variables
    api_key = os.environ.get('YOUTUBE_API_KEY')
    if not api_key:
        return "Error: YOUTUBE_API_KEY environment variable not set."

    # 3. Build the YouTube API service object
    youtube = build('youtube', 'v3', developerKey=api_key)

    comments_list = []
    next_page_token = None
    max_comments = 25 # Limit the number of comments to avoid exceeding API quota

    print(f"\n--- Calling tool: youtube_comment_fetcher for {video_url} ---")
    
    # 4. Loop to fetch all comments (API returns them in pages)
    try:
        while True:
            request = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                maxResults=100,  # Maximum number of results per page
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response['items']:
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments_list.append(comment)
                if len(comments_list) >= max_comments:
                    break
            
            if len(comments_list) >= max_comments:
                break

            next_page_token = response.get('nextPageToken')
            if not next_page_token:
                break
    except Exception as e:
        return f"An API error occurred: {e}"

    if not comments_list:
        return "No comments found for this video."
    
    formatted_comments = "\n".join([f"- {comment}" for comment in comments_list])
    
    print("--- Tool execution successful. Comments fetched. ---")
    return f"Comments from the video at {video_url}:\n{formatted_comments}"

# This is a standard LangChain tool definition, which can be called by the agent.
tools = [youtube_comment_fetcher]

# --- 5. Define the LLM and the Agent's Nodes ---

# Initialize the LLM with the provided credentials.
# Using Groq's Llama 3 8B model for fast inference.
llm = ChatGroq(model="llama3-8b-8192")

# Alternatively, you could use an OpenAI model like this:
# llm = ChatOpenAI(model="gpt-4o-mini")

def analyze_comments_node(state: AgentState):
    """
    Node to use an LLM to analyze the sentiment of the fetched comments.
    """
    print("--- Executing node: analyze_comments_node ---")
    comments = state['comments']
    
    analysis_prompt = PromptTemplate.from_template(
        """
        You are an expert sentiment analyst. Your task is to analyze a list of YouTube comments.
        Provide a structured breakdown of the sentiment (positive, negative, neutral) and
        identify the key themes or topics mentioned in the comments.

        Comments to analyze:
        {comments}

        Analysis:
        - Overall Sentiment:
        - Key Themes:
        - Positive Comments: (Quote 2-3 examples)
        - Negative Comments: (Quote 2-3 examples)
        - Neutral/Other Comments: (Quote 2-3 examples)
        """
    )
    
    chain = analysis_prompt | llm
    analysis = chain.invoke({"comments": comments})
    
    print("--- Comment analysis complete. ---")
    return {"analysis": analysis.content}

def generate_report_node(state: AgentState):
    """
    Node to use an LLM to generate a final, comprehensive report.
    """
    print("--- Executing node: generate_report_node ---")
    analysis = state['analysis']
    video_url = state['video_url']

    report_prompt = PromptTemplate.from_template(
        """
        You are a social media analyst. Based on the following sentiment analysis,
        generate a professional and concise report for a client. The report should
        summarize the key findings and provide actionable insights.

        Video URL: {video_url}
        
        Comment Analysis:
        {analysis}

        Final Report:
        """
    )
    
    chain = report_prompt | llm
    report = chain.invoke({"analysis": analysis, "video_url": video_url})
    
    print("--- Report generation complete. ---")
    return {"report": report.content}

# --- 6. Build the LangGraph Workflow ---

def build_graph():
    """
    Constructs and compiles the LangGraph agent workflow.
    """
    # Create the graph instance with the defined state
    workflow = StateGraph(AgentState)

    # Add the nodes to the graph
    workflow.add_node("fetch_comments", lambda state: {"comments": tools[0].invoke({"video_url": state['video_url']})})
    workflow.add_node("analyze_comments", analyze_comments_node)
    workflow.add_node("generate_report", generate_report_node)

    # Define the entry and exit points and the edges
    workflow.set_entry_point("fetch_comments")
    workflow.add_edge("fetch_comments", "analyze_comments")
    workflow.add_edge("analyze_comments", "generate_report")
    workflow.add_edge("generate_report", END)

    # Compile the graph
    # We pass the checkpointer here to enable memory for the agent.
    app = workflow.compile(checkpointer=InMemorySaver())
    return app

# --- 7. Run the Agent ---
if __name__ == "__main__":
    agent_app = build_graph()
    
    # Example video URL to process
    video_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    # We need to give the agent a unique 'thread_id' so it can manage the state.
    # This is required because we are using the InMemorySaver as a checkpointer.
    # For each new "conversation," you would use a new thread_id.
    thread_id = "test_run_123"

    # Initial state for the agent
    initial_state = {"video_url": video_url}
    
    # We now pass the configurable dictionary with the thread_id
    config = {"configurable": {"thread_id": thread_id}}
    
    print(f"--- Starting agent for video URL: {video_url} with thread_id: {thread_id} ---")
    
    # Invoke the agent and run the workflow
    final_state = agent_app.invoke(initial_state, config=config)

    # Print the final report from the state
    print("\n\n" + "="*50)
    print("         FINAL YOUTUBE COMMENT REPORT")
    print("="*50 + "\n")
    print(final_state['report'])
    print("\n" + "="*50)
