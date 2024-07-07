import pytest

from open_ai_search.retriever import BingScraper, BingAPI

GLOBAL = "https://www.bing.com"
CN = "https://cn.bing.com"


@pytest.mark.parametrize("query", ["魏则西事件"])
@pytest.mark.parametrize("cnt", [1, 19])
@pytest.mark.parametrize("base_url", [GLOBAL, CN])
def test_bing_scraper_max_result_cnt(base_url: str, query: str, cnt: int):
    b = BingScraper(base_url=base_url, max_result_cnt=cnt)
    result = b.search(query)
    assert cnt == len(result)


@pytest.mark.parametrize("query", ["魏则西事件"])
@pytest.mark.parametrize("cnt", [1, 19])
def test_bing_api(query: str, cnt: int):
    b = BingAPI()
    result = b.search(query, max_result_cnt=cnt)
    assert cnt == len(result)
