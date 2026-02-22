from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_webhook_handler_success():
    """Test webhook with a valid action."""
    payload = {"action": "test_action"}
    response = client.post("/webhook", json=payload)
    assert response.status_code == 200
    assert response.json() == {"received": True, "event": "test_action"}

def test_webhook_handler_unknown_action():
    """Test webhook with no action field."""
    payload = {"other": "data"}
    response = client.post("/webhook", json=payload)
    assert response.status_code == 200
    assert response.json() == {"received": True, "event": "unknown"}

def test_webhook_handler_empty_payload():
    """Test webhook with empty json payload."""
    response = client.post("/webhook", json={})
    assert response.status_code == 200
    assert response.json() == {"received": True, "event": "unknown"}
