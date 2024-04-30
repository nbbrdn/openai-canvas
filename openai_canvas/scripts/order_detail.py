import sys

from openai_canvas.apps import order_detail


def main():
    if len(sys.argv) == 2:
        order_id = sys.argv[1]
        order_detail.run(order_id)
    else:
        print("Usage: order-detail <id>")
        sys.exit(1)


if __name__ == "__main__":
    main()
