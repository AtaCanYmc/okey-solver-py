# okey_server/cli.py
import argparse
import sys
from okey_server import state


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
    parser.add_argument(
        "--rf-key", help="Roboflow API Key."
    )
    parser.add_argument(
        "--rf-workspace", default="ata-dc7ry", help="Roboflow Workspace name."
    )
    parser.add_argument(
        "--rf-model-id", default="okey-rummikub", help="Roboflow Model ID."
    )
    parser.add_argument(
        "--rf-model-version", type=int, default=1, help="Roboflow Model Version."
    )
    parser.add_argument(
        "--rf-api-url", help="Roboflow custom API URL."
    )

    args = parser.parse_args()

    # Pass all configurations directly to the state module instead of env variables
    if args.model:
        state.model_path = args.model
    if args.rf_key:
        state.rf_key = args.rf_key
    state.rf_workspace = args.rf_workspace
    state.rf_model_id = args.rf_model_id
    state.rf_model_version = args.rf_model_version
    if args.rf_api_url:
        state.rf_api_url = args.rf_api_url

    try:
        import uvicorn
    except ImportError:
        print(
            "Error: uvicorn is not installed. Install it using 'pip install okey-solver-py[server]'",
            file=sys.stderr
        )
        sys.exit(1)

    from okey_server.app import app

    print(f"Starting Okey Server on http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
