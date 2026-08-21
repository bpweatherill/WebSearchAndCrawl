"""Tests for Firefox Controller and Token Manager."""
import pytest
from unittest.mock import AsyncMock, patch
from server.firefox.controller import FirefoxController
from server.firefox.token_manager import TokenManager


@pytest.mark.asyncio
async def test_firefox_controller_start_stop():
    """Test starting and stopping Firefox Controller."""
    controller = FirefoxController()
    
    # Mock Playwright
    with patch("server.firefox.controller.async_playwright") as mock_playwright:
        mock_browser = AsyncMock()
        mock_playwright.return_value.start.return_value = mock_browser
        
        await controller.start()
        assert controller.playwright is not None
        assert controller.browser is not None
        
        await controller.stop()
        assert controller.browser is None
        assert controller.playwright is None


@pytest.mark.asyncio
async def test_firefox_controller_get_page():
    """Test getting a Firefox page."""
    controller = FirefoxController()
    
    # Mock Playwright
    with patch("server.firefox.controller.async_playwright") as mock_playwright:
        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()
        
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_playwright.return_value.start.return_value = mock_browser
        
        page = await controller.get_page()
        assert page is not None


@pytest.mark.asyncio
async def test_token_manager_add_get_token():
    """Test adding and retrieving tokens."""
    manager = TokenManager()
    
    manager.add_token("nasa.gov", "session", "abc123")
    assert manager.get_token("nasa.gov", "session") == "abc123"


@pytest.mark.asyncio
async def test_token_manager_validate_scope():
    """Test validating token scopes."""
    manager = TokenManager()
    
    # Same domain
    assert manager.validate_token_scope("nasa.gov", "nasa.gov") is True
    
    # Subdomain
    assert manager.validate_token_scope("www.nasa.gov", "nasa.gov") is True
    
    # Different domain
    assert manager.validate_token_scope("nasa.gov", "spacex.com") is False


@pytest.mark.asyncio
async def test_token_manager_clear_tokens():
    """Test clearing tokens."""
    manager = TokenManager()
    
    manager.add_token("nasa.gov", "session", "abc123")
    manager.clear_tokens()
    
    assert manager.get_token("nasa.gov", "session") is None
