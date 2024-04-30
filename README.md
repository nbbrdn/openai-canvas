# Open AI Canvas

## Install
Run the command:
```
python3 -m pip install --user git+https://github.com/nbbrdn/openai-canvas.git
```
Uninstall:
```
python3 -m pip uninstall openai-canvas
```

## Mini Apps
The project consists of several mini-applications, each of which demonstrates some 
aspect of working with the OpenAI API. Below, for each such application, the launch 
command and a brief description are provided.

### pythonista
Command to run: `pythonista <request>`

For example:
```
pythonista "what is x in 1 + 3x = -5"
```
```
pythonista "What's the sunrise and sunset time. Use api.sunrise-sunset.org"
```

Description:

It's an assistant that could answer user questions, by writing Python code as needed 
and connecting the internet.

### local-time
Command to run: `local-time`

Description:

Feel free to interact with this assistant. If you inquire about the time in any city worldwide, the assistant will trigger a designated function. This function retrieves the local date and time from a remote API by providing the UTC offset.

Example:
```
$ local-time
Enter your requset (or STOP to finish conversation.)
> what time is in Omsk?
The current local time in Omsk is 18:06.
> STOP
$
```

## Development
1. Install dependencies:
```
poetry install
```
2. Install pre-commit hook:
```
pre-commit install
```