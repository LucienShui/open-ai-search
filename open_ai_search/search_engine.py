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
        self.date_sep: str = " · "

    @classmethod
    def _prettify(cls, text: str) -> str:
        return text.replace('\xa0', ' ')

    def search(self, query: str, *args, **kwargs) -> List[Retrieval]:
        url: str = urljoin(self.base_url, 'search')
        response: requests.Response = requests.get(url, params={"q": query}, headers=self.headers)
        response.raise_for_status()
        soup: BeautifulSoup = BeautifulSoup(response.text, 'html.parser')
        retrieval_list: List[Retrieval] = []
        for result in soup.find_all('li', attrs={"class": "b_algo"}):
            result: Tag
            retrieval_dict = {
                "title": result.find("h2").text,
                "link": result.find("a", attrs={"class": "tilk"})["href"]
            }
            if p := result.find("p"):
                [each.decompose() for each in p.find_all("span", attrs={"class": "algoSlug_icon"})]
                snippet = p.text.strip().replace('\xa0', ' ')
                if self.date_sep in snippet:
                    date = snippet.split(self.date_sep)[0].strip()
                    retrieval_dict["snippet"] = snippet.lstrip(date).strip()
                    retrieval_dict["date"] = date
                else:
                    retrieval_dict["snippet"] = snippet.strip()

            retrieval_list.append(Retrieval.model_validate(retrieval_dict))
        return retrieval_list
