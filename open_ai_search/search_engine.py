import requests
from typing import List, Optional
from open_ai_search.entity import Retrieval
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag


class SearchEngine:
    def search(self, query: str, *args, **kwargs) -> List[Retrieval]:
        raise NotImplementedError


class Bing(SearchEngine):

    def __init__(self, base_url: Optional[str] = None):
        self.base_url: str = base_url or "https://www.bing.com"
        self.headers: dict = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:84.0) Gecko/20100101 Firefox/84.0"
        }

    def search(self, query: str, *args, **kwargs) -> List[Retrieval]:
        url: str = urljoin(self.base_url, 'search')
        response: requests.Response = requests.get(url, params={"q": query}, headers=self.headers, allow_redirects=True)
        response.raise_for_status()
        soup: BeautifulSoup = BeautifulSoup(response.text, 'html.parser')
        retrieval_list: List[Retrieval] = []
        for result in soup.find_all('li', attrs={"class": "b_algo"}):
            result: Tag
            title: str = result.find("h2").text
            link: str = result.find("a", attrs={"class": "tilk"})["href"]
            snippet = ""
            if p := result.find("p"):
                snippet = p.text
            retrieval_list.append(Retrieval(title=title, link=link, snippet=snippet))
        return retrieval_list
