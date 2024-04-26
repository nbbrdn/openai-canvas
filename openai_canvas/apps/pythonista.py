import os

import openai


def run(message):
    api_key = os.environ.get("OPENAI_API_KEY")
    client = openai.OpenAI(api_key=api_key)
    assistant_id, thread_id = setup_assistant(client, message)
    print(
        "Debugging: Useful for checking the generated agent in the playground. "
        "https://platform.openai.com/playground"
        "?mode=assistant&assistant={assistant_id}"
    )
    print(
        "Debugging: Useful for checking logs. "
        "https://platform.openai.com/playground?thread={thread_id}"
    )


def setup_assistant(client, message):
    pass
