"""Tests for success_config module"""
import pytest
from app.success_config import get_success_urls
from app.models import Goal


def test_get_success_urls():
    """Test getting success URLs for a site and goal"""
    # This is a wrapper around success_urls_for
    urls = get_success_urls("test-site", Goal.PRICING)
    assert isinstance(urls, list)
    # Should return empty list for non-existent site
    assert urls == []


def test_get_success_urls_all_goals():
    """Test getting success URLs for all goal types"""
    for goal in Goal:
        urls = get_success_urls("test-site", goal)
        assert isinstance(urls, list)
