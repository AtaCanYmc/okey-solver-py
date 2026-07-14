import numpy as np
import pytest
from okey_vision import (
    VisionSolverEngine,
    DefaultVisionPipeline,
    Detection,
    BoundingBox,
    parse_default_tile,
)
from okey_vision.providers import DEFAULT_COLOR_ALIASES
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


def test_fuzzy_label_matching():
    # Standard labels
    t1 = parse_default_tile(
        Detection(id="1", bounds=BoundingBox(x=0, y=0, width=1, height=1), confidence=1.0, label="RED-5"),
        0, DEFAULT_COLOR_ALIASES
    )
    assert t1.color == TileColor.RED
    assert t1.value == 5

    # Confused digits (OCR confusions)
    t2 = parse_default_tile(
        Detection(id="2", bounds=BoundingBox(x=0, y=0, width=1, height=1), confidence=1.0, label="RED-S"),
        0, DEFAULT_COLOR_ALIASES
    )
    assert t2.color == TileColor.RED
    assert t2.value == 5

    # Turkey colors and character aliases
    t3 = parse_default_tile(
        Detection(id="3", bounds=BoundingBox(x=0, y=0, width=1, height=1), confidence=1.0, label="MAVI-1I"),
        0, DEFAULT_COLOR_ALIASES
    )
    assert t3.color == TileColor.BLUE
    assert t3.value == 11

    # Typo / fuzzy matching on color
    t4 = parse_default_tile(
        Detection(id="4", bounds=BoundingBox(x=0, y=0, width=1, height=1), confidence=1.0, label="R3D-5"),
        0, DEFAULT_COLOR_ALIASES
    )
    assert t4.color == TileColor.RED
    assert t4.value == 5


@pytest.mark.asyncio
async def test_async_vision_pipeline():
    calls = []

    async def detect_async(frame):
        calls.append("detect_async")
        return [
            Detection(
                id="d1",
                bounds=BoundingBox(x=0, y=0, width=10, height=10),
                confidence=0.98,
                label="RED-5",
            )
        ]

    pipeline = DefaultVisionPipeline(
        detect_fn=lambda f: [],
        classify_fn=lambda f, d: [Tile(id="red-5", color=TileColor.RED, value=5)],
        detect_async_fn=detect_async
    )

    engine = VisionSolverEngine(pipeline)
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)

    res = await engine.vision_engine.process_frame_async(dummy_img)

    assert "detect_async" in calls
    assert len(res) == 1
    assert res[0].color == TileColor.RED
