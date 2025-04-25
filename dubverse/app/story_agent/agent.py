import warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

from google.adk.agents import Agent
# from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types 
import asyncio
from utils import tts_tool ,text_to_speech_file
import os
from dotenv import load_dotenv
load_dotenv() 

api_key = os.environ['GOOGLE_API_KEY'] 

AGENT_MODEL = "gemini-2.0-flash"

root_agent = Agent(
    name="hindi_story_agent_v1",
    model=AGENT_MODEL, 
    description="Generate a Hindi story from a user-provided idea and convert it to speech.",
    instruction=(
        "You are a creative storytelling agent.\n"
        "Given an idea from the user, craft a concise and engaging story in Hindi.\n"
        "Once the story is generated, use the 'tts_tool' to produce the speech output. Pass the story/text generated in the tool and wait for the file to be generated!\n"
        "Respond only with the story text in Hindi. And pass the story as text in the tool 'tts_tool'\n"
        "Make sure to pass the hindi story to the tool to genearate audio file. And wait for it to complete."
    ),
    tools=[tts_tool],
)

session_service = InMemorySessionService()

APP_NAME = "story_app"
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

  content = types.Content(role='user', parts=[types.Part(text=query)])

  final_response_text = "Agent did not produce a final response." 

  async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
      if event.is_final_response():
          if event.content and event.content.parts:
             final_response_text = event.content.parts[0].text
          elif event.actions and event.actions.escalate: # Handle potential errors/escalations
             final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
          break 

  print(f"<<< Agent Response: {final_response_text}")
  return final_response_text


if __name__ == "__main__":
    asyncio.run(call_agent_async(f"Write a horror story"))