from bilibili_api import search
import asyncio

from typing import List
from open_ai_search.entity import Retrieval
from open_ai_search.search_engine import SearchEngine


class BilibiliSearchEngine(SearchEngine):
    def __init__(self):
        super().__init__()

    @staticmethod
    def _sync_search(keyword, page=1):
        return asyncio.run(search.search_by_type(keyword, search_type=search.SearchObjectType.VIDEO,
                                                 video_zone_type=None,
                                                 order_type=search.OrderVideo.PUBDATE, page=page,
                                                 debug_param_func=print))

    def search(self, query: str, *args, **kwargs) -> List[Retrieval]:
        page_num = 1
        items = []
        for i in range(page_num):
            resp = self._sync_search(query, page=i + 1)
            items.extend(resp["result"])

        retrival_list: List[Retrieval] = []
        for item in items:
            title = item["title"]
            link = item["arcurl"]
            snippet = item["description"]
            retrival_list.append(Retrieval(title=title, link=link, snippet=snippet))
        return retrival_list
