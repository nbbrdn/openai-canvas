import json
import logging
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

BASE_API_URL = "https://flow.bayborodin.ru/"

log_file_path = "logs.log"
logging.basicConfig(
    filename=log_file_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

api_key: str = os.environ.get("OPENAI_API_KEY")
client: openai.Client = openai.OpenAI(api_key=api_key)


# Fetch local time function
def fetch_local_time(offset: int) -> Union[datetime, str]:
    url: str = f"{BASE_API_URL}time/"
    params: Dict[str, Any] = {"offset": offset}
    response = requests.get(url, params=params, timeout=5)
    if response.status_code == 200:
        current_time: str = response.json()["current_time"]
        datetime_object: datetime = datetime.fromisoformat(current_time)
        logger.info(f"Remote function response: {datetime_object}")
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
    print("Enter your requset (or STOP to finish conversation.)")
    while True:
        query: str = input("> ")
        if query.upper() == "STOP":
            break

        run, thread = create_message_and_run(assistant=assistant, query=query)
        logger.info(run)

        while True:
            run: openai.Run = client.beta.threads.runs.retrieve(
                thread_id=thread.id, run_id=run.id
            )
            logger.info("Run status: %s", run.status)

            if run.status == "requires_action":
                functions = get_function_details(run)
                outputs = []

                for func in functions:
                    output = execute_function_call(
                        func["name"], func["arguments"]
                    )

                    outputs.append(
                        {
                            "tool_call_id": func["id"],
                            "output": str(output),
                        }
                    )

                run = submit_tool_outputs(run, thread, outputs)
                continue

            if run.status == "completed":
                latest_message = client.beta.threads.messages.list(
                    thread_id=thread.id
                ).data[0]
                logger.info(
                    "Latest message: %s", latest_message.content[0].text.value
                )
                print(latest_message.content[0].text.value)

                user_input = input("> ")
                if user_input.upper() == "STOP":
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
    logger.info("Requested action: %s", run.required_action)

    tool_calls = run.required_action.submit_tool_outputs.tool_calls
    return [
        {
            "id": tool_call.id,
            "name": tool_call.function.name,
            "arguments": tool_call.function.arguments,
        }
        for tool_call in tool_calls
    ]


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
    outputs,
) -> Run:
    run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs=outputs,
    )
    return run
