from playwright.async_api import async_playwright
from typing import Optional, Dict, Any
from pathlib import Path
from server.config import settings
import asyncio
import logging

logger = logging.getLogger(__name__)

class FirefoxController:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self._lock = asyncio.Lock()
        self._profile_path = settings.firefox_profile_path

    async def start(self) -> None:
        """Start Playwright and Firefox."""
        if self.playwright is None:
            self.playwright = await async_playwright().start()
            logger.info("Playwright started.")
        if self.browser is None:
            self.browser = await self.playwright.firefox.launch(
                headless=True,
                firefox_user_prefs={
                    "browser.download.folderList": 2,
                    "browser.download.dir": str(Path(settings.downloads_dir).absolute()),
                }
            )
            logger.info("Firefox browser launched.")

    async def stop(self) -> None:
        """Stop Playwright and Firefox."""
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
        logger.info("Firefox browser and Playwright stopped.")

    async def get_page(self, profile: Optional[str] = None) -> Any:
        """Get a Firefox page with a specific profile or default."""
        await self.start()
        async with self._lock:
            if self.context is None:
                # Use custom profile if specified
                if profile or self._profile_path:
                    profile_path = self._profile_path or f"~/.mozilla/firefox/{profile}"
                    self.context = await self.browser.new_context(
                        firefox_user_prefs={
                            "profile.default_content_setting_values.notifications": 2,  # Disable notifications
                        },
                        user_agent="Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
                        viewport={"width": 1920, "height": 1080},
                    )
                else:
                    self.context = await self.browser.new_context()
            if self.page is None:
                self.page = await self.context.new_page()
            return self.page

    async def navigate(self, url: str, wait_until: str = "domcontentloaded") -> bool:
        """Navigate to a URL and wait for the page to load."""
        page = await self.get_page()
        try:
            await page.goto(url, wait_until=wait_until, timeout=settings.request_timeout_seconds * 1000)
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {e}")
            return False

    async def get_session_cookies(self, url: str) -> Dict[str, str]:
        """Get session cookies for a specific URL."""
        page = await self.get_page()
        await self.navigate(url)
        cookies = await page.context.cookies()
        return {cookie["name"]: cookie["value"] for cookie in cookies}

    async def save_session_tokens(self, domain: str, tokens: Dict[str, str]) -> None:
        """Save session tokens to memory (in-memory only)."""
        # TODO: Implement in TokenManager (Phase 2)
        pass

    async def login(self, url: str, credentials: Optional[Dict[str, str]] = None) -> bool:
        """Log in to a website (placeholder for future automation)."""
        # TODO: Implement login logic (e.g., fill forms, click buttons)
        logger.warning("Login automation not yet implemented.")
        return False
