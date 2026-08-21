"""Tests for Crawler and Rate Limiter."""
import pytest
from unittest.mock import AsyncMock, patch
from server.crawler.crawler import Crawler
from server.crawler.rate_limiter import RateLimiter
from server.firefox.controller import FirefoxController
from server.firefox.token_manager import TokenManager
from server.schemas import CrawlResult
from datetime import datetime


@pytest.mark.asyncio
async def test_crawler_normalize_domain():
    """Test domain normalization."""
    crawler = Crawler(
        firefox_controller=FirefoxController(),
        token_manager=TokenManager(),
        rate_limiter=RateLimiter()
    )
    
    assert crawler._normalize_domain("www.nasa.gov") == "nasa.gov"
    assert crawler._normalize_domain("NASA.GOV") == "nasa.gov"
    assert crawler._normalize_domain("nasa.gov:8080") == "nasa.gov"


@pytest.mark.asyncio
async def test_crawler_extract_text():
    """Test HTML text extraction."""
    crawler = Crawler(
        firefox_controller=FirefoxController(),
        token_manager=TokenManager(),
        rate_limiter=RateLimiter()
    )
    
    html = "<html><body><p>Hello, world!</p><script>alert('test');</script></body></html>"
    text = crawler._extract_text(html)
    
    assert "Hello, world!" in text
    assert "alert" not in text


@pytest.mark.asyncio
async def test_crawler_extract_links():
    """Test link extraction from HTML."""
    crawler = Crawler(
        firefox_controller=FirefoxController(),
        token_manager=TokenManager(),
        rate_limiter=RateLimiter()
    )
    
    html = '<html><body><a href="https://nasa.gov">NASA</a><a href="/mars">Mars</a></body></html>'
    links = crawler._extract_links(html, "https://nasa.gov")
    
    assert "https://nasa.gov" in links
    assert "https://nasa.gov/mars" in links


@pytest.mark.asyncio
async def test_crawler_requires_js():
    """Test JavaScript requirement detection."""
    crawler = Crawler(
        firefox_controller=FirefoxController(),
        token_manager=TokenManager(),
        rate_limiter=RateLimiter()
    )
    
    assert crawler._requires_js("https://nasa.gov/app/") is True
    assert crawler._requires_js("https://nasa.gov/about") is False


@pytest.mark.asyncio
async def test_rate_limiter():
    """Test rate limiting."""
    limiter = RateLimiter()
    
    async def mock_generator():
        for i in range(3):
            yield i
    
    results = []
    async for item in limiter.rate_limited(mock_generator()):
        results.append(item)
    
    assert results == [0, 1, 2]
