"""Tests for Pydantic models"""
import pytest
from app.models import (
    Goal, RunRequest, Step, SiteResult, RunResponse
)


def test_goal_enum():
    """Test Goal enum values"""
    # Test that all goal enums exist and have values
    assert hasattr(Goal, 'TALK_TO_SALES')
    assert hasattr(Goal, 'PRICING')
    assert hasattr(Goal, 'SIGN_UP')
    assert hasattr(Goal, 'HELP')
    assert hasattr(Goal, 'CUSTOMERS')
    
    # Test that values are non-empty strings
    assert isinstance(Goal.TALK_TO_SALES.value, str)
    assert len(Goal.TALK_TO_SALES.value) > 0
    assert isinstance(Goal.PRICING.value, str)
    assert len(Goal.PRICING.value) > 0


def test_run_request_model():
    """Test RunRequest model"""
    req = RunRequest(goal=Goal.PRICING)
    assert req.goal == Goal.PRICING
    assert isinstance(req.goal, Goal)


def test_step_model():
    """Test Step model with all fields"""
    step = Step(
        index=0,
        action="CLICK",
        target="button",
        observation="Clicked button",
        reasoning="Need to click the button",
        succeeded=True,
        done=False,
        url_before="https://example.com",
        url_after="https://example.com/next",
        duration_ms=500,
        error_type=None
    )
    assert step.index == 0
    assert step.action == "CLICK"
    assert step.succeeded is True
    assert step.done is False
    assert step.duration_ms == 500


def test_step_model_minimal():
    """Test Step model with minimal required fields"""
    step = Step(
        index=1,
        action="SCROLL",
        target=None
    )
    assert step.index == 1
    assert step.action == "SCROLL"
    assert step.target is None
    assert step.succeeded is None
    assert step.done is False


def test_site_result_model():
    """Test SiteResult model"""
    result = SiteResult(
        site_id="test_site",
        site_name="Test Site",
        url="https://test.com",
        success=True,
        reason="Goal achieved",
        video_url="https://example.com/video.mp4",
        steps=[
            Step(index=0, action="CLICK", target="button")
        ],
        report="# Test Report"
    )
    assert result.site_id == "test_site"
    assert result.success is True
    assert result.video_url == "https://example.com/video.mp4"
    assert len(result.steps) == 1
    assert result.report == "# Test Report"


def test_site_result_model_minimal():
    """Test SiteResult with minimal required fields"""
    result = SiteResult(
        site_id="test",
        site_name="Test",
        url="https://test.com",
        success=False,
        reason="Failed"
    )
    assert result.site_id == "test"
    assert result.success is False
    assert result.video_url is None
    assert result.steps is None


def test_run_response_model():
    """Test RunResponse model"""
    response = RunResponse(
        goal=Goal.HELP,
        overall_success_rate=75.0,
        total_sites=4,
        successful_sites=3,
        failed_sites=1,
        results=[
            SiteResult(
                site_id="site1",
                site_name="Site 1",
                url="https://site1.com",
                success=True,
                reason="Success"
            )
        ]
    )
    assert response.goal == Goal.HELP
    assert response.overall_success_rate == 75.0
    assert response.total_sites == 4
    assert response.successful_sites == 3
    assert response.failed_sites == 1
    assert len(response.results) == 1
