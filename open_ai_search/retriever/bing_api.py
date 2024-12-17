import re
from datetime import timezone, timedelta
from typing import Optional, List, Dict, Any

import dateutil.parser
import requests

from open_ai_search.entity import Retrieval
from open_ai_search.retriever.base import BaseRetriever


# https://learn.microsoft.com/en-us/bing/search-apis/bing-web-search/reference/query-parameters
class BingAPI(BaseRetriever):

    def __init__(
            self,
            bing_api_mkt: str,
            bing_api_subscription_key: str,
            max_results: Optional[int] = None
    ):
        super().__init__(max_results)
        self.header = {"Ocp-Apim-Subscription-Key": bing_api_subscription_key}
        self.params = {
            "mkt": bing_api_mkt,
            "textDecorations": True,
            "textFormat": "HTML",
        }
        self.bold_pattern: re.Pattern = re.compile(r'</?b>')

    @staticmethod
    def date_formatter(date: str) -> Optional[str]:
        if date:
            return dateutil.parser.parse(date).astimezone(timezone(timedelta(hours=8))).strftime("%Y-%m-%d")
        return None

    def search(self, query: str, max_results: Optional[int] = None, *args, **kwargs) -> List[Retrieval]:
        params: Dict[str, Any] = {**self.params, "q": query, "count": max_results or self.max_results}
        response = requests.get("https://api.bing.microsoft.com/v7.0/search", headers=self.header, params=params)
        response.raise_for_status()
        return [
            Retrieval(
                title=self.bold_pattern.sub('', web_page["name"]), link=web_page["url"], snippet=web_page["snippet"],
                source="bing_api", date=self.date_formatter(web_page.get("dateLastCrawled", "")),
                author=web_page.get("siteName", None)) for web_page in response.json()["webPages"]["value"]
        ]
