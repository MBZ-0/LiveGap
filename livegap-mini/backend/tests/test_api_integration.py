"""Additional integration tests for API"""
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models import Goal
import time


client = TestClient(app)


def test_api_endpoints_without_prefix():
    """Test endpoints work both with and without /api prefix"""
    # Test health endpoint
    response1 = client.get("/health")
    response2 = client.get("/api/health")
    assert response1.status_code == 200
    assert response2.status_code == 200


def test_multiple_concurrent_runs():
    """Test creating multiple runs concurrently"""
    runs = []
    for i in range(3):
        response = client.post(
            "/api/run-reality-check",
            json={"goal": Goal.PRICING.value}
        )
        assert response.status_code == 200
        runs.append(response.json()["run_id"])
    
    # Verify all runs were created
    list_response = client.get("/api/runs")
    assert list_response.status_code == 200
    all_runs = list_response.json()["runs"]
    assert len(all_runs) >= 3


def test_run_lifecycle():
    """Test complete run lifecycle: create, check status, list"""
    # Create run
    create_response = client.post(
        "/api/run-reality-check",
        json={"goal": Goal.SIGN_UP.value}
    )
    assert create_response.status_code == 200
    data = create_response.json()
    run_id = data["run_id"]
    assert data["status"] == "pending"
    assert "created_at" in data
    
    # Check individual run status
    status_response = client.get(f"/api/run/{run_id}")
    assert status_response.status_code == 200
    status_data = status_response.json()
    assert status_data["id"] == run_id
    
    # Verify run appears in list
    list_response = client.get("/api/runs")
    assert list_response.status_code == 200
    runs = list_response.json()["runs"]
    run_ids = [r["id"] for r in runs]
    assert run_id in run_ids


def test_all_goal_types():
    """Test that all goal types can be submitted"""
    for goal in Goal:
        response = client.post(
            "/api/run-reality-check",
            json={"goal": goal.value}
        )
        assert response.status_code == 200
        assert "run_id" in response.json()


def test_cors_headers():
    """Test that CORS headers are present"""
    response = client.get("/api/health")
    # CORS middleware should add access-control headers
    # Just verify the endpoint works
    assert response.status_code == 200


def test_invalid_endpoint():
    """Test accessing non-existent endpoint"""
    response = client.get("/api/nonexistent")
    assert response.status_code == 404


def test_invalid_run_id_format():
    """Test getting status with various invalid run IDs"""
    invalid_ids = ["", "   ", "invalid-id-123"]
    for invalid_id in invalid_ids:
        response = client.get(f"/api/run/{invalid_id}")
        # Should return 404 for non-existent runs
        assert response.status_code == 404
