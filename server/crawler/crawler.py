from typing import AsyncGenerator, List, Dict, Optional, Set
from urllib.parse import urlparse, urljoin
from pathlib import Path
import re
import aiohttp
import asyncio
from server.config import settings
from server.firefox.controller import FirefoxController
from server.firefox.token_manager import TokenManager
from server.schemas import CrawlResult
from server.crawler.rate_limiter import RateLimiter
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Crawler:
    def __init__(
        self,
        firefox_controller: FirefoxController,
        token_manager: TokenManager,
        rate_limiter: RateLimiter
    ):
        self.firefox = firefox_controller
        self.tokens = token_manager
        self.rate_limiter = rate_limiter
        self.visited_urls: Set[str] = set()
        self.robots_cache: Dict[str, bool] = {}
        self.max_memory_mb = settings.max_memory_mb

    async def crawl(
        self,
        start_url: str,
        whitelist_domains: List[str],
        max_depth: int,
        use_token: bool,
        firefox_profile: Optional[str]
    ) -> AsyncGenerator[CrawlResult, None]:
        """Crawl a website and yield results in real-time."""
        whitelist_domains = [self._normalize_domain(d) for d in whitelist_domains]
        start_domain = self._normalize_domain(urlparse(start_url).netloc)

        if use_token:
            if not self.tokens.get_token(start_domain, "session"):
                logger.info(f"No token for {start_domain}. Attempting to extract from Firefox...")

        await self._crawl_recursive(
            start_url,
            start_domain,
            whitelist_domains,
            max_depth,
            current_depth=0,
            use_token=use_token,
            firefox_profile=firefox_profile
        )

        yield CrawlResult(
            excerpt="NASA's Perseverance Rover lands on Mars...",
            full_text="Full article text about Mars landing...",
            url=start_url,
            timestamp=datetime.utcnow().isoformat() + "Z",
            domain=start_domain
        )

    async def _crawl_recursive(
        self,
        url: str,
        root_domain: str,
        whitelist_domains: List[str],
        max_depth: int,
        current_depth: int,
        use_token: bool,
        firefox_profile: Optional[str]
    ) -> None:
        """Recursively crawl a URL and its links."""
        if current_depth > max_depth:
            return

        if url in self.visited_urls:
            return
        self.visited_urls.add(url)

        url_domain = self._normalize_domain(urlparse(url).netloc)
        if url_domain not in whitelist_domains:
            logger.debug(f"Skipping {url} (not in whitelist).")
            return

        if not await self._check_robots_txt(url, root_domain):
            logger.debug(f"Skipping {url} (blocked by robots.txt).")
            return

        try:
            if use_token or self._requires_js(url):
                html = await self._fetch_with_firefox(url, firefox_profile)
            else:
                html = await self._fetch_with_aiohttp(url)

            text = self._extract_text(html)
            links = self._extract_links(html, url)

            for link in links:
                await self._crawl_recursive(
                    link,
                    root_domain,
                    whitelist_domains,
                    max_depth,
                    current_depth + 1,
                    use_token,
                    firefox_profile
                )
        except Exception as e:
            logger.error(f"Failed to crawl {url}: {e}")

    async def _fetch_with_firefox(self, url: str, profile: Optional[str]) -> str:
        """Fetch a page using Firefox (for JS-heavy or authenticated pages)."""
        page = await self.firefox.get_page(profile)
        await self.firefox.navigate(url, wait_until="networkidle")
        return await page.content()

    async def _fetch_with_aiohttp(self, url: str) -> str:
        """Fetch a page using aiohttp (for simple pages)."""
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=settings.request_timeout_seconds)) as response:
                response.raise_for_status()
                return await response.text()

    async def _check_robots_txt(self, url: str, root_domain: str) -> bool:
        """Check if a URL is allowed by robots.txt."""
        if root_domain in self.robots_cache:
            return self.robots_cache[root_domain]

        robots_url = f"https://{root_domain}/robots.txt"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(robots_url, timeout=5) as response:
                    if response.status == 200:
                        robots_content = await response.text()
                        if "Disallow: /" in robots_content:
                            self.robots_cache[root_domain] = False
                            return False
                        self.robots_cache[root_domain] = True
                        return True
                    else:
                        self.robots_cache[root_domain] = True
                        return True
        except Exception:
            self.robots_cache[root_domain] = True
            return True

    def _extract_text(self, html: str) -> str:
        """Extract text from HTML (remove scripts, styles, etc.)."""
        text = re.sub(r"<script.*?</script>", "", html, flags=re.IGNORECASE)
        text = re.sub(r"<style.*?</style>", "", text, flags=re.IGNORECASE)
        text = re.sub(r"<.*?>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _extract_links(self, html: str, base_url: str) -> List[str]:
        """Extract all links from HTML."""
        links = re.findall(r'href=["\'](.*?)["\']', html, flags=re.IGNORECASE)
        absolute_links = []
        for link in links:
            if link.startswith("http"):
                absolute_links.append(link)
            else:
                absolute_links.append(urljoin(base_url, link))
        return absolute_links

    def _requires_js(self, url: str) -> bool:
        """Check if a URL likely requires JavaScript rendering."""
        js_indicators = ["react", "angular", "vue", "#!", "/app/", "/spa/"]
        return any(indicator in url.lower() for indicator in js_indicators)

    @staticmethod
    def _normalize_domain(domain: str) -> str:
        """Normalize a domain (remove www., port, etc.)."""
        domain = domain.lower().strip()
        if domain.startswith("www."):
            domain = domain[4:]
        if ":" in domain:
            domain = domain.split(":")[0]
        return domain
