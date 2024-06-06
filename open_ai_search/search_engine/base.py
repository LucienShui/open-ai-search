from open_ai_search.entity import Retrieval
from typing import List


class SearchEngine:
    def search(self, query: str, *args, **kwargs) -> List[Retrieval]:
        raise NotImplementedError
