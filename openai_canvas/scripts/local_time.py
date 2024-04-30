import sys

from openai_canvas.apps import local_time


def main():
    if len(sys.argv) == 2:
        try:
            offset = int(sys.argv[1])
            local_time.execute(offset)
        except ValueError:
            print("UTC offset must be a number.")
    else:
        print("Usage: local-time <offset>")
        sys.exit(1)


if __name__ == "__main__":
    main()
