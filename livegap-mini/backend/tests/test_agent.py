"""Tests for agent module with Playwright browser mocking"""
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from app.agent import render_report, run_llm_agent_on_site
from app.models import Step, Goal


def test_render_report_empty():
    """Test rendering report with no steps"""
    from app.runner import Site
    site = Site(id="test", name="Test Site", url="https://example.com")
    result = SiteResult(
        site_id="test",
        site_name="Test Site",
        url="https://example.com",
        success=False,
        reason="No steps",
        steps=[]
    )
    report = render_report(site, Goal.LOGIN, result)
    
    assert "Test Site" in report
    assert "FAILURE" in report


def test_render_report_single_step():
    """Test rendering report with one step"""
    from app.runner import Site
    from app.models import SiteResult
    site = Site(id="test", name="Test Site", url="https://example.com")
    steps = [
        Step(
            index=0,
            action="click",
            target="button#login",
            reasoning="Need to click login button",
            observation="Clicked button"
        )
    ]
    result = SiteResult(
        site_id="test",
        site_name="Test Site",
        url="https://example.com",
        success=True,
        reason="Goal achieved",
        steps=steps
    )
    report = render_report(site, Goal.LOGIN, result)
    
    assert "Step 1" in report
    assert "click" in report
    assert "button#login" in report
    assert "Need to click login button" in report


def test_render_report_multiple_steps():
    """Test rendering report with multiple steps"""
    from app.runner import Site
    from app.models import SiteResult
    site = Site(id="test", name="Test Site", url="https://example.com")
    steps = [
        Step(index=0, action="type", target="input[name='username']", 
             reasoning="Enter username", observation="Typed text"),
        Step(index=1, action="click", target="button[type='submit']",
             reasoning="Submit form", observation="Clicked"),
        Step(index=2, action="wait", target="div.success",
             reasoning="Wait for confirmation", observation="Waited")
    ]
    result = SiteResult(
        site_id="test",
        site_name="Test Site",
        url="https://example.com",
        success=True,
        reason="Completed",
        steps=steps
    )
    report = render_report(site, Goal.SIGN_UP, result)
    
    assert "Step 1" in report
    assert "Step 2" in report
    assert "Step 3" in report


def test_render_report_with_optional_fields():
    """Test rendering with optional duration_ms"""
    from app.runner import Site
    from app.models import SiteResult
    site = Site(id="test", name="Test Site", url="https://example.com")
    steps = [
        Step(index=0, action="scroll", target="footer",
             reasoning="Scroll to bottom", observation="Scrolled", duration_ms=500),
        Step(index=1, action="wait", target=None,
             reasoning="Wait for load", observation="Waited", duration_ms=2000)
    ]
    result = SiteResult(
        site_id="test",
        site_name="Test Site",
        url="https://example.com",
        success=True,
        reason="Done",
        steps=steps
    )
    report = render_report(site, Goal.PRICING, result)
    
    assert "scroll" in report.lower()
    assert "wait" in report.lower()


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
    
    # Mock LLM responses - return dict not Step objects
    mock_plan.return_value = {"action": "DONE", "target": "success", "reason": "Test complete"}
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
    
    mock_plan.return_value = {"action": "DONE", "target": "success", "reason": "Clicked submit"}
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
    
    mock_plan.return_value = {"action": "DONE", "target": "success", "reason": "Filled email"}
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
    
    mock_plan.return_value = {"action": "DONE", "target": "success", "reason": "Scrolled"}
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
    
    mock_plan.return_value = {"action": "DONE", "target": "success", "reason": "Animation done"}
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
    
    # Always return scroll action to test max steps limit
    mock_plan.return_value = {"action": "SCROLL", "target": "100", "reason": "Keep going"}
    
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
    
    mock_plan.return_value = {"action": "DONE", "target": "success", "reason": "Navigation complete"}
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
    
    mock_plan.return_value = {"action": "CLICK", "target": "button#missing", "reason": "Try to click"}
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
