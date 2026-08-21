from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional

# --- Request Models ---
class CrawlRequest(BaseModel):
    url: HttpUrl
    whitelist_domains: str = Field(..., description="Comma-delimited list of allowed domains (e.g., 'nasa.gov,spacex.com').")
    max_depth: int = Field(default=3, ge=1, le=9, description="Maximum crawl depth (1-9).")
    use_token: bool = Field(default=False, description="Use Firefox session token if available.")
    firefox_profile: Optional[str] = Field(default=None, description="Firefox profile name to use for tokens.")

class SearchIndexRequest(BaseModel):
    domain: str = Field(..., description="Domain to search (e.g., 'nasa.gov').")
    regex: str = Field(..., description="Regex pattern to match.")
    max_results: int = Field(default=10, ge=1, description="Maximum number of results to return.")

class DownloadRequest(BaseModel):
    domain: str = Field(..., description="Domain to download from (e.g., 'nasa.gov').")
    regex: str = Field(..., description="Regex pattern for files to download (e.g., '.*\\.pdf$').")
    output_dir: Optional[str] = Field(default=None, description="Custom output directory (default: ./downloads/{domain}).")

class WebSearchRequest(BaseModel):
    query: str = Field(..., description="Search query.")
    search_engine: Optional[str] = Field(default=None, description="Search engine (default: Firefox default).")
    use_token: bool = Field(default=False, description="Use Firefox session token if available.")
    firefox_profile: Optional[str] = Field(default=None, description="Firefox profile name.")

# --- Response Models ---
class CrawlResult(BaseModel):
    excerpt: str
    full_text: str
    url: HttpUrl
    timestamp: str
    domain: str

class SearchIndexResult(BaseModel):
    url: HttpUrl
    excerpt: str
    timestamp: str

class DownloadResult(BaseModel):
    filename: str
    url: HttpUrl
    parsed_text: Optional[str] = None

class WebSearchResult(BaseModel):
    title: str
    url: HttpUrl
    snippet: str

class ErrorResponse(BaseModel):
    error: str
    details: Optional[str] = None
