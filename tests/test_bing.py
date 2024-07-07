import pytest

from open_ai_search.retriever import Bing

GLOBAL = "http://www.bing.com"
CN = "http://cn.bing.com"


@pytest.mark.parametrize("query", ["魏则西事件"])
@pytest.mark.parametrize("cnt", [1, 19])
@pytest.mark.parametrize("base_url", [GLOBAL, CN])
def test_max_answer_cnt(base_url: str, query: str, cnt: int):
    b = Bing(base_url=base_url, max_result_cnt=cnt)
    result = b.search(query)
    assert cnt == len(result)
