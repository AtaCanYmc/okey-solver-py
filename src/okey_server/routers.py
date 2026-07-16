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


# ==========================================
# VISION SOLVE ENDPOINTS (Vision + Solver)
# ==========================================

@router.post("/vision/solve/local", response_model=OrchestratorResult)
async def solve_vision_local(
        file: UploadFile = File(...),
        okey_meta_color: Optional[TileColor] = Form(None),
        okey_meta_value: Optional[int] = Form(None),
        model_path: Optional[str] = Form(None),
        pipeline: Optional[Any] = Depends(get_vision_pipeline),
):
    """
    Processes an uploaded board image using a local YOLO model and solves the optimal arrangement.
    """
    from okey_vision.providers import LocalYoloProvider

    active_pipeline = None
    if model_path:
        try:
            active_pipeline = LocalYoloProvider(model_path=model_path)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to initialize request-scoped LocalYoloProvider: {e}"
            )
    elif isinstance(pipeline, LocalYoloProvider):
        active_pipeline = pipeline

    if active_pipeline is None:
        raise HTTPException(
            status_code=400,
            detail="Local YOLO vision provider not configured. Please supply model_path in the request or set YOLO_MODEL_PATH."
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


@router.post("/vision/solve/roboflow", response_model=OrchestratorResult)
async def solve_vision_roboflow(
        file: UploadFile = File(...),
        okey_meta_color: Optional[TileColor] = Form(None),
        okey_meta_value: Optional[int] = Form(None),
        api_key: Optional[str] = Form(None),
        workspace: Optional[str] = Form(None),
        model_id: Optional[str] = Form(None),
        model_version: Optional[int] = Form(1),
        pipeline: Optional[Any] = Depends(get_vision_pipeline),
):
    """
    Processes an uploaded board image using standard Roboflow object detection and solves the optimal arrangement.
    """
    from okey_vision.providers import RoboflowProvider

    active_pipeline = None

    if api_key:
        m_id = model_id or "rummikub-p8akb-vr0ef-2-yolov8n-t1"
        v_num = model_version if model_version is not None else 1
        ws = workspace or "ata-dc7ry"
        try:
            active_pipeline = RoboflowProvider(
                api_key=api_key,
                model_id=m_id,
                model_version=v_num,
                workspace_name=ws
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to initialize request-scoped RoboflowProvider: {e}"
            )
    elif isinstance(pipeline, RoboflowProvider):
        active_pipeline = pipeline

    if active_pipeline is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Roboflow standard provider not configured. "
                "Please supply api_key in the request or set ROBOFLOW_API_KEY."
            )
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


@router.post("/vision/solve/roboflow/workflow", response_model=OrchestratorResult)
async def solve_vision_roboflow_workflow(
        file: UploadFile = File(...),
        okey_meta_color: Optional[TileColor] = Form(None),
        okey_meta_value: Optional[int] = Form(None),
        api_key: Optional[str] = Form(None),
        workspace: Optional[str] = Form(None),
        workflow_id: Optional[str] = Form(None),
        pipeline: Optional[Any] = Depends(get_vision_pipeline),
):
    """
    Processes an uploaded board image using custom Roboflow workflows and solves the optimal arrangement.
    """
    from okey_vision.providers import RoboflowWorkflowProvider

    active_pipeline = None

    if api_key:
        ws = workspace or "ata-dc7ry"
        wf_id = workflow_id or "rummikub-vrummikub-p8akb-vr0ef-3-yolov8n-t1-logic"
        try:
            active_pipeline = RoboflowWorkflowProvider(
                api_key=api_key,
                workspace_name=ws,
                workflow_id=wf_id
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to initialize request-scoped RoboflowWorkflowProvider: {e}"
            )
    elif isinstance(pipeline, RoboflowWorkflowProvider):
        active_pipeline = pipeline

    if active_pipeline is None:
        raise HTTPException(
            status_code=400,
            detail="Roboflow workflow provider not configured. Please supply api_key in the request or set ROBOFLOW_API_KEY."
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


# ==========================================
# VISION EXTRACT ENDPOINTS (Vision Only)
# ==========================================

@router.post("/vision/extract/local", response_model=List[Tile])
async def extract_vision_local(
        file: UploadFile = File(...),
        model_path: Optional[str] = Form(None),
        pipeline: Optional[Any] = Depends(get_vision_pipeline),
):
    """
    Detects and extracts the list of Okey tiles from an uploaded image using local YOLO weights.
    """
    from okey_vision.providers import LocalYoloProvider

    active_pipeline = None
    if model_path:
        try:
            active_pipeline = LocalYoloProvider(model_path=model_path)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to initialize request-scoped LocalYoloProvider: {e}"
            )
    elif isinstance(pipeline, LocalYoloProvider):
        active_pipeline = pipeline

    if active_pipeline is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Local YOLO vision provider not configured. "
                "Please supply model_path in the request or set YOLO_MODEL_PATH."
            )
        )

    try:
        content = await file.read()
        from okey_vision import VisionEngine
        vision_engine = VisionEngine(pipeline=active_pipeline)
        tiles = await vision_engine.process_frame_async(content)
        return tiles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vision/extract/roboflow", response_model=List[Tile])
async def extract_vision_roboflow(
        file: UploadFile = File(...),
        api_key: Optional[str] = Form(None),
        workspace: Optional[str] = Form(None),
        model_id: Optional[str] = Form(None),
        model_version: Optional[int] = Form(1),
        pipeline: Optional[Any] = Depends(get_vision_pipeline),
):
    """
    Detects and extracts the list of Okey tiles from an uploaded image using standard Roboflow models.
    """
    from okey_vision.providers import RoboflowProvider

    active_pipeline = None

    if api_key:
        m_id = model_id or "rummikub-p8akb-vr0ef-2-yolov8n-t1"
        v_num = model_version if model_version is not None else 1
        ws = workspace or "ata-dc7ry"
        try:
            active_pipeline = RoboflowProvider(
                api_key=api_key,
                model_id=m_id,
                model_version=v_num,
                workspace_name=ws
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to initialize request-scoped RoboflowProvider: {e}"
            )
    elif isinstance(pipeline, RoboflowProvider):
        active_pipeline = pipeline

    if active_pipeline is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Roboflow standard provider not configured. "
                "Please supply api_key in the request or set ROBOFLOW_API_KEY."
            )
        )

    try:
        content = await file.read()
        from okey_vision import VisionEngine
        vision_engine = VisionEngine(pipeline=active_pipeline)
        tiles = await vision_engine.process_frame_async(content)
        return tiles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/vision/extract/roboflow/workflow", response_model=List[Tile])
async def extract_vision_roboflow_workflow(
        file: UploadFile = File(...),
        api_key: Optional[str] = Form(None),
        workspace: Optional[str] = Form(None),
        workflow_id: Optional[str] = Form(None),
        pipeline: Optional[Any] = Depends(get_vision_pipeline),
):
    """
    Detects and extracts the list of Okey tiles from an uploaded image using custom Roboflow workflows.
    """
    from okey_vision.providers import RoboflowWorkflowProvider

    active_pipeline = None

    if api_key:
        ws = workspace or "ata-dc7ry"
        wf_id = workflow_id or "rummikub-vrummikub-p8akb-vr0ef-3-yolov8n-t1-logic"
        try:
            active_pipeline = RoboflowWorkflowProvider(
                api_key=api_key,
                workspace_name=ws,
                workflow_id=wf_id
            )
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to initialize request-scoped RoboflowWorkflowProvider: {e}"
            )
    elif isinstance(pipeline, RoboflowWorkflowProvider):
        active_pipeline = pipeline

    if active_pipeline is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Roboflow workflow provider not configured. "
                "Please supply api_key in the request or set ROBOFLOW_API_KEY."
            )
        )

    try:
        content = await file.read()
        from okey_vision import VisionEngine
        vision_engine = VisionEngine(pipeline=active_pipeline)
        tiles = await vision_engine.process_frame_async(content)
        return tiles
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
