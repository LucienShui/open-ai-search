from datetime import timezone, timedelta
from typing import Optional, List, Dict, Any

import dateutil.parser
import requests

from open_ai_search.config import config
from open_ai_search.entity import Retrieval
from open_ai_search.retriever import RetrieverBase


# https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/reference/query-parameters
class BingAPI(RetrieverBase):

    def __init__(self):
        self.header = {"Ocp-Apim-Subscription-Key": config.bing_api_subscription_key}
        self.params = {
            "mkt": config.bing_api_mkt,
            "textDecorations": True,
            "textFormat": "HTML",
        }

    @staticmethod
    def date_formatter(date: str) -> Optional[str]:
        if date:
            return dateutil.parser.parse(date).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
        return None

    def search(self, query: str, max_result_cnt: Optional[int], *args, **kwargs) -> List[Retrieval]:
        params: Dict[str, Any] = {**self.params, "q": query, "count": max_result_cnt}
        response = requests.get("https://api.bing.microsoft.com/v7.0/search", headers=self.header, params=params)
        response.raise_for_status()
        return [
            Retrieval(
                title=web_page["name"], link=web_page["url"], snippet=web_page["snippet"], source="bing_api",
                date=self.date_formatter(web_page.get("dateLastCrawled", "")), author=web_page.get("siteName", None)
            ) for web_page in response.json()["webPages"]["value"]
        ]
