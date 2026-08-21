from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from server.schemas import (
    CrawlRequest, SearchIndexRequest, DownloadRequest, WebSearchRequest,
    CrawlResult, SearchIndexResult, DownloadResult, WebSearchResult, ErrorResponse
)
from server.config import settings
from server.firefox.controller import FirefoxController
from server.firefox.token_manager import TokenManager
from server.crawler.crawler import Crawler
from server.crawler.rate_limiter import RateLimiter
from server.indexer.indexer import Indexer
from server.indexer.search_engine import SearchEngine
from server.downloader.downloader import Downloader
import json
import asyncio
from typing import AsyncGenerator, List
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
firefox_controller = FirefoxController()
token_manager = TokenManager()
rate_limiter = RateLimiter()
indexer = Indexer()
search_engine = SearchEngine(indexer)
downloader = Downloader()
crawler = Crawler(firefox_controller, token_manager, rate_limiter)

app = FastAPI(title="MCP Web Crawler Server")

# --- MCP Tools ---
@app.post("/crawl_website")
async def crawl_website(request: CrawlRequest):
    """
    Crawl a website (authenticated or not) and stream results in chunked JSON.
    Respects `robots.txt`, whitelisted domains, and rate limits.
    """
    try:
        # Normalize whitelist domains
        whitelist_domains = [d.strip() for d in request.whitelist_domains.split(",") if d.strip()]
        if not whitelist_domains:
            raise HTTPException(status_code=400, detail="At least one whitelisted domain is required.")

        # Start Firefox if needed
        if request.use_token or any(
            d for d in whitelist_domains
            if any(ext in d for ext in [".gov", ".com", ".org"])  # Simple heuristic for auth-needed domains
        ):
            await firefox_controller.start()

        # Stream crawl results
        async def generate():
            async for result in crawler.crawl(
                start_url=str(request.url),
                whitelist_domains=whitelist_domains,
                max_depth=request.max_depth,
                use_token=request.use_token,
                firefox_profile=request.firefox_profile
            ):
                # Save to index
                indexer.save_result(result)
                # Stream result
                yield json.dumps(result.dict()) + "\n"
                await asyncio.sleep(0.1)  # Simulate real-time

        return StreamingResponse(generate(), media_type="application/x-ndjson")

    except Exception as e:
        logger.error(f"Crawl failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search_index")
async def search_index(request: SearchIndexRequest):
    """
    Search the local index for regex matches in a specific domain.
    """
    try:
        results = search_engine.search(request)
        return results
    except Exception as e:
        logger.error(f"Index search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download_documents")
async def download_documents(request: DownloadRequest):
    """
    Download documents matching a regex from a crawled site.
    Streams results as JSONL (one result per line).
    """
    try:
        async def generate():
            async for result in downloader.download(
                domain=request.domain,
                regex=request.regex,
                output_dir=request.output_dir
            ):
                yield json.dumps(result.dict()) + "\n"
                await asyncio.sleep(0.1)

        return StreamingResponse(generate(), media_type="application/x-ndjson")

    except Exception as e:
        logger.error(f"Download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/get_search_results")
async def get_search_results(request: WebSearchRequest):
    """
    Use Firefox's search engine to fetch results for a query.
    Streams results as JSONL.
    """
    try:
        # Start Firefox
        await firefox_controller.start()
        page = await firefox_controller.get_page(request.firefox_profile)

        # Navigate to search engine
        search_engine_url = self._get_search_engine_url(request.search_engine)
        await firefox_controller.navigate(search_engine_url)

        # Perform search (placeholder)
        async def generate():
            # TODO: Implement actual search logic
            yield json.dumps(WebSearchResult(
                title="Mock Search Result",
                url="https://www.nasa.gov",
                snippet="Mock snippet for NASA."
            ).dict()) + "\n"

        return StreamingResponse(generate(), media_type="application/x-ndjson")

    except Exception as e:
        logger.error(f"Web search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def _get_search_engine_url(engine: Optional[str]) -> str:
        """Get the URL for a search engine."""
        if engine is None:
            return "https://www.google.com"  # Default
        search_engines = {
            "google": "https://www.google.com",
            "bing": "https://www.bing.com",
            "duckduckgo": "https://duckduckgo.com"
        }
        return search_engines.get(engine, "https://www.google.com")

@app.get("/list_indexed_domains")
async def list_indexed_domains():
    """
    List all domains with indexed content.
    """
    try:
        return indexer.list_indexed_domains()
    except Exception as e:
        logger.error(f"Failed to list indexed domains: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Health Check ---
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
