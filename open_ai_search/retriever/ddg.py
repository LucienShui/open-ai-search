from typing import Optional, List, Dict

from duckduckgo_search import AsyncDDGS

from open_ai_search.entity import Retrieval
from open_ai_search.retriever.base import RetrieverBase

class DuckDuckGo(RetrieverBase):
    def __init__(self, max_results: Optional[int] = None):
        super().__init__(max_results)
        self.max_results: Optional[int] = max_results or 10
        self.ddg = AsyncDDGS()

    async def search(self, query: str, max_results: Optional[int] = None, *args, **kwargs) -> List[Retrieval]:
        results: List[Dict[str, str]] = await self.ddg.atext(query, max_results=max_results)
        retrievals: List[Retrieval] = [
            Retrieval(
                title=result["title"],
                link=result["href"],
                snippet=result["body"],
                source="ddg"
            ) for result in results
        ]
        return retrievals