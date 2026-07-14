import numpy as np
import pytest
from okey_vision import (
    VisionSolverEngine,
    DefaultVisionPipeline,
    Detection,
    BoundingBox,
    parse_default_tile,
    OkeyVisionError,
    ProviderError,
)
from okey_vision.providers import DEFAULT_COLOR_ALIASES, RoboflowProvider, RoboflowWorkflowProvider
from okey_solver import Tile, TileColor, MeldType
from okey_solver.errors import InvalidTileError


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


def test_invalid_tile_error_raised():
    with pytest.raises(InvalidTileError) as exc_info:
        parse_default_tile(
            Detection(id="det-err", bounds=BoundingBox(x=0, y=0, width=10, height=10), confidence=0.9, label="INVALIDCOLOR-99"),
            0, DEFAULT_COLOR_ALIASES
        )
    assert "Unsupported or unrecognized tile color" in str(exc_info.value)
    assert exc_info.value.payload["label"] == "INVALIDCOLOR-99"

    with pytest.raises(InvalidTileError) as exc_info:
        parse_default_tile(
            Detection(id="det-err-val", bounds=BoundingBox(x=0, y=0, width=10, height=10), confidence=0.9, label="RED-99"),
            0, DEFAULT_COLOR_ALIASES
        )
    assert "Unsupported tile value" in str(exc_info.value)
    assert exc_info.value.payload["parsed_value"] == 99


def test_provider_error_raised_roboflow():
    # Use an invalid URL or key to trigger ProviderError
    provider = RoboflowProvider(api_key="invalid_key")
    provider.base_url = "https://invalid.domain.roboflow.com"
    
    from okey_vision.types import FrameInput
    dummy_frame = FrameInput(data=np.zeros((100, 100, 3), dtype=np.uint8))
    
    with pytest.raises(ProviderError) as exc_info:
        provider.detect(dummy_frame)
    assert "Roboflow API connection failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_provider_error_raised_roboflow_async():
    provider = RoboflowProvider(api_key="invalid_key")
    provider.base_url = "https://invalid.domain.roboflow.com"
    
    from okey_vision.types import FrameInput
    dummy_frame = FrameInput(data=np.zeros((100, 100, 3), dtype=np.uint8))
    
    with pytest.raises(ProviderError) as exc_info:
        await provider.detect_async(dummy_frame)
    assert "Roboflow API async connection failed" in str(exc_info.value)


def test_workflow_provider_error_unexpected_response():
    provider = RoboflowWorkflowProvider(api_key="dummy")
    
    # Mocking run_workflow to return an invalid format
    class MockClient:
        def run_workflow(self, **kwargs):
            return "not-a-dict-or-list"
            
    provider.client = MockClient()
    from okey_vision.types import FrameInput
    dummy_frame = FrameInput(data=np.zeros((100, 100, 3), dtype=np.uint8))
    
    with pytest.raises(ProviderError) as exc_info:
        provider.detect(dummy_frame)
    assert "Unexpected workflow result type" in str(exc_info.value)
