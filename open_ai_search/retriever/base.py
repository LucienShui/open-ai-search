import requests
from open_ai_search.entity import Retrieval
from typing import List, Tuple, Optional


class RetrieverBase:
    def search(self, query: str, max_result_cnt: Optional[int], *args, **kwargs) -> List[Retrieval]:
        raise NotImplementedError


class SearchEngineScraperBase(RetrieverBase):
    result_count_per_page: int = 10
    headers: dict = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; rv:84.0) Gecko/20100101 Firefox/84.0",
        "Accept-Language": "en-US,en;q=0.6",
    }

    def __init__(self, max_result_cnt: Optional[int] = None):
        self.max_result_cnt: int = max_result_cnt or 10

    def generate_url(self, query: str) -> str:
        raise NotImplementedError

    def parse_one_page(self, session: requests.Session, url: str,
                       max_result_cnt: int) -> Tuple[List[Retrieval], Optional[str]]:
        """
        Parse one page from bing search
        :param session: requests session
        :param url: url to get
        :param max_result_cnt: max retrieval to return
        :return: List[Retrival], next page url (if exceed max_answer_cnt, return None instead of url)
        """
        raise NotImplementedError

    def search(self, query: str, max_result_cnt: Optional[int] = None, *args, **kwargs) -> List[Retrieval]:
        try:
            max_result_cnt: int = max_result_cnt or self.max_result_cnt
            session: requests.Session = requests.session()
            session.headers.update(self.headers)
            url: str = self.generate_url(query)
            retrieval_list: List[Retrieval] = []

            # 向上取整，然后多取一页
            for page in range((max_result_cnt + self.result_count_per_page - 1) // self.result_count_per_page + 1):
                page_retrieval_list, url = self.parse_one_page(session, url, max_result_cnt - len(retrieval_list))
                retrieval_list.extend(page_retrieval_list)
                if not url:
                    break
            return retrieval_list
        except Exception as e:
            return []
