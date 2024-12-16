import pytest

from open_ai_search.retriever import BingScraper, BingAPI

GLOBAL = "https://www.bing.com"
CN = "https://cn.bing.com"


@pytest.mark.parametrize("query", ["魏则西事件"])
@pytest.mark.parametrize("cnt", [1, 19])
@pytest.mark.parametrize("base_url", [GLOBAL, CN])
def test_bing_scraper_max_results(base_url: str, query: str, cnt: int):
    b = BingScraper(base_url=base_url, max_results=cnt)
    result = b.search(query)
    assert cnt == len(result)


@pytest.mark.parametrize("query", ["魏则西事件"])
@pytest.mark.parametrize("cnt", [1, 19])
def test_bing_api(query: str, cnt: int):
    b = BingAPI()
    result = b.search(query, max_results=cnt)
    assert cnt == len(result)
