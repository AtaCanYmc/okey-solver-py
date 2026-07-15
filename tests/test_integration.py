# tests/test_integration.py
import os
from pathlib import Path
from fastapi.testclient import TestClient
from okey_server.app import app
from okey_vision.types import Detection, BoundingBox
from okey_core.types import Tile, TileColor
from okey_server.routers import get_vision_pipeline

client = TestClient(app)


class MockPipeline:
    async def preprocess_async(self, frame):
        return frame

    async def detect_async(self, frame):
        return [
            Detection(
                id="v1",
                bounds=BoundingBox(x=10, y=10, width=50, height=50),
                confidence=0.98,
                label="RED-13"
            )
        ]

    async def classify_async(self, frame, detections):
        return [Tile(id="red-13", color=TileColor.RED, value=13)]


def test_integration_solve_image():
    # Resolve the path to the integration test image
    image_path = Path(__file__).parent.parent / ".github" / "screenshots" / "okey-solver-test-image.jpeg"
    assert image_path.exists(), f"Integration test image not found at {image_path}"

    model_path = os.getenv("YOLO_MODEL_PATH")
    rf_key = os.getenv("ROBOFLOW_API_KEY")

    has_live_provider = bool(model_path or rf_key)

    if not has_live_provider:
        app.dependency_overrides[get_vision_pipeline] = lambda: MockPipeline()
        print("[test_integration_solve_image] -> Using MockPipeline for integration test "
              "due to missing YOLO_MODEL_PATH and ROBOFLOW_API_KEY.")

    try:
        with open(image_path, "rb") as img_file:
            files = {"file": ("okey-solver-test-image.jpeg", img_file, "image/jpeg")}
            response = client.post("/api/v1/vision/solve", files=files)

        assert response.status_code == 200
        data = response.json()
        assert "tiles" in data
        assert "arrangement" in data

        if not has_live_provider:
            assert len(data["tiles"]) == 1
            assert data["tiles"][0]["value"] == 13
            assert data["tiles"][0]["color"] == "RED"
    finally:
        app.dependency_overrides.clear()
