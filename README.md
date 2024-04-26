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

## Development
1. Install dependencies:
```
poetry install
```
2. Install pre-commit hook:
```
pre-commit install
```