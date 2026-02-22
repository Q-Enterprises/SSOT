from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    """Verify that the health check endpoint returns a 200 OK status and the expected JSON response."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"status": "alive"}

def test_readiness_check():
    """Verify that the readiness check endpoint returns a 200 OK status and the expected JSON response with a timestamp."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert data["ok"] is True
    assert isinstance(data["ts"], int)
