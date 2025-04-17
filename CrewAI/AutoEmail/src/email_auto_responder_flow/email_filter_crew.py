# from crewai import Agent, Crew, Process, Task, LLM
# from crewai.project import CrewBase, agent, crew, task
# from crewai_tools import SerperDevTool
# from langchain_community.tools.gmail.get_thread import GmailGetThread
# # from langchain_community.tools.tavily_search import TavilySearchResults
# # from langchain_openai import ChatOpenAI
# from crewai.tools import BaseTool
# from pydantic import Field
# from typing import Type
# from pydantic import BaseModel, ConfigDict
# import create_draft  

# import os
# from dotenv import load_dotenv
# load_dotenv() 

# llm = LLM(
# model=os.environ['MODEL'],
# api_key= os.environ['GEMINI_API_KEY'],
# # base_url="https://api.your-provider.com/v1"
# )

# @CrewBase
# class EmailFilterCrew(BaseModel):
#     """Email Filter Crew"""
#     model_config = ConfigDict(ignored_types=(str,))
#     agents_config = "config/agents.yaml"
#     tasks_config = "config/tasks.yaml"

#     @agent
#     def email_response_writer(self) -> Agent:
#         gmail = GmailGetThread()
#         return Agent(
#             config=self.agents_config["email_response_writer"],
#             llm=llm,
#             verbose=True,
#             tools=[
#                 # TavilySearchResults(),
#                 GmailGetThread(api_resource=gmail.api_resource),
#                 create_draft,
#             ],
#         )

#     # @task
#     # def draft_responses_task(self) -> Task:
#     #     return Task(config=self.tasks_config["send_followup_email"])
#     @task
#     def draft_responses_task(self) -> Task:
#         task_config = self.tasks_config["send_followup_email"]
#         task_config["agent"] = "email_response_writer"  # Explicitly set the agent name
#         return Task(config=task_config)
    
#     @crew
#     def crew(self) -> Crew:
#         """Creates the Email Filter Crew"""
#         return Crew(
#             agents=self.agents,
#             tasks=self.tasks,
#             process=Process.sequential,
#             verbose=True,
#             llm = llm
#         )
# if __name__ == "__main__":
#     crew()


from typing import ClassVar
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import SerperDevTool
from langchain_community.tools.gmail.get_thread import GmailGetThread
# from langchain_community.tools.tavily_search import TavilySearchResults
# from langchain_openai import ChatOpenAI
from create_draft import CreateDraftTool
import os
from dotenv import load_dotenv
from pydantic import ConfigDict
from typing import ClassVar, Dict, Any

load_dotenv() 

llm = LLM(
    model=os.environ['MODEL'],
    api_key=os.environ['GEMINI_API_KEY'],
    # base_url="https://api.your-provider.com/v1"
)

@CrewBase
class EmailFilterCrew:
    """Email Filter Crew"""
    agents_config: ClassVar[str] = "config/agents.yaml"
    tasks_config: ClassVar[str]  =  "config/tasks.yaml"
    
    # Alternative approach using ConfigDict if ClassVar doesn't work
    # model_config = ConfigDict(arbitrary_types_allowed=True)

    @agent
    def email_response_writer(self) -> Agent:
        gmail = GmailGetThread()
        # draft_tool = CreateDraftTool()  # Instantiate the tool
        
        return Agent(
            config=self.agents_config["email_response_writer"],  # Make sure this matches your YAML
            llm=llm,
            verbose=True,
            tools=[
                # TavilySearchResults(),
                GmailGetThread(api_resource=gmail.api_resource),
                CreateDraftTool.create_draft,  # Use the instantiated tool
            ],
        )

    @task
    def draft_responses_task(self) -> Task:
        task_config = self.tasks_config["send_followup_email"].copy()  # Create a copy to avoid modifying the original
        task_config["agent"] = "email_response_writer"  # Explicitly set the agent name
        return Task(config=task_config)
    
    @crew
    def crew(self) -> Crew:
        """Creates the Email Filter Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            llm=llm
        )

# if __name__ == "__main__":
#     EmailFilterCrew().crew().kickoff()  # Properly instantiate and run
