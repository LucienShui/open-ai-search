from open_ai_search.retriever import Baidu
import pytest


@pytest.mark.parametrize("query", ["魏则西事件", "How to access Baidu?"])
@pytest.mark.parametrize("cnt", [1, 19])
def test_baidu(query: str, cnt: int):
    engine = Baidu()
    result = engine.search(query, cnt)
    assert len(result) == cnt
