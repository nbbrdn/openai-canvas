import json
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Tuple, Union

import openai
import requests
from openai.types.beta.assistant import Assistant
from openai.types.beta.thread import Thread
from openai.types.beta.threads.run import Run

INSTRUCTIONS: str = """
You're a support service chat bot.
Use the provided functions to answer questions.
Synthesise answer based on provided function output and be consise.
"""

api_key: str = os.environ.get("OPENAI_API_KEY")
client: openai.Client = openai.OpenAI(api_key=api_key)


# Fetch local time function
def fetch_local_time(offset: int) -> Union[datetime, str]:
    print("fetching data from remote...")
    url: str = "https://flow.bayborodin.ru/time/"
    params: Dict[str, Any] = {"offset": offset}
    response = requests.get(url, params=params, timeout=5)
    if response.status_code == 200:
        current_time: str = response.json()["current_time"]
        datetime_object: datetime = datetime.fromisoformat(current_time)
        print(f"remote response: {datetime_object}")
        return datetime_object
    return (
        "Error: Unable to fetch local time. "
        "Status code: {response.status_code}"
    )


available_functions = {
    "fetch_local_time": fetch_local_time,
}


def run_conversation() -> None:
    # Assistant setup
    tools: List[Dict[str, Any]] = [
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

    assistant: Assistant = client.beta.assistants.create(
        name="Support chat bot",
        instructions=INSTRUCTIONS,
        model="gpt-4-turbo",
        tools=tools,
    )

    # Conversation loop
    while True:
        query: str = input()
        run, thread = create_message_and_run(assistant=assistant, query=query)
        print(run)

        while True:
            run: openai.Run = client.beta.threads.runs.retrieve(
                thread_id=thread.id, run_id=run.id
            )
            print("run status", run.status)

            if run.status == "requires_action":
                function_name, arguments, function_id = get_function_details(
                    run
                )
                function_response = execute_function_call(
                    function_name, arguments
                )
                run = submit_tool_outputs(
                    run, thread, function_id, function_response
                )
                continue

            if run.status == "completed":
                latest_message = client.beta.threads.messages.list(
                    thread_id=thread.id
                ).data[0]
                print(latest_message.content[0].text.value)
                user_input = input()
                if user_input == "STOP":
                    break
                run, thread = create_message_and_run(
                    assistant=assistant, query=user_input, thread=thread
                )
                continue

            time.sleep(1)


# Helper functions


def create_message_and_run(
    assistant: Assistant, query: str, thread: Thread = None
) -> Tuple[Run, Thread]:
    if not thread:
        thread = client.beta.threads.create()

    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=query
    )
    run: Run = client.beta.threads.runs.create(
        thread_id=thread.id, assistant_id=assistant.id
    )
    return run, thread


def get_function_details(run: Run):
    print("\nrun.required_action\n", run.required_action)

    called_function = run.required_action.submit_tool_outputs.tool_calls[0]
    function_name = called_function.function.name
    arguments = called_function.function.arguments
    function_id = called_function.id

    print(f"function_name: {function_name} and arguments: {arguments}")

    return function_name, arguments, function_id


def execute_function_call(
    function_name: str, arguments: str
) -> Union[str, datetime]:
    function = available_functions.get(function_name, None)
    if function:
        arguments = json.loads(arguments)
        return function(**arguments)
    return f"Error: function {function_name} does not exist"


def submit_tool_outputs(
    run: Run,
    thread: Thread,
    function_id: str,
    function_response: Union[str, datetime],
) -> Run:
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
