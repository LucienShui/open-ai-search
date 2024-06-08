import re
from typing import List, Optional, Tuple
from unicodedata import category as ch_cate
from urllib.parse import urljoin, urlencode

import requests
from bs4 import BeautifulSoup, Tag

from open_ai_search.entity import Retrieval
from open_ai_search.search_engine import SearchEngine

spaces: List[str] = [char for code_point in range(0x110000) if ch_cate(char := chr(code_point)) in ['Zs', 'Zl', 'Zp']]


class BingSearchEngine(SearchEngine):
    def __init__(self, base_url: Optional[str] = None, max_answer_cnt: Optional[int] = None):
        self.base_url: str = base_url or "https://www.bing.com"
        self.max_answer_cnt: int = max_answer_cnt or 20
        self.date_sep: str = " · "
        self.session = requests.session()
        self.headers: dict = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:84.0) Gecko/20100101 Firefox/84.0",
            "Accept-Language": "en-US,en;q=0.6",
            "Referer": self.base_url
        }
        self.space_pattern: re.Pattern = re.compile(f"[{''.join(spaces)}]")

    def parse_one_page(self, session: requests.Session, url: str,
                       max_answer_cnt: int) -> Tuple[List[Retrieval], Optional[str]]:
        """
        Parse one page from bing search
        :param session: requests session
        :param url: url to get
        :param max_answer_cnt: max retrieval to return
        :return: List[Retrival], next page url (if exceed max_answer_cnt, return None instead of url)
        """
        retrieval_list: List[Retrieval] = []
        response: requests.Response = session.get(url)
        self.session.headers["Referer"] = url
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
            if len(retrieval_list) >= max_answer_cnt:
                return retrieval_list, None
        url = urljoin(self.base_url, soup.select_one('div#b_content nav[role="navigation"] a.sb_pagN')["href"])
        return retrieval_list, url

    def search(self, query: str, *args, **kwargs) -> List[Retrieval]:
        session: requests.Session = requests.session()
        session.headers.update(self.headers)
        url: str = "?".join([urljoin(self.base_url, 'search'), urlencode({"q": query, "form": "QBLH"})])
        retrieval_list: List[Retrieval] = []
        for page in range((self.max_answer_cnt + 9) // 10):
            page_retrieval_list, url = self.parse_one_page(session, url, self.max_answer_cnt - len(retrieval_list))
            retrieval_list.extend(page_retrieval_list)
            if not url:
                break
        return retrieval_list
