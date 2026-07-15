# tests/test_server.py
from fastapi.testclient import TestClient
from okey_server.app import app


client = TestClient(app)


def test_arrange_hand_endpoint():
    payload = {
        "tiles": [
            {"id": "r5", "color": "RED", "value": 5},
            {"id": "r6", "color": "RED", "value": 6},
            {"id": "r7", "color": "RED", "value": 7}
        ]
    }
    response = client.post("/solver/arrange", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["melds"]) == 1
    assert data["totalScore"] == 18


def test_dependency_override_mock():
    class MockSolver:
        def find_best_arrangement(self, tiles, okey_meta):
            from okey_core.types import Arrangement
            return Arrangement(melds=[], remainingTiles=tiles, totalScore=999)

    from okey_server.app import get_solver_engine
    
    app.dependency_overrides[get_solver_engine] = lambda: MockSolver()
    try:
        payload = {"tiles": []}
        response = client.post("/solver/arrange", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["totalScore"] == 999
    finally:
        app.dependency_overrides.clear()


def test_solve_vision_endpoint():
    from okey_vision.types import Detection, BoundingBox
    from okey_core.types import Tile, TileColor

    class MockPipeline:
        async def preprocess_async(self, frame):
            return frame

        async def detect_async(self, frame):
            return [
                Detection(
                    id="v1",
                    bounds=BoundingBox(x=0, y=0, width=1, height=1),
                    confidence=0.95,
                    label="RED-5"
                )
            ]

        async def classify_async(self, frame, detections):
            return [Tile(id="red-5", color=TileColor.RED, value=5)]

    from okey_server.app import get_vision_pipeline
    app.dependency_overrides[get_vision_pipeline] = lambda: MockPipeline()
    try:
        import io
        file_data = {"file": ("test.jpg", io.BytesIO(b"dummydata"), "image/jpeg")}
        response = client.post("/vision/solve", files=file_data)
        assert response.status_code == 200
        data = response.json()
        assert len(data["tiles"]) == 1
        assert data["tiles"][0]["id"] == "red-5"
        assert data["arrangement"]["totalScore"] == 0
    finally:
        app.dependency_overrides.clear()


def test_solve_vision_with_request_params():
    import io
    file_data = {"file": ("test.jpg", io.BytesIO(b"dummydata"), "image/jpeg")}
    form_data = {"model_path": "non_existent_file.pt"}
    response = client.post("/vision/solve", files=file_data, data=form_data)
    assert response.status_code == 400
    assert "Failed to initialize request-scoped" in response.json()["detail"]


