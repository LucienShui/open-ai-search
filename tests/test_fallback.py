from typing import Optional, List
import pytest

from open_ai_search.entity import Retrieval
from open_ai_search.retriever import RetrieverBase, FallbackRetriever, BingScraper


class EmptyRetriever(RetrieverBase):
    def search(self, query: str, max_result_cnt: Optional[int] = None, *args, **kwargs) -> List[Retrieval]:
        return []


@pytest.mark.parametrize("query", ["魏则西事件"])
@pytest.mark.parametrize("cnt", [1, 19])
def test_fallback(query: str, cnt: int):
    engine = FallbackRetriever([EmptyRetriever(), BingScraper()])
    result = engine.search(query, cnt)
    assert len(result) == cnt
