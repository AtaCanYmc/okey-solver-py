# okey_vision/orchestrator.py
from typing import Any, List, Optional, Callable, Dict
from okey_vision.engine import VisionEngine, VisionPipeline
from okey_core.types import Tile, Arrangement, OkeyMeta


class VisionOrchestrator:
    def __init__(
        self,
        pipeline: VisionPipeline,
        okey_meta: Optional[OkeyMeta] = None,
        solve_tiles_fn: Optional[
            Callable[[List[Tile], Optional[OkeyMeta]], Any]
        ] = None,
        observers: Optional[List[Any]] = None,
    ):
        self.vision_engine = VisionEngine(pipeline, observers=observers)
        self.okey_meta = okey_meta
        
        if solve_tiles_fn is None:
            # Lazy import SolverEngine to fully decouple okey_vision from okey_solver
            from okey_solver.solver import SolverEngine
            self.solve_tiles = lambda tiles, meta: SolverEngine.findBestArrangement(tiles, meta)
        else:
            self.solve_tiles = solve_tiles_fn

    def analyze_frame(self, frame: Any) -> Dict[str, Any]:
        tiles = self.vision_engine.process_frame(frame)
        output = self.solve_tiles(tiles, self.okey_meta)
        return {"tiles": tiles, "output": output}


class VisionSolverEngine(VisionOrchestrator):
    def __init__(
        self,
        pipeline: VisionPipeline,
        okey_meta: Optional[OkeyMeta] = None,
        solve_tiles_fn: Optional[
            Callable[[List[Tile], Optional[OkeyMeta]], Arrangement]
        ] = None,
        observers: Optional[List[Any]] = None,
    ):
        super().__init__(pipeline, okey_meta, solve_tiles_fn, observers)

    def analyze_frame(self, frame: Any) -> Dict[str, Any]:
        res = super().analyze_frame(frame)
        return {
            "tiles": res["tiles"],
            "output": res["output"],
            "arrangement": res["output"],
        }
