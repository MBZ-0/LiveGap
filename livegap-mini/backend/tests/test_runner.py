"""Tests for runner module (Site dataclass and loaders)"""
import pytest
from app.runner import Site, load_sites, success_urls_for
from app.models import Goal


def test_site_dataclass():
    """Test Site dataclass creation"""
    site = Site(
        id="test_site",
        name="Test Site",
        url="https://test.com"
    )
    assert site.id == "test_site"
    assert site.name == "Test Site"
    assert site.url == "https://test.com"


def test_load_sites():
    """Test loading sites from YAML config"""
    sites = load_sites()
    assert isinstance(sites, list)
    assert len(sites) > 0
    
    # Check first site has required fields
    first_site = sites[0]
    assert hasattr(first_site, 'id')
    assert hasattr(first_site, 'name')
    assert hasattr(first_site, 'url')
    assert isinstance(first_site.id, str)
    assert isinstance(first_site.name, str)
    assert isinstance(first_site.url, str)


def test_load_sites_caching():
    """Test that sites are cached after first load"""
    sites1 = load_sites()
    sites2 = load_sites()
    # Should return same cached instance
    assert sites1 is sites2


def test_success_urls_for():
    """Test retrieving success URLs for a site and goal"""
    sites = load_sites()
    if sites:
        site_id = sites[0].id
        urls = success_urls_for(site_id, Goal.PRICING)
        assert isinstance(urls, list)
        # URLs could be empty list or contain strings
        for url in urls:
            assert isinstance(url, str)


def test_success_urls_for_nonexistent_site():
    """Test success URLs for non-existent site returns empty list"""
    urls = success_urls_for("nonexistent-site-id", Goal.PRICING)
    assert urls == []


def test_success_urls_for_all_goals():
    """Test success URLs can be retrieved for all goal types"""
    sites = load_sites()
    if sites:
        site_id = sites[0].id
        for goal in Goal:
            urls = success_urls_for(site_id, goal)
            assert isinstance(urls, list)
