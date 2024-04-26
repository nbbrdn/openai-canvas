import sys

from openai_canvas.apps import pythonista


def main():
    if len(sys.argv) == 2:
        task = sys.argv[1]
        pythonista.run(task)
    else:
        print("Usage: pythonista <message>")
        sys.exit(1)


if __name__ == "__main__":
    main()
