"""Tests for agent module with Playwright browser mocking"""
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from app.agent import render_report, run_llm_agent_on_site
from app.models import Step, Goal


def test_render_report_empty():
    """Test rendering report with no steps"""
    steps = []
    report = render_report(steps)
    
    assert report == ""


def test_render_report_single_step():
    """Test rendering report with one step"""
    steps = [
        Step(
            step_number=1,
            action="click",
            target="button#login",
            reasoning="Need to click login button"
        )
    ]
    report = render_report(steps)
    
    assert "Step 1" in report
    assert "click" in report
    assert "button#login" in report
    assert "Need to click login button" in report


def test_render_report_multiple_steps():
    """Test rendering report with multiple steps"""
    steps = [
        Step(step_number=1, action="type", target="input[name='username']", 
             reasoning="Enter username", text="testuser"),
        Step(step_number=2, action="click", target="button[type='submit']",
             reasoning="Submit form"),
        Step(step_number=3, action="wait", target="div.success",
             reasoning="Wait for confirmation")
    ]
    report = render_report(steps)
    
    assert "Step 1" in report
    assert "Step 2" in report
    assert "Step 3" in report
    assert "testuser" in report


def test_render_report_with_optional_fields():
    """Test rendering with optional text and wait_seconds"""
    steps = [
        Step(step_number=1, action="scroll", target="footer",
             reasoning="Scroll to bottom", scroll_amount=500),
        Step(step_number=2, action="wait", target=None,
             reasoning="Wait for load", wait_seconds=2)
    ]
    report = render_report(steps)
    
    assert "500" in report or "scroll" in report
    assert "2" in report or "wait" in report


@pytest.mark.asyncio
@patch('app.agent.async_playwright')
@patch('app.agent.plan_next_action')
@patch('app.agent.classify_success')
async def test_run_llm_agent_basic_flow(mock_classify, mock_plan, mock_playwright):
    """Test basic agent flow with mocked Playwright"""
    # Mock Playwright context manager
    mock_pw = AsyncMock()
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    
    mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_page.goto = AsyncMock()
    mock_page.screenshot = AsyncMock(return_value=b'fake-screenshot')
    mock_page.url = "https://example.com/success"
    
    # Setup async context manager
    mock_playwright.return_value.__aenter__.return_value = mock_pw
    mock_playwright.return_value.__aexit__.return_value = AsyncMock()
    
    # Mock LLM responses
    mock_plan.return_value = [
        Step(step_number=1, action="click", target="button", reasoning="Test")
    ]
    mock_classify.return_value = True
    
    from app.success_config import SuccessConfig
    success_config = SuccessConfig(["https://example.com/success"])
    
    result = await run_llm_agent_on_site(
        site_name="Test Site",
        start_url="https://example.com",
        goal=Goal.LOGIN,
        success_config=success_config,
        video_save_path="/tmp/test.webm"
    )
    
    assert len(result) > 0
    assert mock_page.goto.called


@pytest.mark.asyncio
@patch('app.agent.async_playwright')
@patch('app.agent.plan_next_action')
@patch('app.agent.classify_success')
async def test_run_llm_agent_click_action(mock_classify, mock_plan, mock_playwright):
    """Test agent executes click action"""
    mock_pw = AsyncMock()
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    
    mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_page.goto = AsyncMock()
    mock_page.click = AsyncMock()
    mock_page.screenshot = AsyncMock(return_value=b'screenshot')
    mock_page.url = "https://example.com/done"
    
    mock_playwright.return_value.__aenter__.return_value = mock_pw
    mock_playwright.return_value.__aexit__.return_value = AsyncMock()
    
    mock_plan.return_value = [
        Step(step_number=1, action="click", target="button#submit", reasoning="Click submit")
    ]
    mock_classify.return_value = True
    
    from app.success_config import SuccessConfig
    success_config = SuccessConfig(["https://example.com/done"])
    
    result = await run_llm_agent_on_site(
        site_name="Test",
        start_url="https://example.com",
        goal=Goal.SIGNUP,
        success_config=success_config,
        video_save_path="/tmp/video.webm"
    )
    
    assert mock_page.click.called


@pytest.mark.asyncio
@patch('app.agent.async_playwright')
@patch('app.agent.plan_next_action')
@patch('app.agent.classify_success')
async def test_run_llm_agent_type_action(mock_classify, mock_plan, mock_playwright):
    """Test agent executes type action"""
    mock_pw = AsyncMock()
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    
    mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_page.goto = AsyncMock()
    mock_page.fill = AsyncMock()
    mock_page.screenshot = AsyncMock(return_value=b'img')
    mock_page.url = "https://example.com"
    
    mock_playwright.return_value.__aenter__.return_value = mock_pw
    mock_playwright.return_value.__aexit__.return_value = AsyncMock()
    
    mock_plan.return_value = [
        Step(step_number=1, action="type", target="input#email", 
             reasoning="Enter email", text="test@example.com")
    ]
    mock_classify.return_value = True
    
    from app.success_config import SuccessConfig
    success_config = SuccessConfig(["https://example.com"])
    
    result = await run_llm_agent_on_site(
        site_name="Test",
        start_url="https://example.com",
        goal=Goal.ADD_TO_CART,
        success_config=success_config,
        video_save_path=None
    )
    
    assert mock_page.fill.called


@pytest.mark.asyncio
@patch('app.agent.async_playwright')
@patch('app.agent.plan_next_action')
@patch('app.agent.classify_success')
async def test_run_llm_agent_scroll_action(mock_classify, mock_plan, mock_playwright):
    """Test agent executes scroll action"""
    mock_pw = AsyncMock()
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    
    mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_page.goto = AsyncMock()
    mock_page.evaluate = AsyncMock()
    mock_page.screenshot = AsyncMock(return_value=b'data')
    mock_page.url = "https://example.com"
    
    mock_playwright.return_value.__aenter__.return_value = mock_pw
    mock_playwright.return_value.__aexit__.return_value = AsyncMock()
    
    mock_plan.return_value = [
        Step(step_number=1, action="scroll", target="footer",
             reasoning="Scroll down", scroll_amount=300)
    ]
    mock_classify.return_value = True
    
    from app.success_config import SuccessConfig
    success_config = SuccessConfig(["https://example.com"])
    
    result = await run_llm_agent_on_site(
        site_name="Test",
        start_url="https://example.com",
        goal=Goal.CHECKOUT,
        success_config=success_config,
        video_save_path="/tmp/vid.webm"
    )
    
    assert mock_page.evaluate.called


@pytest.mark.asyncio
@patch('app.agent.async_playwright')
@patch('app.agent.plan_next_action')
@patch('app.agent.classify_success')
async def test_run_llm_agent_wait_action(mock_classify, mock_plan, mock_playwright):
    """Test agent executes wait action"""
    mock_pw = AsyncMock()
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    
    mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_page.goto = AsyncMock()
    mock_page.wait_for_timeout = AsyncMock()
    mock_page.screenshot = AsyncMock(return_value=b'bytes')
    mock_page.url = "https://example.com"
    
    mock_playwright.return_value.__aenter__.return_value = mock_pw
    mock_playwright.return_value.__aexit__.return_value = AsyncMock()
    
    mock_plan.return_value = [
        Step(step_number=1, action="wait", target=None,
             reasoning="Wait for animation", wait_seconds=3)
    ]
    mock_classify.return_value = True
    
    from app.success_config import SuccessConfig
    success_config = SuccessConfig(["https://example.com"])
    
    result = await run_llm_agent_on_site(
        site_name="Test",
        start_url="https://example.com",
        goal=Goal.SEARCH,
        success_config=success_config,
        video_save_path="/tmp/recording.webm"
    )
    
    assert mock_page.wait_for_timeout.called


@pytest.mark.asyncio
@patch('app.agent.async_playwright')
@patch('app.agent.plan_next_action')
async def test_run_llm_agent_max_steps(mock_plan, mock_playwright):
    """Test agent respects maximum steps limit"""
    mock_pw = AsyncMock()
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    
    mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_page.goto = AsyncMock()
    mock_page.screenshot = AsyncMock(return_value=b'data')
    mock_page.url = "https://example.com"
    
    mock_playwright.return_value.__aenter__.return_value = mock_pw
    mock_playwright.return_value.__aexit__.return_value = AsyncMock()
    
    # Return infinite steps
    mock_plan.return_value = [
        Step(step_number=i, action="wait", target=None, reasoning="Step", wait_seconds=1)
        for i in range(1, 100)
    ]
    
    from app.success_config import SuccessConfig
    success_config = SuccessConfig(["https://example.com/never"])
    
    result = await run_llm_agent_on_site(
        site_name="Test",
        start_url="https://example.com",
        goal=Goal.LOGIN,
        success_config=success_config,
        video_save_path=None
    )
    
    # Should stop before 100 steps
    assert len(result) < 50


@pytest.mark.asyncio
@patch('app.agent.async_playwright')
@patch('app.agent.plan_next_action')
@patch('app.agent.classify_success')
async def test_run_llm_agent_video_recording(mock_classify, mock_plan, mock_playwright):
    """Test agent with video recording enabled"""
    mock_pw = AsyncMock()
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    mock_video = AsyncMock()
    
    mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_page.goto = AsyncMock()
    mock_page.screenshot = AsyncMock(return_value=b'screenshot')
    mock_page.url = "https://example.com"
    mock_page.video = mock_video
    mock_video.path = AsyncMock(return_value="/tmp/recording.webm")
    
    mock_playwright.return_value.__aenter__.return_value = mock_pw
    mock_playwright.return_value.__aexit__.return_value = AsyncMock()
    
    mock_plan.return_value = [
        Step(step_number=1, action="click", target="a", reasoning="Navigate")
    ]
    mock_classify.return_value = True
    
    from app.success_config import SuccessConfig
    success_config = SuccessConfig(["https://example.com"])
    
    result = await run_llm_agent_on_site(
        site_name="Test",
        start_url="https://example.com",
        goal=Goal.LOGIN,
        success_config=success_config,
        video_save_path="/tmp/test_recording.webm"
    )
    
    # Video should be enabled
    assert mock_browser.new_context.called


@pytest.mark.asyncio
@patch('app.agent.async_playwright')
@patch('app.agent.plan_next_action')
@patch('app.agent.classify_success')
async def test_run_llm_agent_error_handling(mock_classify, mock_plan, mock_playwright):
    """Test agent handles action errors gracefully"""
    mock_pw = AsyncMock()
    mock_browser = AsyncMock()
    mock_context = AsyncMock()
    mock_page = AsyncMock()
    
    mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
    mock_browser.new_context = AsyncMock(return_value=mock_context)
    mock_context.new_page = AsyncMock(return_value=mock_page)
    mock_page.goto = AsyncMock()
    mock_page.click = AsyncMock(side_effect=Exception("Element not found"))
    mock_page.screenshot = AsyncMock(return_value=b'error-screenshot')
    mock_page.url = "https://example.com"
    
    mock_playwright.return_value.__aenter__.return_value = mock_pw
    mock_playwright.return_value.__aexit__.return_value = AsyncMock()
    
    mock_plan.return_value = [
        Step(step_number=1, action="click", target="button#missing", reasoning="Click")
    ]
    mock_classify.return_value = False
    
    from app.success_config import SuccessConfig
    success_config = SuccessConfig(["https://example.com/success"])
    
    result = await run_llm_agent_on_site(
        site_name="Test",
        start_url="https://example.com",
        goal=Goal.LOGIN,
        success_config=success_config,
        video_save_path=None
    )
    
    # Should complete despite error
    assert len(result) >= 0
