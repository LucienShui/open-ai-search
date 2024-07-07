from typing import Optional, List

from open_ai_search.entity import Retrieval
from open_ai_search.retriever import RetrieverBase


class FallbackRetriever(RetrieverBase):

    def __init__(self, retriever_list: List[RetrieverBase]):
        self.retriever_list: List[RetrieverBase] = retriever_list

    def search(self, query: str, max_result_cnt: Optional[int], *args, **kwargs) -> List[Retrieval]:
        for retriever in self.retriever_list:
            if retrieval_list := retriever.search(query, max_result_cnt):
                return retrieval_list
        return []
