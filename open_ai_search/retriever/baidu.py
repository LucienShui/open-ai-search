from typing import List, Tuple, Optional
from urllib.parse import urlparse, urljoin, urlencode, quote, parse_qs, ParseResult, urlunparse
import re

import requests
from bs4 import BeautifulSoup, Tag

from open_ai_search.entity import Retrieval
from .base import SearchEngineScraperBase


class Baidu(SearchEngineScraperBase):
    snippet_pattern = re.compile(r'^content-right_')

    def __init__(self):
        super().__init__()
        self.base_url = "http://www.baidu.com"

    def generate_url(self, query: str) -> str:
        url: str = "?".join([urljoin(self.base_url, "s"), urlencode({'wd': query})])
        return url

    def parse_one_page(self, session: requests.Session, url: str,
                       max_result_cnt: int) -> Tuple[List[Retrieval], Optional[str]]:
        retrieval_list: List[Retrieval] = []
        response: requests.Response = session.get(url)
        session.headers["Referer"] = url

        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        for result in soup.find_all("div", attrs={"class": "result"}):
            a: Tag = result.find("a")
            title: str = a.get_text()
            encrypt_link: str = a.get("href")
            encrypt_link_headers = dict(requests.head(encrypt_link).headers.items())
            if not (link := encrypt_link_headers.get("Location", None)):
                continue
            snippet: str = result.find("span", attrs={"class", self.snippet_pattern}).get_text().strip()
            retrieval: Retrieval = Retrieval(title=title, link=link, snippet=snippet, source="baidu")
            if dom := result.find("span", attrs={"class": "c-color-gray2"}):
                retrieval.date = dom.get_text().strip()
            if dom := result.find("div", attrs={"class": "c-img-s"}):
                retrieval.icon_url = dom.find("img").get("src").strip()
            if dom := result.find("span", attrs={"class": "c-color-gray"}):
                retrieval.author = dom.get_text().strip()
            retrieval_list.append(retrieval)
            if len(retrieval_list) == max_result_cnt:
                return retrieval_list, None

        # Standardization
        next_page_url = urljoin(self.base_url, soup.find("a", attrs={"class": "n"}).get("href"))
        parsed_url: ParseResult = urlparse(next_page_url)
        params_dict: dict = parse_qs(parsed_url.query)
        modified_parsed_url = parsed_url._replace(query=urlencode(params_dict))
        modified_next_page_url: str = urlunparse(modified_parsed_url)

        return retrieval_list, modified_next_page_url
