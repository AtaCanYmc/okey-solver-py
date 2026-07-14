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

