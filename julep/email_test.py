from julep import Julep
import os
import yaml 
import time
from dotenv import load_dotenv

load_dotenv()

client = Julep(
    api_key=os.getenv('JULEP_API_KEY'),
    environment=os.getenv('JULEP_ENVIRONMENT', 'development')
)

# Create an agent
agent = client.agents.create(
    name="Email Assistant",
    model="claude-3.5-sonnet",
    about="An AI assistant that specializes in composing and sending emails."
)


# Add a tool to the agent
tool = client.agents.tools.create(
    agent_id=agent.id,
    name="send_email",
    **yaml.safe_load("""
    type: integration
    integration:
      provider: email
      method: send
      setup:
        host: "gmail.com"
        port: 8080
        user: "akshaw.ak4"
        password: "akshaw322"
    """),
)

# Create a task that inherits this tool
task = client.tasks.create(
    agent_id=agent.id,
    tools = tool,
    name="Handle Support Request",
    **yaml.safe_load("""
    main:
    - tool: send_email
      arguments:
        to: $ steps[0].input.customer_email
        from: "akshaw.ak4@gmail.com"
        subject: $ steps[0].input.subject
        body: $ steps[0].input.body
    """)
)

# Execute the task
execution = client.executions.create(
    task_id=task.id,
    input={
        "customer_email": "akshat_s1@mt.iitr.ac.in",
        "subject": "Hello from Akshat",
        "body": "This is a test email sent using Julep."
    }
)

# Wait for the execution to complete
while (result := client.executions.get(execution.id)).status not in ['succeeded', 'failed']:
    print(f"Execution status: {result.status}")
    time.sleep(1)

if result.status == "succeeded":
    print("Email sent successfully!")
    print(result.output)
else:
    print(f"Error: {result.error}")

