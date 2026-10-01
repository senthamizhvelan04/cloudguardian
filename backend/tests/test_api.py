from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

# Default API key from .env.example / config defaults
AUTH_HEADER = {"x-api-key": "change-me"}

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_unauthenticated_create_rejected():
    payload = {
        "type": "HIGH_CPU",
        "instance": "i-test",
        "severity": "HIGH",
        "description": "CPU above 80%",
        "cpu": 85
    }
    r = client.post("/api/v1/incidents", json=payload)
    assert r.status_code == 401

def test_incident_lifecycle():
    payload = {
        "type": "HIGH_CPU",
        "instance": "i-test",
        "severity": "HIGH",
        "description": "CPU above 80%",
        "cpu": 85
    }
    r = client.post("/api/v1/incidents", json=payload, headers=AUTH_HEADER)
    assert r.status_code == 201
    incident_id = r.json()["id"]

    r = client.post(f"/api/v1/incidents/{incident_id}/diagnose", headers=AUTH_HEADER)
    assert r.status_code == 200
    assert r.json()["approval_required"] is True

    r = client.post(f"/api/v1/incidents/{incident_id}/approve", json={
        "action": "restart_service",
        "approved_by": "operator",
        "approved": True
    }, headers=AUTH_HEADER)
    assert r.status_code == 200

    r = client.post(f"/api/v1/incidents/{incident_id}/remediate", json={
        "action": "restart_service"
    }, headers=AUTH_HEADER)
    assert r.status_code == 200

    r = client.post(f"/api/v1/incidents/{incident_id}/verify", headers=AUTH_HEADER)
    assert r.status_code == 200
    assert r.json()["status"] == "RESOLVED"

def test_list_incidents_no_auth_required():
    r = client.get("/api/v1/incidents")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
