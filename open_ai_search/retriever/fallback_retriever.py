from typing import Optional, List

from open_ai_search.entity import Retrieval
from open_ai_search.retriever import RetrieverBase


class FallbackRetriever(RetrieverBase):

    def __init__(self, retriever_list: List[RetrieverBase], max_results: Optional[int] = None):
        super().__init__(max_results)
        self.retriever_list: List[RetrieverBase] = retriever_list

    def search(self, query: str, max_results: Optional[int] = None, *args, **kwargs) -> List[Retrieval]:
        for retriever in self.retriever_list:
            if retrieval_list := retriever.search(query, max_results or self.max_results):
                return retrieval_list
        return []
