from typing import Optional, List, Dict

from duckduckgo_search import DDGS

from open_ai_search.entity import Retrieval
from open_ai_search.retriever.base import BaseRetriever

class DuckDuckGo(BaseRetriever):
    def __init__(self, max_results: Optional[int] = None):
        super().__init__(max_results)
        self.max_results: Optional[int] = max_results or 10
        self.ddg = DDGS()

    async def search(self, query: str, max_results: Optional[int] = None, *args, **kwargs) -> List[Retrieval]:
        results: List[Dict[str, str]] = self.ddg.text(query, max_results=max_results or self.max_results)
        retrievals: List[Retrieval] = [
            Retrieval(
                title=result["title"],
                link=result["href"],
                snippet=result["body"],
                source="ddg"
            ) for result in results
        ]
        return retrievals