# okey_orchestrator/orchestrator.py
import asyncio
from typing import Any, List, Optional, Callable
from okey_vision.engine import VisionEngine, VisionPipeline
from okey_solver import create_standard_okey_solver, SolverEngine
from okey_core.types import Tile, Arrangement, OkeyMeta, OrchestratorResult


class VisionOrchestrator:
    def __init__(
        self,
        pipeline: VisionPipeline,
        okey_meta: Optional[OkeyMeta] = None,
        solve_tiles_fn: Optional[
            Callable[[List[Tile], Optional[OkeyMeta]], Any]
        ] = None,
        observers: Optional[List[Any]] = None,
        solver: Optional[SolverEngine] = None,
    ):
        self.vision_engine = VisionEngine(pipeline, observers=observers)
        self.okey_meta = okey_meta
        self.solver = solver or create_standard_okey_solver()
        self.solve_tiles = solve_tiles_fn or (
            lambda tiles, meta: self.solver.find_best_arrangement(tiles, meta)
        )

    def analyze_frame(self, frame: Any) -> OrchestratorResult:
        tiles = self.vision_engine.process_frame(frame)
        output = self.solve_tiles(tiles, self.okey_meta)
        arrangement = output if isinstance(output, Arrangement) else None
        return OrchestratorResult(tiles=tiles, arrangement=arrangement)

    async def analyze_frame_async(self, frame: Any) -> OrchestratorResult:
        tiles = await self.vision_engine.process_frame_async(frame)
        output = await asyncio.to_thread(self.solve_tiles, tiles, self.okey_meta)
        arrangement = output if isinstance(output, Arrangement) else None
        return OrchestratorResult(tiles=tiles, arrangement=arrangement)


class VisionSolverEngine:
    """
    Composition wrapper offering a clean, type-safe solver-orchestration layout.
    """

    def __init__(
        self,
        pipeline: VisionPipeline,
        okey_meta: Optional[OkeyMeta] = None,
        solve_tiles_fn: Optional[
            Callable[[List[Tile], Optional[OkeyMeta]], Arrangement]
        ] = None,
        observers: Optional[List[Any]] = None,
        solver: Optional[SolverEngine] = None,
        strategy: str = "backtracking",
    ):
        resolved_solver = solver or create_standard_okey_solver(strategy=strategy)
        self.orchestrator = VisionOrchestrator(
            pipeline=pipeline,
            okey_meta=okey_meta,
            solve_tiles_fn=solve_tiles_fn,
            observers=observers,
            solver=resolved_solver,
        )

    def analyze_frame(self, frame: Any) -> OrchestratorResult:
        return self.orchestrator.analyze_frame(frame)

    async def analyze_frame_async(self, frame: Any) -> OrchestratorResult:
        return await self.orchestrator.analyze_frame_async(frame)
