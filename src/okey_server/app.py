# okey_server/app.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from okey_server import state
from okey_server.routers import router


def load_env_file():
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_env_file()

    model_path = os.getenv("YOLO_MODEL_PATH")
    rf_key = os.getenv("ROBOFLOW_API_KEY")

    if model_path:
        from okey_vision.providers import LocalYoloProvider
        try:
            state.vision_pipeline = LocalYoloProvider(model_path=model_path)
            print(f"Loaded LocalYoloProvider with model: {model_path}")
        except Exception as e:
            print(f"Warning: Failed to load local YOLO provider: {e}")
    else:
        # Default fallback to Roboflow if no local model path is specified
        from okey_vision.providers import RoboflowWorkflowProvider
        key = rf_key or "ROBOFLOW_API_KEY"
        workspace = os.getenv("ROBOFLOW_WORKSPACE", "ata-dc7ry")
        workflow = os.getenv("ROBOFLOW_WORKFLOW_ID", "rummikub-vrummikub-p8akb-vr0ef-3-yolov8n-t1-logic")
        
        try:
            state.vision_pipeline = RoboflowWorkflowProvider(
                api_key=key,
                workspace_name=workspace,
                workflow_id=workflow
            )
            print(f"Loaded default RoboflowWorkflowProvider (Workspace: {workspace}, Workflow: {workflow})")
        except Exception as e:
            print(f"Warning: Failed to load default Roboflow workflow provider: {e}")
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
