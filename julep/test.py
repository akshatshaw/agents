from julep import Julep
import os
import yaml 
import time
from dotenv import load_dotenv

load_dotenv()

client = Julep(
    api_key=os.getenv('JULEP_API_KEY'),
    environment=os.getenv('JULEP_ENVIRONMENT')
)


agent = client.agents.create(
    name="Writing Assistant",
    model="claude-3.5-sonnet",
    about="A helpful AI assistant that in story telling."
)

with open(r'.\julep\yaml_task\story.yaml', 'r') as file:
  story_task = yaml.safe_load(file)


with open(r'.\julep\yaml_task\summary.yaml', 'r') as file:
  summary_task = yaml.safe_load(file)
  
with open(r'.\julep\yaml_task\custom.yaml', 'r') as file:
  custom_task = yaml.safe_load(file)


task = client.tasks.create(
    agent_id=agent.id,
    **custom_task # Unpack the task definition
)

# user = client.users.create(
#     name="Anon",
#     about="a storyteller how writes story",
#     metadata={"name": "Anon"},
# )


execution = client.executions.create(
    task_id=task.id,
    input={"topic": "Hi my name is akshat shaw, i study in IIT ROORKEE"}
)

# Wait for the execution to complete
while (result := client.executions.get(execution.id)).status not in ['succeeded', 'failed']:
    print(result.status)
    # time.sleep(1)

if result.status == "succeeded":
    print(result.output)
else:
    print(f"Error: {result.error}")