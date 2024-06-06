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
                                                 order_type=search.OrderVideo.TOTALRANK, page=page,
                                                 debug_param_func=None))

    def search(self, query: str, max_results: int = 10, max_pages: int = 1, *args, **kwargs) -> List[Retrieval]:
        retrival_list: List[Retrieval] = []
        for i in range(max_pages):
            response = self._sync_search(query, page=i + 1)
            for item in response["result"]:
                if len(retrival_list) == max_results:
                    break
                title = item["title"]
                link = item["arcurl"]
                snippet = item["description"]
                retrival_list.append(Retrieval(title=title, link=link, snippet=snippet, source="bilibili_video"))
        return retrival_list
