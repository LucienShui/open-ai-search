import pytest

from open_ai_search.retriever import Bing

GLOBAL = "https://www.bing.com"
CN = "https://cn.bing.com"


@pytest.mark.parametrize("query", ["魏则西事件"])
@pytest.mark.parametrize("cnt", [1, 19])
@pytest.mark.parametrize("base_url", [GLOBAL, CN])
def test_max_result_cnt(base_url: str, query: str, cnt: int):
    b = Bing(base_url=base_url, max_result_cnt=cnt)
    result = b.search(query)
    assert cnt == len(result)
