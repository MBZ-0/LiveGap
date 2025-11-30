"""Tests for runs store module"""
import pytest
from datetime import datetime
from app.runs_store import (
    create_run, get_run, update_run_status, get_all_runs, to_dict, RUNS
)
from app.models import RunResponse, SiteResult, Goal


def setup_function():
    """Clear runs before each test"""
    RUNS.clear()


def test_create_run():
    """Test creating a new run"""
    run_id = "test-run-123"
    run = create_run(run_id)
    
    assert run.id == run_id
    assert run.status == "pending"
    assert run.result is None
    assert run.error is None
    assert isinstance(run.created_at, datetime)


def test_get_run():
    """Test retrieving a run by ID"""
    run_id = "test-run-456"
    created = create_run(run_id)
    
    retrieved = get_run(run_id)
    assert retrieved is not None
    assert retrieved.id == run_id
    assert retrieved == created


def test_get_run_not_found():
    """Test getting non-existent run returns None"""
    result = get_run("nonexistent-run-id")
    assert result is None


def test_update_run_status():
    """Test updating run status"""
    run_id = "test-run-789"
    create_run(run_id)
    
    # Update to running
    update_run_status(run_id, "running")
    run = get_run(run_id)
    assert run.status == "running"
    
    # Update to done with result
    result = RunResponse(
        goal=Goal.PRICING,
        overall_success_rate=50.0,
        total_sites=2,
        successful_sites=1,
        failed_sites=1,
        results=[]
    )
    update_run_status(run_id, "done", result=result)
    run = get_run(run_id)
    assert run.status == "done"
    assert run.result == result


def test_update_run_status_with_error():
    """Test updating run with error"""
    run_id = "test-run-error"
    create_run(run_id)
    
    error_msg = "Something went wrong"
    update_run_status(run_id, "error", error=error_msg)
    
    run = get_run(run_id)
    assert run.status == "error"
    assert run.error == error_msg


def test_get_all_runs():
    """Test getting all runs sorted by creation time"""
    # Create multiple runs
    run1 = create_run("run-1")
    run2 = create_run("run-2")
    run3 = create_run("run-3")
    
    all_runs = get_all_runs()
    assert len(all_runs) == 3
    # Should be sorted newest first (reverse chronological)
    assert all_runs[0].id == "run-3"
    assert all_runs[2].id == "run-1"


def test_to_dict_basic():
    """Test converting run to dictionary"""
    run_id = "test-run-dict"
    run = create_run(run_id)
    
    result_dict = to_dict(run)
    assert result_dict["id"] == run_id
    assert result_dict["status"] == "pending"
    assert "created_at" in result_dict
    assert "result" not in result_dict
    assert "error" not in result_dict


def test_to_dict_with_result():
    """Test converting run with result to dictionary"""
    run_id = "test-run-dict-result"
    run = create_run(run_id)
    
    result = RunResponse(
        goal=Goal.HELP,
        overall_success_rate=100.0,
        total_sites=1,
        successful_sites=1,
        failed_sites=0,
        results=[
            SiteResult(
                site_id="test",
                site_name="Test Site",
                url="https://test.com",
                success=True,
                reason="Success"
            )
        ]
    )
    update_run_status(run_id, "done", result=result)
    
    result_dict = to_dict(run)
    assert result_dict["id"] == run_id
    assert result_dict["status"] == "done"
    assert "result" in result_dict
    assert result_dict["result"]["overall_success_rate"] == 100.0


def test_to_dict_with_error():
    """Test converting run with error to dictionary"""
    run_id = "test-run-dict-error"
    run = create_run(run_id)
    
    error_msg = "Test error"
    update_run_status(run_id, "error", error=error_msg)
    
    result_dict = to_dict(run)
    assert result_dict["id"] == run_id
    assert result_dict["status"] == "error"
    assert "error" in result_dict
    assert result_dict["error"] == error_msg
