import warnings
# Ignore all warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types 

from yt_transcript import *

yt_url = "https://www.youtube.com/watch?v=sBuoMkJsMsA"

AGENT_MODEL = "gemini-2.0-flash"

root_agent = Agent(
    name="yt_agent_v1",
    model=AGENT_MODEL, 
    description="Extracts transcripts from YouTube videos and summarizes the learnings related to a given topic.",
    instruction = (
    "You are an expert YouTube video summarizer. "
    "Given a topic and a YouTube video URL, use the 'get_youtube_transcript' tool to extract the transcript (returned as a JSON with key 'result'). "
    "From the transcript, generate a clear and concise summary that captures the key learnings relevant to the given topic. "
    "Your output should be only the final summarized content — answer in bullet points."
    ),
    tools=[get_youtube_transcript],
)
session_service = InMemorySessionService()

APP_NAME = "yt_app"
USER_ID = "user_1"
SESSION_ID = "session_001" 

# Create the specific session where the conversation will happen
session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)
print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

# --- Runner ---
runner = Runner(
    agent=root_agent, 
    app_name=APP_NAME,   
    session_service=session_service #
)
print(f"Runner created for agent '{runner.agent.name}'.")

async def call_agent_async(query: str):
  """Sends a query to the agent and prints the final response."""
  print(f"\n>>> User Query: {query}")

  # Prepare the user's message in ADK format
  content = types.Content(role='user', parts=[types.Part(text=query)])

  final_response_text = "Agent did not produce a final response." #default

  async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
      # You can uncomment the line below to see *all* events during execution
      # print(f"  [Event] Author: {event.author}, Type: {type(event).__name__}, Final: {event.is_final_response()}, Content: {event.content}")

      # Key Concept: is_final_response() marks the concluding message for the turn.
      if event.is_final_response():
          if event.content and event.content.parts:
             # Assuming text response in the first part
             final_response_text = event.content.parts[0].text
          elif event.actions and event.actions.escalate: # Handle potential errors/escalations
             final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
          break 

  print(f"<<< Agent Response: {final_response_text}")
  return final_response_text


if __name__ == "__main__":
    call_agent_async(f"how to swim? yt_url= {yt_url}")

# text =call_agent_async(f"how to swim? yt_url= {yt_url}")