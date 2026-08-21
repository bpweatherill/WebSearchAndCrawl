from pathlib import Path
from typing import List, Dict, Optional
import json
import re
from server.config import settings
from server.schemas import CrawlResult, SearchIndexResult
import logging

logger = logging.getLogger(__name__)

class Indexer:
    def __init__(self):
        self.index_dir = Path(settings.index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def save_result(self, result: CrawlResult) -> None:
        """Save a crawl result to the index for its domain."""
        index_path = self.index_dir / f"{result.domain}.json"
        index = self._load_index(str(index_path))
        # Replace existing entry if URL already exists
        index[result.url] = {
            "excerpt": result.excerpt,
            "full_text": result.full_text,
            "timestamp": result.timestamp
        }
        self._save_index(str(index_path), index)

    def search_index(self, domain: str, regex: str, max_results: int = 10) -> List[SearchIndexResult]:
        """Search the index for a domain using regex."""
        index_path = self.index_dir / f"{domain}.json"
        if not index_path.exists():
            return []

        index = self._load_index(str(index_path))
        results = []
        pattern = re.compile(regex, re.IGNORECASE)

        for url, data in index.items():
            if pattern.search(data["excerpt"]) or pattern.search(data["full_text"]):
                results.append(SearchIndexResult(
                    url=url,
                    excerpt=data["excerpt"],
                    timestamp=data["timestamp"]
                ))
                if len(results) >= max_results:
                    break

        return results

    def list_indexed_domains(self) -> List[str]:
        """List all domains with indexed content."""
        return [f.stem for f in self.index_dir.glob("*.json")]

    def _load_index(self, index_path: str) -> Dict[str, Dict[str, str]]:
        """Load an index file from disk."""
        try:
            with open(index_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def _save_index(self, index_path: str, index: Dict[str, Dict[str, str]]) -> None:
        """Save an index file to disk."""
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
