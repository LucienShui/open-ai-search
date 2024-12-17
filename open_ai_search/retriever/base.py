from typing import List, Optional

from open_ai_search.entity import Retrieval


class BaseRetriever:
    def __init__(self, max_results: Optional[int] = None):
        self.max_results: Optional[int] = max_results or 10

    async def search(self, query: str, max_results: Optional[int] = None, *args, **kwargs) -> List[Retrieval]:
        raise NotImplementedError
