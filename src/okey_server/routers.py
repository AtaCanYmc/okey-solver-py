# okey_server/routers.py
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from okey_core.types import Tile, OkeyMeta, Arrangement, OrchestratorResult, TileColor
from okey_solver import create_standard_okey_solver, SolverEngine
from okey_server import state

router = APIRouter()


# Dependency Injection Providers
def get_solver_engine() -> SolverEngine:
    return create_standard_okey_solver()


def get_vision_pipeline() -> Optional[Any]:
    return state.vision_pipeline


class ArrangeRequest(BaseModel):
    tiles: List[Tile]
    okey_meta: Optional[OkeyMeta] = None


@router.post("/solver/arrange", response_model=Arrangement)
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


@router.post("/vision/solve", response_model=OrchestratorResult)
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
