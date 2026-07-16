# tests/test_server.py
from fastapi.testclient import TestClient
from okey_server.app import app


client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "0.3.0"}


def test_arrange_hand_endpoint():
    payload = {
        "tiles": [
            {"id": "r5", "color": "RED", "value": 5},
            {"id": "r6", "color": "RED", "value": 6},
            {"id": "r7", "color": "RED", "value": 7},
        ]
    }
    response = client.post("/api/v1/solver/arrange", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["melds"]) == 1
    assert data["totalScore"] == 18


def test_dependency_override_mock():
    class MockSolver:
        def find_best_arrangement(self, tiles, okey_meta):
            from okey_core.types import Arrangement

            return Arrangement(melds=[], remainingTiles=tiles, totalScore=999)

    from okey_server.routers import get_solver_engine

    app.dependency_overrides[get_solver_engine] = lambda: MockSolver()
    try:
        payload = {"tiles": []}
        response = client.post("/api/v1/solver/arrange", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["totalScore"] == 999
    finally:
        app.dependency_overrides.clear()


def test_solve_vision_local_endpoint():
    from okey_vision.types import Detection, BoundingBox
    from okey_core.types import Tile, TileColor
    from okey_vision.providers import LocalYoloProvider

    class MockLocalPipeline(LocalYoloProvider):
        def __init__(self):
            pass

        async def preprocess_async(self, frame):
            return frame

        async def detect_async(self, frame):
            return [
                Detection(
                    id="v1",
                    bounds=BoundingBox(x=0, y=0, width=1, height=1),
                    confidence=0.95,
                    label="RED-5",
                )
            ]

        async def classify_async(self, frame, detections):
            return [Tile(id="red-5", color=TileColor.RED, value=5)]

    from okey_server.dependencies import get_local_yolo_provider

    app.dependency_overrides[get_local_yolo_provider] = lambda: MockLocalPipeline()
    try:
        import io

        file_data = {"file": ("test.jpg", io.BytesIO(b"dummydata"), "image/jpeg")}
        response = client.post("/api/v1/vision/solve/local", files=file_data)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tiles"]) == 1
        assert data["tiles"][0]["id"] == "red-5"
    finally:
        app.dependency_overrides.clear()


def test_solve_vision_roboflow_endpoint():
    from okey_vision.types import Detection, BoundingBox
    from okey_core.types import Tile, TileColor
    from okey_vision.providers import RoboflowProvider

    class MockRoboflowPipeline(RoboflowProvider):
        def __init__(self):
            pass

        async def preprocess_async(self, frame):
            return frame

        async def detect_async(self, frame):
            return [
                Detection(
                    id="v1",
                    bounds=BoundingBox(x=0, y=0, width=1, height=1),
                    confidence=0.95,
                    label="BLUE-8",
                )
            ]

        async def classify_async(self, frame, detections):
            return [Tile(id="blue-8", color=TileColor.BLUE, value=8)]

    from okey_server.dependencies import get_roboflow_provider

    app.dependency_overrides[get_roboflow_provider] = lambda: MockRoboflowPipeline()
    try:
        import io

        file_data = {"file": ("test.jpg", io.BytesIO(b"dummydata"), "image/jpeg")}
        response = client.post("/api/v1/vision/solve/roboflow", files=file_data)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tiles"]) == 1
        assert data["tiles"][0]["id"] == "blue-8"
    finally:
        app.dependency_overrides.clear()


def test_solve_vision_roboflow_workflow_endpoint():
    from okey_vision.types import Detection, BoundingBox
    from okey_core.types import Tile, TileColor
    from okey_vision.providers import RoboflowWorkflowProvider

    class MockWorkflowPipeline(RoboflowWorkflowProvider):
        def __init__(self):
            pass

        async def preprocess_async(self, frame):
            return frame

        async def detect_async(self, frame):
            return [
                Detection(
                    id="v1",
                    bounds=BoundingBox(x=0, y=0, width=1, height=1),
                    confidence=0.95,
                    label="BLACK-11",
                )
            ]

        async def classify_async(self, frame, detections):
            return [Tile(id="black-11", color=TileColor.BLACK, value=11)]

    from okey_server.dependencies import get_roboflow_workflow_provider

    app.dependency_overrides[get_roboflow_workflow_provider] = lambda: (
        MockWorkflowPipeline()
    )
    try:
        import io

        file_data = {"file": ("test.jpg", io.BytesIO(b"dummydata"), "image/jpeg")}
        response = client.post(
            "/api/v1/vision/solve/roboflow/workflow", files=file_data
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["tiles"]) == 1
        assert data["tiles"][0]["id"] == "black-11"
    finally:
        app.dependency_overrides.clear()


# ==========================================
# EXTRACTIONS TESTS
# ==========================================


def test_extract_vision_local_endpoint():
    from okey_vision.types import Detection, BoundingBox
    from okey_core.types import Tile, TileColor
    from okey_vision.providers import LocalYoloProvider

    class MockLocalPipeline(LocalYoloProvider):
        def __init__(self):
            pass

        async def preprocess_async(self, frame):
            return frame

        async def detect_async(self, frame):
            return [
                Detection(
                    id="v1",
                    bounds=BoundingBox(x=0, y=0, width=1, height=1),
                    confidence=0.95,
                    label="RED-5",
                )
            ]

        async def classify_async(self, frame, detections):
            return [Tile(id="red-5", color=TileColor.RED, value=5)]

    from okey_server.dependencies import get_local_yolo_provider

    app.dependency_overrides[get_local_yolo_provider] = lambda: MockLocalPipeline()
    try:
        import io

        file_data = {"file": ("test.jpg", io.BytesIO(b"dummydata"), "image/jpeg")}
        response = client.post("/api/v1/vision/extract/local", files=file_data)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["tiles"], list)
        assert len(data["tiles"]) == 1
        assert data["tiles"][0]["id"] == "red-5"
    finally:
        app.dependency_overrides.clear()


def test_extract_vision_roboflow_endpoint():
    from okey_vision.types import Detection, BoundingBox
    from okey_core.types import Tile, TileColor
    from okey_vision.providers import RoboflowProvider

    class MockRoboflowPipeline(RoboflowProvider):
        def __init__(self):
            pass

        async def preprocess_async(self, frame):
            return frame

        async def detect_async(self, frame):
            return [
                Detection(
                    id="v1",
                    bounds=BoundingBox(x=0, y=0, width=1, height=1),
                    confidence=0.95,
                    label="BLUE-8",
                )
            ]

        async def classify_async(self, frame, detections):
            return [Tile(id="blue-8", color=TileColor.BLUE, value=8)]

    from okey_server.dependencies import get_roboflow_provider

    app.dependency_overrides[get_roboflow_provider] = lambda: MockRoboflowPipeline()
    try:
        import io

        file_data = {"file": ("test.jpg", io.BytesIO(b"dummydata"), "image/jpeg")}
        response = client.post("/api/v1/vision/extract/roboflow", files=file_data)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["tiles"], list)
        assert len(data["tiles"]) == 1
        assert data["tiles"][0]["id"] == "blue-8"
    finally:
        app.dependency_overrides.clear()


def test_extract_vision_roboflow_workflow_endpoint():
    from okey_vision.types import Detection, BoundingBox
    from okey_core.types import Tile, TileColor
    from okey_vision.providers import RoboflowWorkflowProvider

    class MockWorkflowPipeline(RoboflowWorkflowProvider):
        def __init__(self):
            pass

        async def preprocess_async(self, frame):
            return frame

        async def detect_async(self, frame):
            return [
                Detection(
                    id="v1",
                    bounds=BoundingBox(x=0, y=0, width=1, height=1),
                    confidence=0.95,
                    label="BLACK-11",
                )
            ]

        async def classify_async(self, frame, detections):
            return [Tile(id="black-11", color=TileColor.BLACK, value=11)]

    from okey_server.dependencies import get_roboflow_workflow_provider

    app.dependency_overrides[get_roboflow_workflow_provider] = lambda: (
        MockWorkflowPipeline()
    )
    try:
        import io

        file_data = {"file": ("test.jpg", io.BytesIO(b"dummydata"), "image/jpeg")}
        response = client.post(
            "/api/v1/vision/extract/roboflow/workflow", files=file_data
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["tiles"], list)
        assert len(data["tiles"]) == 1
        assert data["tiles"][0]["id"] == "black-11"
    finally:
        app.dependency_overrides.clear()


def test_solve_vision_local_with_request_params():
    import io

    file_data = {"file": ("test.jpg", io.BytesIO(b"dummydata"), "image/jpeg")}
    form_data = {"model_path": "non_existent_file.pt"}
    response = client.post(
        "/api/v1/vision/solve/local", files=file_data, data=form_data
    )
    assert response.status_code == 400
    assert "Failed to initialize request-scoped" in response.json()["detail"]


def test_solve_vision_roboflow_request_params():
    from PIL import Image
    import io

    img = Image.new("RGB", (10, 10), color="red")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    file_data = {"file": ("test.jpg", img_bytes, "image/jpeg")}
    form_data = {
        "api_key": "mock_api_key",
        "workspace": "mock_workspace",
        "model_id": "mock_model_id",
        "model_version": 1,
    }
    response = client.post(
        "/api/v1/vision/solve/roboflow", files=file_data, data=form_data
    )
    # Lazy load succeeds in constructor, but detect fails due to invalid api_key connection error (500)
    assert response.status_code == 500
    assert (
        "Roboflow API connection failed" in response.json()["detail"]
        or "Roboflow API async connection failed" in response.json()["detail"]
    )


def test_solve_vision_roboflow_workflow_request_params():
    from PIL import Image
    import io

    img = Image.new("RGB", (10, 10), color="red")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="JPEG")
    img_bytes.seek(0)

    file_data = {"file": ("test.jpg", img_bytes, "image/jpeg")}
    form_data = {
        "api_key": "mock_api_key",
        "workspace": "mock_workspace",
        "workflow_id": "mock_workflow_id",
        "api_url": "https://detect.roboflow.com",
    }
    response = client.post(
        "/api/v1/vision/solve/roboflow/workflow", files=file_data, data=form_data
    )
    # Reaches run_workflow and fails to connect to mock_api_key (500)
    assert response.status_code == 500
    assert "Error querying Roboflow Workflow API" in response.json()["detail"]


def test_file_validation_size_limit():
    import io

    # Create large dummy content (11MB)
    large_data = io.BytesIO(b"0" * (11 * 1024 * 1024))
    file_data = {"file": ("large.jpg", large_data, "image/jpeg")}

    response = client.post("/api/v1/vision/solve/local", files=file_data)
    assert response.status_code == 413
    assert "File too large" in response.json()["detail"]


def test_file_validation_mime_type():
    import io

    invalid_data = io.BytesIO(b"plain text file content")
    file_data = {"file": ("text.txt", invalid_data, "text/plain")}

    response = client.post("/api/v1/vision/solve/local", files=file_data)
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["detail"]


def test_vision_provider_registry_caching():
    from unittest.mock import patch
    from okey_server.registry import VisionProviderRegistry

    registry = VisionProviderRegistry()

    with patch("okey_vision.providers.LocalYoloProvider") as mock_yolo:
        mock_yolo.return_value = "mock_instance_1"
        provider1 = registry.get_local_yolo_provider("weights.pt")
        provider2 = registry.get_local_yolo_provider("weights.pt")

        mock_yolo.assert_called_once_with(model_path="weights.pt")
        assert provider1 == "mock_instance_1"
        assert provider2 == "mock_instance_1"
