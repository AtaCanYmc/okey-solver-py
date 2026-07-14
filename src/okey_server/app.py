# okey_server/app.py
import os
from typing import List, Optional, Any
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from okey_core.types import Tile, OkeyMeta, Arrangement, OrchestratorResult, TileColor
from okey_solver import create_standard_okey_solver, SolverEngine


# Optional vision pipeline initialized at startup
vision_pipeline: Optional[Any] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global vision_pipeline
    model_path = os.getenv("YOLO_MODEL_PATH")
    rf_key = os.getenv("ROBOFLOW_API_KEY")

    if model_path:
        from okey_vision.providers import LocalYoloProvider
        try:
            vision_pipeline = LocalYoloProvider(model_path=model_path)
            print(f"Loaded LocalYoloProvider with model: {model_path}")
        except Exception as e:
            print(f"Warning: Failed to load local YOLO provider: {e}")
    elif rf_key:
        from okey_vision.providers import RoboflowProvider
        model_id = os.getenv("ROBOFLOW_MODEL_ID", "rummikub-5bldr")
        version = os.getenv("ROBOFLOW_MODEL_VERSION", "1")
        vision_pipeline = RoboflowProvider(api_key=rf_key, model_id=model_id, model_version=version)
        print(f"Loaded RoboflowProvider with model ID: {model_id}")
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
    pipeline: Optional[Any] = Depends(get_vision_pipeline),
):
    """
    Processes an uploaded board image, detects the tiles, and returns the optimal meld arrangement.
    """
    if pipeline is None:
        raise HTTPException(
            status_code=400,
            detail="Vision provider not configured. Please set YOLO_MODEL_PATH or ROBOFLOW_API_KEY environment variables."
        )

    try:
        content = await file.read()
        from okey_orchestrator import VisionSolverEngine
        
        okey_meta = None
        if okey_meta_color and okey_meta_value is not None:
            okey_meta = OkeyMeta(color=okey_meta_color, value=okey_meta_value)

        engine = VisionSolverEngine(pipeline=pipeline, okey_meta=okey_meta)
        result = await engine.analyze_frame_async(content)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
