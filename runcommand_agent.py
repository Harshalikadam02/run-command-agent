import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
import os

load_dotenv()

client = OpenAI()

def query_db(sql):
    pass

def run_command(command):
    result = os.system(command=command)
    return result
    #execute command
    #return result

available_tools = {
    "run_command": {
        "fn": run_command,
        "description": "Takes a command as input to execute on system and returns output"
    }
}

system_prompt = """
    You are an helpfull AI assistant who is specialized in resolving user query.
    You work on start, plan, action, observe mode.
    For the given user query and available tool. and based on the tool selection you perform an action to c
    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    -Follow the Output JSON Format.
    -Always perform one step at a time and wait for next input
    -Carefully analyse the user query

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function".
    }}

    Available Tools:
    - run_command: Takes a command as input to execute on system and returns output


    Example:
    User Query: create a file named magic.txt
    Output: {{ "step": "plan", "content": "User wants to create a file magic.txt" }}
    Output: {{ "step": "plan", "content": "From the available tools I should call run_command"}}
    Output: {{ "step": "action", "function": "run_command", "input": "touch magic.txt"}}
    Output: {{ "step": "observe", "output": "exit_code=0, stdout=, stderr=" }}
    Outout: {{ "step": "output", "content": "Created magic.txt in the current directory"}}
"""

messages = [
    { "role": "system", "content": system_prompt }
]

user_query = input('> ')
messages.append({"role": "user", "content": user_query})

while True:
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=messages
    )

    parsed_output = json.loads(response.choices[0].message.content)
    messages.append({"role": "assistant", "content": json.dumps(parsed_output)})

    if parsed_output.get("step") == "plan":
        print(f"{parsed_output.get('content')}")
        continue

    if parsed_output.get("step") == "action":
        tool_name = parsed_output.get("function")
        tool_input = parsed_output.get("input")

        if tool_name in available_tools:
            output = available_tools[tool_name]["fn"](tool_input)
            messages.append({
                "role": "assistant",
                "content": json.dumps({"step": "observe", "output": output})
            })
            continue

    if parsed_output.get("step") == "output":
        print(f"{parsed_output.get('content')}")
        break
