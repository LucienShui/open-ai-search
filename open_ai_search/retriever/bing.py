import re
from typing import List, Optional, Tuple
from unicodedata import category as ch_cate
from urllib.parse import urljoin, urlencode

import requests
from bs4 import BeautifulSoup, Tag

from open_ai_search.entity import Retrieval
from open_ai_search.retriever import SearchEngineScraperBase

spaces: List[str] = [char for code_point in range(0x110000) if ch_cate(char := chr(code_point)) in ['Zs', 'Zl', 'Zp']]


class Bing(SearchEngineScraperBase):
    def __init__(self, base_url: Optional[str] = None, max_result_cnt: Optional[int] = None):
        super().__init__(max_result_cnt)
        self.base_url: str = base_url or "https://www.bing.com"
        self.date_sep: str = " · "
        self.space_pattern: re.Pattern = re.compile(f"[{''.join(spaces)}]")

    def parse_one_page(self, session: requests.Session, url: str,
                       max_result_cnt: int) -> Tuple[List[Retrieval], Optional[str]]:
        retrieval_list: List[Retrieval] = []
        response: requests.Response = session.get(url)
        session.headers["Referer"] = url
        response.raise_for_status()
        soup: BeautifulSoup = BeautifulSoup(response.text, 'html.parser')
        result_list: List[Tag] = soup.find_all('li', attrs={"class": "b_algo"})
        assert len(result_list) > 0, "No search result, maybe there is something wrong with bing."
        for result in result_list:
            retrieval_dict = {
                "title": result.find("h2").text,
                "link": result.find("a", attrs={"class": "tilk"})["href"]
            }
            if p := result.find("p"):
                [each.decompose() for each in p.find_all("span", attrs={"class": "algoSlug_icon"})]
                snippet = self.space_pattern.sub(' ', p.text.strip())
                if self.date_sep in snippet:
                    date = snippet.split(self.date_sep)[0].strip()
                    retrieval_dict["snippet"] = snippet.lstrip(date).strip()
                    retrieval_dict["date"] = date
                else:
                    retrieval_dict["snippet"] = snippet.strip()
                retrieval_dict["source"] = "bing"
                retrieval_list.append(Retrieval.model_validate(retrieval_dict))
            if len(retrieval_list) >= max_result_cnt:
                return retrieval_list, None
        url = urljoin(self.base_url, soup.select_one('div#b_content nav[role="navigation"] a.sb_pagN')["href"])
        return retrieval_list, url

    def generate_url(self, query: str) -> str:
        url: str = "?".join([urljoin(self.base_url, 'search'), urlencode({"q": query, "form": "QBLH"})])
        return url
