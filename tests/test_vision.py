import numpy as np
from okey_vision import (
    VisionSolverEngine,
    DefaultVisionPipeline,
    Detection,
    BoundingBox,
)
from okey_solver import Tile, TileColor, MeldType


def test_vision_solver_engine_orchestration():
    calls = []

    def preprocess_fn(frame):
        calls.append("preprocess")
        return frame

    def detect_fn(frame):
        calls.append("detect")
        return [
            Detection(
                id="d1",
                bounds=BoundingBox(x=0, y=0, width=10, height=10),
                confidence=0.98,
                label="RED-5",
            ),
            Detection(
                id="d2",
                bounds=BoundingBox(x=12, y=0, width=10, height=10),
                confidence=0.98,
                label="RED-6",
            ),
            Detection(
                id="d3",
                bounds=BoundingBox(x=24, y=0, width=10, height=10),
                confidence=0.98,
                label="RED-7",
            ),
        ]

    def classify_fn(frame, detections):
        calls.append("classify")
        assert len(detections) == 3
        return [
            Tile(id="red-5", color=TileColor.RED, value=5),
            Tile(id="red-6", color=TileColor.RED, value=6),
            Tile(id="red-7", color=TileColor.RED, value=7),
        ]

    pipeline = DefaultVisionPipeline(
        detect_fn=detect_fn, classify_fn=classify_fn, preprocess_fn=preprocess_fn
    )

    engine = VisionSolverEngine(pipeline)

    # Create a dummy image array to pass
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)

    res = engine.analyze_frame(dummy_img)

    assert calls == ["preprocess", "detect", "classify"]
    assert len(res["tiles"]) == 3
    assert len(res["arrangement"].melds) == 1
    assert res["arrangement"].melds[0].type == MeldType.SERI
    assert res["arrangement"].totalScore == 18
