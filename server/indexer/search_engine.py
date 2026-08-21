from typing import List
from server.indexer.indexer import Indexer
from server.schemas import SearchIndexRequest, SearchIndexResult

class SearchEngine:
    def __init__(self, indexer: Indexer):
        self.indexer = indexer

    def search(self, request: SearchIndexRequest) -> List[SearchIndexResult]:
        """Search the index for a domain using regex."""
        return self.indexer.search_index(
            domain=request.domain,
            regex=request.regex,
            max_results=request.max_results
        )
