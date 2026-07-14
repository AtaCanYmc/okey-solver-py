# okey_server/cli.py
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Okey Server CLI - Start the Okey solver FastAPI microservice."
    )
    parser.add_argument(
        "--host", default="0.0.0.0", help="Bind IP address (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="Port to listen on (default: 8000)"
    )
    parser.add_argument(
        "--model", help="Path to the local YOLO model (.pt) file."
    )

    args = parser.parse_args()

    if args.model:
        os.environ["YOLO_MODEL_PATH"] = args.model

    try:
        import uvicorn
    except ImportError:
        print(
            "Error: uvicorn is not installed. Install it using 'pip install okey-solver-py[server]'",
            file=sys.stderr
        )
        sys.exit(1)

    print(f"Starting Okey Server on http://{args.host}:{args.port}")
    uvicorn.run("okey_server.app:app", host=args.host, port=args.port)


if __name__ == "__main__":
    main()
