# okey_server/app.py
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from okey_server import state
from okey_server.routers import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_path = state.model_path
    rf_key = state.rf_key

    if model_path:
        from okey_vision.providers import LocalYoloProvider
        try:
            state.vision_pipeline = LocalYoloProvider(model_path=model_path)
            print(f"Loaded LocalYoloProvider with model: {model_path}")
        except Exception as e:
            print(f"Warning: Failed to load local YOLO provider: {e}")
    else:
        # Default fallback to Roboflow standard model if no local model path is specified
        from okey_vision.providers import RoboflowProvider
        key = rf_key or "ROBOFLOW_API_KEY"
        workspace = state.rf_workspace
        model_id = state.rf_model_id
        model_version = state.rf_model_version
        rf_api_url = state.rf_api_url

        try:
            state.vision_pipeline = RoboflowProvider(
                api_key=key,
                model_id=model_id,
                model_version=model_version,
                workspace_name=workspace,
                api_url=rf_api_url
            )
            print(
                f"Loaded default RoboflowProvider (Workspace: {workspace}, Model: {model_id}, Version: {model_version})")
        except Exception as e:
            print(f"Warning: Failed to load default Roboflow provider: {e}")
    yield


app = FastAPI(
    title="Okey Solver API",
    description="Microservice for solving Okey hand arrangements and detecting tiles from images.",
    version="0.3.0",
    lifespan=lifespan
)


@app.get("/health")
def health_check():
    """
    Service health check endpoint.
    """
    return {"status": "ok", "version": "0.3.0"}


# Register endpoints with /api/v1 prefix
app.include_router(router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

