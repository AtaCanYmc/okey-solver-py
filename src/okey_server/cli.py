# okey_server/cli.py
import argparse
import sys

from okey_server.settings import OkeyServerSettings


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
        "--rf-workspace", help="Roboflow Workspace name."
    )
    parser.add_argument(
        "--rf-model-id", help="Roboflow Model ID."
    )
    parser.add_argument(
        "--rf-model-version", type=int, help="Roboflow Model Version."
    )
    parser.add_argument(
        "--rf-api-url", help="Roboflow custom API URL."
    )

    args = parser.parse_args()

    # Pass configuration arguments to Pydantic Settings initialization
    settings_kwargs = {}
    if args.model:
        settings_kwargs["model_path"] = args.model
    if args.rf_key:
        settings_kwargs["rf_key"] = args.rf_key
    if args.rf_workspace:
        settings_kwargs["rf_workspace"] = args.rf_workspace
    if args.rf_model_id:
        settings_kwargs["rf_model_id"] = args.rf_model_id
    if args.rf_model_version is not None:
        settings_kwargs["rf_model_version"] = args.rf_model_version
    if args.rf_api_url:
        settings_kwargs["rf_api_url"] = args.rf_api_url

    settings = OkeyServerSettings(**settings_kwargs)

    try:
        import uvicorn
    except ImportError:
        print(
            "Error: uvicorn is not installed. Install it using 'pip install okey-solver-py[server]'",
            file=sys.stderr
        )
        sys.exit(1)

    from okey_server.app import app
    app.state.settings = settings

    print(f"Starting Okey Server on http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
