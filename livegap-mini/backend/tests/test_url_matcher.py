"""Tests for URL matcher utility"""
import pytest
from app.url_matcher import normalize_url


def test_normalize_url_basic():
    """Test basic URL normalization"""
    assert normalize_url("https://example.com") == "https://example.com/"
    assert normalize_url("https://example.com/") == "https://example.com/"


def test_normalize_url_with_path():
    """Test URL with path"""
    assert normalize_url("https://example.com/path") == "https://example.com/path"
    assert normalize_url("https://example.com/path/") == "https://example.com/path"


def test_normalize_url_removes_query():
    """Test that query parameters are removed"""
    assert normalize_url("https://example.com?foo=bar") == "https://example.com/"
    assert normalize_url("https://example.com/path?foo=bar&baz=qux") == "https://example.com/path"


def test_normalize_url_removes_fragment():
    """Test that URL fragments are removed"""
    assert normalize_url("https://example.com#section") == "https://example.com/"
    assert normalize_url("https://example.com/path#section") == "https://example.com/path"


def test_normalize_url_lowercase():
    """Test that URLs are lowercased"""
    assert normalize_url("https://EXAMPLE.COM/PATH") == "https://example.com/path"
    assert normalize_url("HTTPS://Example.Com/Path") == "https://example.com/path"


def test_normalize_url_complex():
    """Test complex URL with all components"""
    url = "HTTPS://Example.COM/Path/To/Page?query=value#fragment"
    expected = "https://example.com/path/to/page"
    assert normalize_url(url) == expected


def test_normalize_url_trailing_slashes():
    """Test trailing slash handling"""
    assert normalize_url("https://example.com/path/") == "https://example.com/path"
    assert normalize_url("https://example.com/path///") == "https://example.com/path"
