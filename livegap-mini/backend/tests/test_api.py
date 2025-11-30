"""Tests for FastAPI endpoints"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Goal


client = TestClient(app)


def test_health_endpoint():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_health_endpoint():
    """Test API health endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_run_reality_check_endpoint():
    """Test reality check endpoint returns immediately with run_id"""
    response = client.post(
        "/api/run-reality-check",
        json={"goal": Goal.PRICING.value}
    )
    assert response.status_code == 200
    data = response.json()
    assert "run_id" in data
    assert "status" in data
    assert "created_at" in data
    assert data["status"] == "pending"


def test_get_run_status_not_found():
    """Test getting status for non-existent run"""
    response = client.get("/api/run/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Run not found"


def test_list_runs_endpoint():
    """Test listing all runs"""
    response = client.get("/api/runs")
    assert response.status_code == 200
    data = response.json()
    assert "runs" in data
    assert isinstance(data["runs"], list)


def test_run_reality_check_and_status():
    """Test creating a run and checking its status"""
    # Create a run
    create_response = client.post(
        "/api/run-reality-check",
        json={"goal": Goal.TALK_TO_SALES.value}
    )
    assert create_response.status_code == 200
    run_id = create_response.json()["run_id"]
    
    # Check status immediately (should be pending or running)
    status_response = client.get(f"/api/run/{run_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["id"] == run_id  # API returns 'id' not 'run_id'
    assert status_data["status"] in ["pending", "running", "done", "error"]


def test_invalid_goal():
    """Test API with invalid goal"""
    response = client.post(
        "/api/run-reality-check",
        json={"goal": "invalid-goal-value"}
    )
    assert response.status_code == 422  # Validation error
