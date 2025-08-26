# All code is self-contained and runnable within this block.
# Remember to install the required libraries:
# pip install langchain langchain-community langchain-core langgraph 'pydantic<2' langchain-groq

# --- 1. Import necessary libraries ---
import os
import re
import random
import time
import json
from typing import TypedDict, Annotated, List, Literal, Optional
from langchain_core.messages import BaseMessage, AnyMessage, HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_groq import ChatGroq
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- 2. Set API Keys and Environment Variables ---
# The following variables have been set based on your request.
os.environ['GROQ_API_KEY'] = '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'
os.environ['LANGCHAIN_API_KEY'] = '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'
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_PROJECT'] = 'simple_bot'
os.environ['EMAIL_ADDRESS'] = 'hoiiworld7631@gmail.com'
os.environ['EMAIL_PASSWORD'] = 'lhss ymso cbmt fahh'

# --- 3. Define the Agent's State ---
class AgentState(TypedDict):
    """Represents the state of our agent."""
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]
    niche: str
    youtube_subscribers: int
    insta_followers: int
    linkedin_followers: int
    youtube_url: str
    insta_url: str
    linkedin_url: str
    drafted_mail: str
    companies_found: Optional[str]
    confirmation: Optional[Literal["yes", "no"]]


# --- 4. Define the Tools (Nodes that perform actions) ---

@tool
def get_emails_from_db() -> str:
    """
    A tool to retrieve emails from a local JSON database file.
    """
    print(f"\n--- Calling tool: get_emails_from_db ---")
    
    try:
        with open('assets.json', 'r') as f:
            data = json.load(f)
            emails = data.get('marketing_mails', [])
    except FileNotFoundError:
        return "Error: assets.json file not found."
    except json.JSONDecodeError:
        return "Error: Could not decode assets.json. Check file format."
    
    if not emails:
        return "No recipients found in assets.json."
    
    formatted_output = "\n".join([f"- {email}" for email in emails])
    
    print("--- Tool execution successful. Emails retrieved from local database. ---\n")
    return f"Found {len(emails)} potential sponsors:\n{formatted_output}"

@tool
def send_sponsorship_emails(email_content: str, recipients: str) -> str:
    """
    A real tool to send emails using Python's smtplib library.
    NOTE: You must set EMAIL_ADDRESS and EMAIL_PASSWORD environment variables.
          For Gmail, you will need to use an App Password for security.
    """
    print(f"\n--- Calling tool: send_sponsorship_emails ---")
    
    email_address = os.environ.get('EMAIL_ADDRESS')
    email_password = os.environ.get('EMAIL_PASSWORD')

    if not email_address or not email_password:
        return "Error: EMAIL_ADDRESS or EMAIL_PASSWORD environment variable not set. Email not sent."

    recipients_list = [r.strip() for r in recipients.split(',')]
    
    if not recipients_list or recipients_list == ['']:
        print("--- No valid recipients found. Email not sent. ---")
        return "No valid recipients found. Email not sent."

    msg = MIMEMultipart()
    msg["From"] = email_address
    msg["To"] = ", ".join(recipients_list)
    msg["Subject"] = 'Sponsorship Inquiry'
    msg.attach(MIMEText(email_content, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_address, email_password.replace(" ", ""))
        server.sendmail(email_address, recipients_list, msg.as_string())
        server.quit()
        print("--- Emails successfully sent. ---\n")
        return "Emails have been sent to the marketing handles."
    except Exception as e:
        print(f"--- Failed to send emails: {e} ---\n")
        return f"Error: Failed to send emails. Details: {e}"

# --- 5. Define the LLM and the Agent's Nodes ---

llm = ChatGroq(model="llama3-8b-8192")

def collect_data_node(state: AgentState) -> AgentState:
    """Node to collect influencer data."""
    print("--- Executing node: collect_data_node ---")
    niche = "tech reviews"
    youtube_subs = 55000
    insta_followers = 15000
    linkedin_followers = 8000
    youtube_url = "youtube.com/mytechchannel"
    insta_url = "instagram.com/mytechchannel"
    linkedin_url = "linkedin.com/in/mytechchannel"
    print(f"Data collected for niche: {niche}")
    return {
        "niche": niche,
        "youtube_subscribers": youtube_subs,
        "insta_followers": insta_followers,
        "linkedin_followers": linkedin_followers,
        "youtube_url": youtube_url,
        "insta_url": insta_url,
        "linkedin_url": linkedin_url
    }

def draft_mail_node(state: AgentState) -> AgentState:
    """Node to use the LLM to draft a sponsorship email."""
    print("--- Executing node: draft_mail_node ---")
    draft_prompt = PromptTemplate.from_template(
        """
        You are an expert ghostwriter for a social media influencer. Your task is to draft a professional, concise, and compelling sponsorship email.
        Here is the influencer's data:
        - Niche: {niche}
        - YouTube Subscribers: {youtube_subscribers}
        - Instagram Followers: {insta_followers}
        - LinkedIn Followers: {linkedin_followers}
        - YouTube Profile: {youtube_url}
        - Instagram Profile: {insta_url}
        - LinkedIn Profile: {linkedin_url}
        Draft a short email suitable for a marketing department. The tone should be friendly yet professional. Clearly state the influencer's niche, audience size, and a brief value proposition. Do not include a subject line or a salutation (e.g., "Hi,"). End with "Best regards," followed by "Influencer's Name".
        Draft:
        """
    )
    chain = draft_prompt | llm
    drafted_mail_content = chain.invoke(state)
    print("--- Sponsorship email drafted by LLM. ---")
    return {"drafted_mail": drafted_mail_content.content}

def confirm_mail_node(state: AgentState) -> AgentState:
    """Node to simulate user confirmation."""
    print("--- Executing node: confirm_mail_node ---")
    print("\nDrafted Email for Your Review:\n" + "="*50)
    print(state['drafted_mail'])
    print("="*50 + "\n")
    user_input = "yes"
    print(f"Simulating user confirmation: '{user_input}'")
    if user_input.lower() == "yes":
        return {"confirmation": "yes"}
    else:
        return {"confirmation": "no"}

def send_mail_node(state: AgentState) -> AgentState:
    """Node to send the confirmed emails using a tool."""
    print("--- Executing node: send_mail_node ---")
    recipients_raw = state['companies_found']
    emails = re.findall(r'[\w\.-]+@[\w\.-]+', recipients_raw)
    recipients_string = ", ".join(emails)
    
    if not emails:
        print("--- No email addresses to send to. Skipping email tool call. ---")
        return {"messages": [HumanMessage(content="Agent completed. No emails were found, so no messages were sent.")]}

    send_sponsorship_emails.invoke({"email_content": state['drafted_mail'], "recipients": recipients_string})
    return {"messages": [HumanMessage(content="Emails have been sent.")]}


# --- 6. Build the LangGraph Workflow ---

def build_graph():
    """Constructs and compiles the LangGraph agent workflow."""
    workflow = StateGraph(AgentState)
    workflow.add_node("collect_data", collect_data_node)
    workflow.add_node("draft_mail", draft_mail_node)
    # The search node now calls the local database function
    workflow.add_node("search_companies", lambda state: {"companies_found": get_emails_from_db.invoke({})})
    workflow.add_node("confirm_mail", confirm_mail_node)
    workflow.add_node("send_mail", send_mail_node)
    workflow.set_entry_point("collect_data")
    workflow.add_edge("collect_data", "draft_mail")
    workflow.add_edge("draft_mail", "search_companies")
    workflow.add_edge("search_companies", "confirm_mail")
    
    def should_continue(state):
        return "send_mail" if state['confirmation'] == "yes" else "draft_mail"

    workflow.add_conditional_edges("confirm_mail", should_continue)
    workflow.add_edge("send_mail", END)
    app = workflow.compile(checkpointer=InMemorySaver())
    return app

# --- 7. Run the Agent ---
if __name__ == "__main__":
    agent_app = build_graph()
    import uuid
    thread_id = str(uuid.uuid4())
    initial_state = {}
    config = {"configurable": {"thread_id": thread_id}}
    print(f"--- Starting sponsor_agent with thread_id: {thread_id} ---")
    final_state = agent_app.invoke(initial_state, config=config)
    print("\n\n" + "="*50)
    print("        AGENT RUN COMPLETE")
    print("="*50)
    print("Final State:")
    print(final_state)
    print("="*50)
