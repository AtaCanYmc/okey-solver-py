# okey_server/routers.py
import logging
from typing import List, Optional, Any
from fastapi import APIRouter, Depends, Form, HTTPException
from pydantic import BaseModel
from okey_core.types import Tile, OkeyMeta, Arrangement, OrchestratorResult, TileColor
from okey_solver import SolverEngine
from okey_vision.errors import OkeyVisionError

from okey_server.dependencies import (
    get_solver_engine,
    validate_image_file,
    get_roboflow_workflow_provider,
)

logger = logging.getLogger("okey_server.routers")
router = APIRouter()


class ArrangeRequest(BaseModel):
    tiles: List[Tile]
    okey_meta: Optional[OkeyMeta] = None


class ExtractResult(BaseModel):
    tiles: List[Tile]
    raw: Optional[Any] = None


async def run_vision_safe(coro) -> Any:
    """
    Helper to run vision coroutines safely. Maps expected OkeyVisionErrors to HTTPExceptions
    with original messages, and maps unexpected errors to generic 500 HTTPExceptions.
    """
    try:
        return await coro
    except OkeyVisionError as e:
        logger.exception("Vision provider error occurred")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected server error in vision pipeline")
        raise HTTPException(
            status_code=500, detail="An internal server error occurred."
        )


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
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected server error in solver")
        raise HTTPException(
            status_code=500, detail="An internal server error occurred."
        )


# ==========================================
# VISION SOLVE ENDPOINT (Vision + Solver)
# ==========================================


@router.post("/vision/solve", response_model=OrchestratorResult)
async def solve_vision(
    okey_meta_color: Optional[TileColor] = Form(None),
    okey_meta_value: Optional[int] = Form(None),
    image_content: bytes = Depends(validate_image_file),
    pipeline: Any = Depends(get_roboflow_workflow_provider),
):
    """
    Processes an uploaded board image using Roboflow workflows and solves the optimal arrangement.
    """
    from okey_orchestrator import VisionSolverEngine

    okey_meta = None
    if okey_meta_color and okey_meta_value is not None:
        okey_meta = OkeyMeta(color=okey_meta_color, value=okey_meta_value)

    engine = VisionSolverEngine(pipeline=pipeline, okey_meta=okey_meta)
    return await run_vision_safe(engine.analyze_frame_async(image_content))


# ==========================================
# VISION EXTRACT ENDPOINT (Vision Only)
# ==========================================


@router.post("/vision/extract", response_model=ExtractResult)
async def extract_vision(
    image_content: bytes = Depends(validate_image_file),
    pipeline: Any = Depends(get_roboflow_workflow_provider),
):
    """
    Detects and extracts the list of Okey tiles from an uploaded image using Roboflow workflows.
    """
    from okey_vision import VisionEngine

    vision_engine = VisionEngine(pipeline=pipeline)
    tiles = await run_vision_safe(vision_engine.process_frame_async(image_content))
    raw_val = getattr(pipeline, "last_raw_response", None)
    return ExtractResult(tiles=tiles, raw=raw_val)
