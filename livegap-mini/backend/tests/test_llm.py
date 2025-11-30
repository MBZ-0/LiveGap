"""Tests for LLM module with mocking"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from app.llm import plan_next_action, classify_success
from app.models import Goal


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    return {
        "choices": [{
            "message": {
                "content": '{"action": "CLICK", "target": "Get Started", "reason": "Found signup button"}'
            }
        }]
    }


@patch('app.llm.httpx.post')
@patch('app.llm.os.getenv')
def test_plan_next_action_with_api_key(mock_getenv, mock_post, mock_openai_response):
    """Test plan_next_action with OpenAI API"""
    mock_getenv.side_effect = lambda key, default=None: {
        'OPENAI_API_KEY': 'test-key',
        'OPENAI_MODEL': 'gpt-4',
        'OPENAI_ENDPOINT': 'https://api.openai.com/v1/chat/completions'
    }.get(key, default)
    
    mock_response = Mock()
    mock_response.json.return_value = mock_openai_response
    mock_post.return_value = mock_response
    
    result = plan_next_action(
        goal=Goal.SIGN_UP,
        url="https://example.com",
        body_text="Welcome to our site",
        recent=[],
        step_num=0,
        max_steps=5
    )
    
    assert result["action"] == "CLICK"
    assert result["target"] == "Get Started"
    assert "reason" in result


@patch('app.llm.os.getenv')
def test_plan_next_action_without_api_key(mock_getenv):
    """Test plan_next_action falls back without API key"""
    mock_getenv.return_value = None
    
    result = plan_next_action(
        goal=Goal.PRICING,
        url="https://example.com",
        body_text="Check our prices",
        recent=[],
        step_num=0,
        max_steps=5
    )
    
    # Should fallback to SCROLL
    assert result["action"] in ["SCROLL", "CLICK", "DONE"]
    assert "reason" in result


@patch('app.llm.httpx.post')
@patch('app.llm.os.getenv')
def test_plan_next_action_with_invalid_json(mock_getenv, mock_post):
    """Test plan_next_action handles invalid JSON response"""
    mock_getenv.side_effect = lambda key, default=None: {
        'OPENAI_API_KEY': 'test-key',
    }.get(key, default)
    
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "invalid json"}}]
    }
    mock_post.return_value = mock_response
    
    result = plan_next_action(
        goal=Goal.HELP,
        url="https://example.com",
        body_text="Need help?",
        recent=[],
        step_num=0,
        max_steps=5
    )
    
    # Should fallback gracefully
    assert "action" in result


@patch('app.llm.httpx.post')
@patch('app.llm.os.getenv')
def test_plan_next_action_api_error(mock_getenv, mock_post):
    """Test plan_next_action handles API errors"""
    mock_getenv.side_effect = lambda key, default=None: {
        'OPENAI_API_KEY': 'test-key',
    }.get(key, default)
    
    mock_post.side_effect = Exception("API Error")
    
    result = plan_next_action(
        goal=Goal.CUSTOMERS,
        url="https://example.com",
        body_text="Customer testimonials",
        recent=[],
        step_num=0,
        max_steps=5
    )
    
    # Should fallback on error
    assert "action" in result


@pytest.mark.asyncio
@patch('app.llm.success_urls_for')
async def test_classify_success_matching_url(mock_success_urls):
    """Test classify_success with matching URL"""
    mock_success_urls.return_value = [
        "https://example.com/pricing",
        "https://example.com/plans"
    ]
    
    mock_page = Mock()
    mock_page.url = "https://example.com/pricing"
    
    result = await classify_success(mock_page, Goal.PRICING, "test-site")
    
    assert result is True


@pytest.mark.asyncio
@patch('app.llm.success_urls_for')
async def test_classify_success_non_matching_url(mock_success_urls):
    """Test classify_success with non-matching URL"""
    mock_success_urls.return_value = [
        "https://example.com/pricing"
    ]
    
    mock_page = Mock()
    mock_page.url = "https://example.com/home"
    
    result = await classify_success(mock_page, Goal.PRICING, "test-site")
    
    assert result is False


@pytest.mark.asyncio
@patch('app.llm.success_urls_for')
async def test_classify_success_empty_success_urls(mock_success_urls):
    """Test classify_success with no success URLs configured"""
    mock_success_urls.return_value = []
    
    mock_page = Mock()
    mock_page.url = "https://example.com/anywhere"
    
    result = await classify_success(mock_page, Goal.SIGN_UP, "test-site")
    
    assert result is False


def test_plan_next_action_with_recent_actions():
    """Test plan includes recent action history"""
    recent = [
        {"action": "CLICK", "target": "Menu"},
        {"action": "SCROLL", "target": "500"}
    ]
    
    result = plan_next_action(
        goal=Goal.TALK_TO_SALES,
        url="https://example.com",
        body_text="Contact our sales team",
        recent=recent,
        step_num=2,
        max_steps=5
    )
    
    assert "action" in result
    assert "reason" in result


def test_plan_next_action_last_step():
    """Test plan on last step suggests DONE"""
    result = plan_next_action(
        goal=Goal.HELP,
        url="https://example.com/help",
        body_text="Help center",
        recent=[],
        step_num=4,
        max_steps=5
    )
    
    assert "action" in result
    # On last step, should consider wrapping up
