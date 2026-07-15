# okey_server/app.py
import os
from typing import List, Optional, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from okey_core.types import Tile, OkeyMeta, Arrangement, OrchestratorResult, TileColor
from okey_solver import create_standard_okey_solver, SolverEngine


# Optional vision pipeline initialized at startup as a fallback
vision_pipeline: Optional[Any] = None


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
    global vision_pipeline
    load_env_file()

    model_path = os.getenv("YOLO_MODEL_PATH")
    rf_key = os.getenv("ROBOFLOW_API_KEY")

    if model_path:
        from okey_vision.providers import LocalYoloProvider
        try:
            vision_pipeline = LocalYoloProvider(model_path=model_path)
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
            vision_pipeline = RoboflowWorkflowProvider(
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


# Dependency Injection Providers
def get_solver_engine() -> SolverEngine:
    return create_standard_okey_solver()


def get_vision_pipeline() -> Optional[Any]:
    return vision_pipeline


class ArrangeRequest(BaseModel):
    tiles: List[Tile]
    okey_meta: Optional[OkeyMeta] = None


@app.post("/solver/arrange", response_model=Arrangement)
def arrange_hand(
    req: ArrangeRequest,
    solver: SolverEngine = Depends(get_solver_engine),
):
    """
    Solves and arranges a given list of Okey tiles into optimal melds.
    """
    try:
        return solver.find_best_arrangement(req.tiles, req.okey_meta)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/vision/solve", response_model=OrchestratorResult)
async def solve_vision(
    file: UploadFile = File(...),
    okey_meta_color: Optional[TileColor] = Form(None),
    okey_meta_value: Optional[int] = Form(None),
    # Vision request variables
    api_key: Optional[str] = Form(None),
    workspace: Optional[str] = Form(None),
    workflow_id: Optional[str] = Form(None),
    model_path: Optional[str] = Form(None),
    pipeline: Optional[Any] = Depends(get_vision_pipeline),
):
    """
    Processes an uploaded board image, detects the tiles, and returns the optimal meld arrangement.
    Variables (api_key, workspace, workflow_id, or model_path) can be supplied directly in the form request.
    """
    # Decide which pipeline provider to use for this request context
    active_pipeline = pipeline

    if model_path:
        from okey_vision.providers import LocalYoloProvider
        try:
            active_pipeline = LocalYoloProvider(model_path=model_path)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to initialize request-scoped LocalYoloProvider: {e}"
            )
    elif api_key:
        from okey_vision.providers import RoboflowWorkflowProvider
        ws = workspace or "ata-dc7ry"
        wf = workflow_id or "rummikub-vrummikub-p8akb-vr0ef-3-yolov8n-t1-logic"
        try:
            active_pipeline = RoboflowWorkflowProvider(
                api_key=api_key,
                workspace_name=ws,
                workflow_id=wf
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to initialize request-scoped RoboflowWorkflowProvider: {e}"
            )

    if active_pipeline is None:
        raise HTTPException(
            status_code=400,
            detail="Vision provider not configured. Please supply api_key or model_path in the request or environment variables."
        )

    try:
        content = await file.read()
        from okey_orchestrator import VisionSolverEngine
        
        okey_meta = None
        if okey_meta_color and okey_meta_value is not None:
            okey_meta = OkeyMeta(color=okey_meta_color, value=okey_meta_value)

        engine = VisionSolverEngine(pipeline=active_pipeline, okey_meta=okey_meta)
        result = await engine.analyze_frame_async(content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
