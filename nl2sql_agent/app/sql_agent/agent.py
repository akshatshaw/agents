import warnings
warnings.filterwarnings("ignore")

import logging
logging.basicConfig(level=logging.ERROR)

import os
import json
import asyncio
from typing import List, Dict, Any
from dotenv import load_dotenv

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

from utils import *

load_dotenv()
api_key = os.environ['GOOGLE_API_KEY']
AGENT_MODEL = "gemini-2.0-flash"


# Create our SQL Agent
# root_agent = Agent(
#     name="sql_query_generator",
#     model=AGENT_MODEL,
#     description="Generates SQL queries from natural language questions using schema metadata and similar examples.",
#     instruction=(
#         "You are an expert SQL query generator. "
#         "Strictly call the tool and get the system prompt first, then respond to the system prompt. "
#         "Given a query from user, use the tool first 'generate_system_prompt' and wait till its response to generate the contextual query and explanation."
#         "Given a natural language question about data, generate an appropriate SQL query. "
#         "Use the provided schema metadata and similar examples to create accurate queries. "
#         "Your response should include the SQL query and an explanation of what it does and why specific joins, filters, "
#         "or aggregations were chosen. Format SQL with proper indentation for readability."
#     ),
#     tools=[generate_system_prompt],
# )

root_agent = Agent(
    name="sql_query_generator",
    model=AGENT_MODEL,
    description="Generates SQL queries from natural language questions using schema metadata and similar examples.",
    instruction=(
        "You are an expert SQL query generator. "
        "Strictly call the tool and get the system prompt first, then respond to the system prompt. "
        "Given a query from user, use the tool first 'generate_system_prompt' and wait till its response to generate the contextual query and explanation."
        "Given a natural language question about data, generate an appropriate SQL query. "
        "Use the provided schema metadata and similar examples to create accurate queries. "
        
        "If you encounter any ambiguities or potential confusion when analyzing the table schemas, such as:"
        "- Tables with similar column names but different purposes"
        "- Unclear relationships between tables"
        "- Multiple possible join paths"
        "- Ambiguous column references in the user's question"
        "- Overlapping functionality across different tables"
        "Then explicitly ask the user for clarification before proceeding with query generation."
        
        "When asking for clarification:"
        "1. Clearly explain the specific schema confusion you've identified"
        "2. Present the competing interpretations or options"
        "3. Ask a targeted question that will resolve the ambiguity"
        
        "Only after resolving any schema ambiguities should you generate the SQL query."
        "Your response should include the SQL query and an explanation of what it does and why specific joins, filters, "
        "or aggregations were chosen. Format SQL with proper indentation for readability."
    ),
    tools=[generate_system_prompt],
)

# Create session service and session
session_service = InMemorySessionService()

APP_NAME = "sql_query_app"
USER_ID = "user_1"
SESSION_ID = "session_001"

# Create the specific session where the conversation will happen
session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)
print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

# Create the runner
runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service
)
print(f"Runner created for agent '{runner.agent.name}'.")

async def generate_sql_from_nl(query: str):
    """Sends a natural language query to the agent and returns the SQL response."""
    print(f"\n>>> User Query: {query}")

    # Prepare the user's message in ADK format
    content = types.Content(role='user', parts=[types.Part(text=query)])

    final_response_text = "Agent did not produce a final response."  # default

    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                # Assuming text response in the first part
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:  # Handle potential errors/escalations
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break

    print(f"<<< Agent Response: {final_response_text}")
    return final_response_text
