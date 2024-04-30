import json
import os
import time
from datetime import datetime
from typing import Union

import openai
import requests

INSTRUCTIONS = """
You're a support service chat bot.
Use the provided functions to answer questions.
Synthesise answer based on provided function output and be consise.
"""


def fetch_local_time(offset) -> Union[datetime, str]:
    print("fetching data from remote...")
    url = "https://flow.bayborodin.ru/time/"
    params = {"offset": offset}
    response = requests.get(url, params=params, timeout=5)
    status_code = response.status_code
    if status_code == 200:
        dt_str = response.json()["current_time"]
        datetime_object = datetime.fromisoformat(dt_str)
        print(f"remote response: {datetime_object}")
        return datetime_object
    return f"Error: Unable to fetch local time. Status code: {status_code}"


available_functions = {
    "fetch_local_time": fetch_local_time,
}

api_key = os.environ.get("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key)

available_functions = {
    "fetch_local_time": fetch_local_time,
}


def execute(offset):
    tools = [
        {
            "type": "function",
            "function": {
                "name": "fetch_local_time",
                "description": "Fetch the local date and time by UTC offset.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "offset": {
                            "type": "integer",
                            "description": "The UTC time zone offset.",
                        }
                    },
                    "required": ["offset"],
                },
            },
        }
    ]

    assistant = client.beta.assistants.create(
        name="Support chat bot",
        instructions=INSTRUCTIONS,
        model="gpt-4-turbo",
        tools=tools,
    )

    query = input()
    run, thread = create_message_and_run(assistant=assistant, query=query)
    print(run)

    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id, run_id=run.id
        )
        print("run status", run.status)

        if run.status == "requires_action":

            function_name, arguments, function_id = get_function_details(run)

            function_response = execute_function_call(function_name, arguments)

            run = submit_tool_outputs(
                run, thread, function_id, function_response
            )

            continue
        if run.status == "completed":

            messages = client.beta.threads.messages.list(thread_id=thread.id)
            latest_message = messages.data[0]
            text = latest_message.content[0].text.value
            print(text)

            user_input = input()
            if user_input == "STOP":
                break

            run, thread = create_message_and_run(
                assistant=assistant, query=user_input, thread=thread
            )

            continue
        time.sleep(1)


def create_message_and_run(assistant, query, thread=None):
    if not thread:
        thread = client.beta.threads.create()

    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=query
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant.id
    )
    return run, thread


def get_function_details(run):
    print("\nrun.required_action\n", run.required_action)

    function_name = run.required_action.submit_tool_outputs.tool_calls[
        0
    ].function.name
    arguments = run.required_action.submit_tool_outputs.tool_calls[
        0
    ].function.arguments
    function_id = run.required_action.submit_tool_outputs.tool_calls[0].id

    print(f"function_name: {function_name} and arguments: {arguments}")

    return function_name, arguments, function_id


def execute_function_call(function_name, arguments):
    function = available_functions.get(function_name, None)
    if function:
        arguments = json.loads(arguments)
        return function(**arguments)
    return f"Error: function {function_name} does not exist"


def submit_tool_outputs(run, thread, function_id, function_response):
    run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs=[
            {
                "tool_call_id": function_id,
                "output": str(function_response),
            }
        ],
    )
    return run
