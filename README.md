# WebSearchAndCrawl

**An MCP Server for Authenticated Web Crawling, Searching, and Document Processing**

---.

## **🚀 Purpose**

`WebSearchAndCrawl` is an **MCP (Model Context Protocol) server** designed to:

1. **Crawl websites** (including authenticated ones) using **Firefox session tokens** or browser automation.
2. **Search crawled content** for regex matches and store results in a structured index.
3. **Download and parse documents** (PDF, DOCX, XLSX, etc.) from crawled sites.
4. **Stream results in real-time** via HTTP for integration with MCP clients.
5. **Respect `robots.txt`** and enforce **rate limits** (5 requests/sec, 5 threads max).

This tool is ideal for:
- **Researchers** who need to scrape authenticated or dynamic websites.
- **Developers** building AI agents that require web data.
- **Automation** of repetitive web tasks (e.g., monitoring, data extraction).

---

## **🔧 Features**

| Feature | Description |
|---------|-------------|
| **Authenticated Crawling** | Uses Firefox session tokens to access logged-in pages. |
| **Browser Automation** | Falls back to Playwright for dynamic content or login forms. |
| **Domain Whitelisting** | Only crawls URLs matching a comma-delimited list of domains. |
| **Depth-limited Crawling** | Configurable crawl depth (1-9 layers). |
| **Regex Search** | Search crawled content or index for regex patterns. |
| **Document Parsing** | Extracts text from PDF, DOCX, XLSX, and TXT files. |
| **Real-time Streaming** | Results are streamed as JSONL (chunked by page). |
| **Indexing** | Stores results in JSON files per domain for later search. |
| **Rate Limiting** | Enforces 5 requests/sec and 5 threads max. |
| **Resume Support** | Can resume interrupted crawls from checkpoints. |
| **Session Validation** | Validates token scopes to prevent misuse. |

---

## **📦 Installation**

### **Prerequisites**
1. **Python 3.9+** (recommended: 3.11+).
2. **Firefox** (required for browser automation).
3. **System Libraries** (for document parsing):
   - **PDF**: `poppler-utils` (Linux) or `pdfminer.six` (cross-platform).
   - **DOCX/XLSX**: `python-docx`, `openpyxl`.

### **Steps**

#### 1. Clone the Repository
```bash
git clone https://github.com/bpweatherill/WebSearchAndCrawl.git
cd WebSearchAndCrawl
```

#### 2. Set Up a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate   # Windows
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Install Playwright Browsers
```bash
playwright install firefox
```

#### 5. (Optional) Configure Environment Variables
Create a `.env` file in the project root:
```ini
# Server
MCP_PORT=8808
MCP_HOST=0.0.0.0

# Crawler
MAX_DEPTH=9
MAX_THREADS=5
RATE_LIMIT=5
REQUEST_TIMEOUT=10
MAX_MEMORY_MB=1024

# Firefox
FIREFOX_PROFILE=my_profile  # Optional: Specific Firefox profile
DEFAULT_SEARCH_ENGINE=google

# Directories
INDEX_DIR=./index
DOWNLOADS_DIR=./downloads
CHECKPOINTS_DIR=./checkpoints
```

---

## **🏃 Usage**

### **1. Start the MCP Server**
```bash
python -m server.main
```
The server will start on `http://localhost:8808` (or the port specified in `.env`).

### **2. MCP Tools (HTTP Endpoints)**

All tools return **JSON responses** and support **streaming** for real-time results.

| Endpoint | Method | Description | Request Body |
|----------|--------|-------------|---------------|
| `/crawl_website` | POST | Crawl a website and stream results. | [CrawlRequest](#crawlrequest) |
| `/search_index` | POST | Search the local index for regex matches. | [SearchIndexRequest](#searchindexrequest) |
| `/download_documents` | POST | Download documents matching a regex. | [DownloadRequest](#downloadrequest) |
| `/get_search_results` | POST | Use Firefox's search engine to fetch results. | [WebSearchRequest](#websearchrequest) |
| `/list_indexed_domains` | GET | List all domains with indexed content. | - |
| `/health` | GET | Health check. | - |

---

#### **Request/Response Schemas**

##### **CrawlRequest**
```json
{
  "url": "https://www.nasa.gov",
  "whitelist_domains": "nasa.gov",
  "max_depth": 3,
  "use_token": false,
  "firefox_profile": "my_profile"
}
```
- `url`: Starting URL for the crawl.
- `whitelist_domains`: Comma-delimited list of allowed domains (e.g., `"nasa.gov,spacex.com"`).
- `max_depth`: Maximum crawl depth (1-9).
- `use_token`: Use Firefox session token if available.
- `firefox_profile`: Firefox profile name (optional).

**Streamed Response (JSONL)**:
```json
{
  "excerpt": "NASA's Perseverance Rover lands on Mars...",
  "full_text": "Full article text here...",
  "url": "https://www.nasa.gov/mars2020",
  "timestamp": "2024-05-20T12:00:00Z",
  "domain": "nasa.gov"
}
```

---.

##### **SearchIndexRequest**
```json
{
  "domain": "nasa.gov",
  "regex": ".*Mars.*",
  "max_results": 10
}
```
- `domain`: Domain to search (e.g., `"nasa.gov"`).
- `regex`: Regex pattern to match.
- `max_results`: Maximum number of results to return.

**Response**:
```json
[
  {
    "url": "https://www.nasa.gov/mars2020",
    "excerpt": "NASA's Perseverance Rover lands on Mars...",
    "timestamp": "2024-05-20T12:00:00Z"
  }
]
```

---.

##### **DownloadRequest**
```json
{
  "domain": "nasa.gov",
  "regex": ".*\\.pdf$",
  "output_dir": "./downloads/nasa.gov"
}
```
- `domain`: Domain to download from.
- `regex`: Regex pattern for files to download (e.g., `"*.pdf"`).
- `output_dir`: Custom output directory (optional).

**Streamed Response (JSONL)**:
```json
{
  "filename": "./downloads/nasa.gov/mars_rover.pdf",
  "url": "https://www.nasa.gov/pdf/mars_rover.pdf",
  "parsed_text": "Extracted text from PDF..."
}
```

---.

##### **WebSearchRequest**
```json
{
  "query": "NASA Mars missions",
  "search_engine": "google",
  "use_token": false,
  "firefox_profile": "my_profile"
}
```
- `query`: Search query.
- `search_engine`: Search engine (default: Firefox default).
- `use_token`: Use Firefox session token if available.
- `firefox_profile`: Firefox profile name (optional).

**Streamed Response (JSONL)**:
```json
{
  "title": "Mars 2020 Mission - NASA",
  "url": "https://www.nasa.gov/mars2020",
  "snippet": "Learn about the Perseverance Rover..."
}
```

---

## **🔍 Examples**

### **1. Crawl NASA.gov and Index Results**
```bash
curl -X POST http://localhost:8808/crawl_website \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.nasa.gov",
    "whitelist_domains": "nasa.gov",
    "max_depth": 2,
    "use_token": false
  }'
```

### **2. Search Indexed Content for "Mars"**
```bash
curl -X POST http://localhost:8808/search_index \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "nasa.gov",
    "regex": ".*Mars.*",
    "max_results": 5
  }'
```

### **3. Download PDFs from NASA.gov**
```bash
curl -X POST http://localhost:8808/download_documents \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "nasa.gov",
    "regex": ".*\\.pdf$"
  }'
```

### **4. Use Firefox to Search Google**
```bash
curl -X POST http://localhost:8808/get_search_results \
  -H "Content-Type: application/json" \
  -d '{
    "query": "NASA Mars missions",
    "search_engine": "google"
  }'
```

---

## **📁 Project Structure**
```
WebSearchAndCrawl/
│
├── server/                          # Core server logic
│   ├── __init__.py
│   ├── main.py                       # FastAPI app + MCP tools
│   ├── config.py                     # Configuration settings
│   ├── schemas.py                    # Pydantic request/response models
│   │
│   ├── firefox/                      # Firefox browser automation
│   │   ├── __init__.py
│   │   ├── controller.py              # Playwright Firefox management
│   │   └── token_manager.py           # Session token handling
│   │
│   ├── crawler/                     # Web crawling logic
│   │   ├── __init__.py
│   │   ├── crawler.py                # Main crawling logic
│   │   └── rate_limiter.py            # Thread/rate limiting
│   │
│   ├── indexer/                     # Indexing and search
│   │   ├── __init__.py
│   │   ├── indexer.py                 # JSON index management
│   │   └── search_engine.py           # Regex search
│   │
│   ├── downloader/                  # Document downloading and parsing
│   │   ├── __init__.py
│   │   ├── downloader.py              # Download logic
│   │   └── parsers/                  # File type parsers
│   │       ├── __init__.py
│   │       ├── pdf_parser.py
│   │       ├── docx_parser.py
│   │       └── xlsx_parser.py
│   │
│   └── streamer.py                   # Chunked JSON streaming
│
├── tests/                           # Unit and integration tests
│   ├── __init__.py
│   ├── test_firefox.py
│   └── test_crawler.py
│
├── index/                           # Index files (auto-generated)
│   ├── nasa.gov.json
│   └── ...
│
├── downloads/                       # Downloaded documents (auto-generated)
│   ├── nasa.gov/
│   │   ├── document1.pdf
│   │   └── ...
│   └── ...
│
├── checkpoints/                     # Crawl checkpoints (auto-generated)
│   └── ...
│
├── requirements.txt                 # Python dependencies
├── .env.example                     # Example environment variables
└── README.md                        # This file
```

---

## **⚙️ Configuration**

### **Environment Variables**
| Variable | Default | Description |
|----------|---------|-------------|
| `MCP_PORT` | `8808` | HTTP server port. |
| `MCP_HOST` | `0.0.0.0` | HTTP server host. |
| `MAX_DEPTH` | `9` | Maximum crawl depth (1-9). |
| `MAX_THREADS` | `5` | Maximum concurrent threads. |
| `RATE_LIMIT` | `5` | Maximum requests per second. |
| `REQUEST_TIMEOUT` | `10` | Timeout for requests (seconds). |
| `MAX_MEMORY_MB` | `1024` | Maximum memory usage (MB). |
| `FIREFOX_PROFILE` | `None` | Firefox profile name (optional). |
| `DEFAULT_SEARCH_ENGINE` | `google` | Default search engine. |
| `INDEX_DIR` | `./index` | Directory for index files. |
| `DOWNLOADS_DIR` | `./downloads` | Directory for downloaded files. |
| `CHECKPOINTS_DIR` | `./checkpoints` | Directory for crawl checkpoints. |

---

## **🛡️ Security Considerations**

1. **Session Tokens**:
   - Tokens are **only stored in memory** (not persisted to disk).
   - Token scopes are **validated** to prevent misuse (e.g., a token for `nasa.gov` cannot be used for `evil.com`).

2. **Input Sanitization**:
   - All inputs (URLs, regex, etc.) are **sanitized** to prevent injection attacks.

3. **Rate Limiting**:
   - Enforces **5 requests/sec** and **5 threads max** to avoid overwhelming servers.

4. **`robots.txt` Compliance**:
   - The crawler **respects `robots.txt`** and skips disallowed URLs.

5. **Whitelisting**:
   - Only URLs matching the **whitelisted domains** are crawled.

---

## **🚀 Enhancements (Roadmap)**

| Enhancement | Description | Priority |
|--------------|-------------|----------|
| **Persistent Tokens** | Store tokens in an encrypted file for persistence across restarts. | Medium |
| **Full `robots.txt` Parsing** | Properly parse `robots.txt` rules instead of simple checks. | Medium |
| **Advanced Pagination Handling** | Detect and follow pagination links (e.g., "Next" buttons). | High |
| **Lazy-Loading Support** | Detect and trigger lazy-loaded content (e.g., infinite scroll). | High |
| **Checkpointing** | Save crawl state to resume interrupted crawls. | High |
| **Full-Text Search** | Support full-text search in addition to regex. | Low |
| **Database Backend** | Replace JSON files with SQLite/PostgreSQL for scalability. | Low |
| **Distributed Crawling** | Support horizontal scaling with multiple workers. | Low |
| **Docker Support** | Add a `Dockerfile` for containerized deployment. | Medium |
| **Authentication Helpers** | Built-in support for common auth methods (OAuth, SAML). | Medium |
| **Proxy Support** | Add proxy support for crawling behind firewalls. | Low |
| **Custom Headers** | Allow users to specify custom headers for requests. | Medium |
| **Webhook Notifications** | Notify a webhook URL when new results are found. | Low |

---

## **🤝 Contributing**

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a Pull Request.

---

## **📜 License**

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## **📞 Support**

- **Issues**: Report bugs or request features in the [GitHub Issues](https://github.com/bpweatherill/WebSearchAndCrawl/issues) tab.
- **Discussions**: Join the [GitHub Discussions](https://github.com/bpweatherill/WebSearchAndCrawl/discussions) for Q&A.

---

## **🏆 Acknowledgments**

- **Playwright**: For browser automation.
- **FastAPI**: For the HTTP server.
- **pdfminer.six**: For PDF parsing.
- **python-docx/openpyxl**: For Office file parsing.
