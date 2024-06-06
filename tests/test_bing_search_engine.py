import unittest
from open_ai_search.search_engine import BingSearchEngine


class BingSearchTestCase(unittest.TestCase):
    def search(self, base_url: str = None):
        b = BingSearchEngine(base_url=base_url)
        result = b.search("周杰伦最近有哪几场演唱会？")
        self.assertGreater(len(result), 0)

    def test_bing_search(self):
        self.search()

    def test_cn_bing_search(self):
        self.search(base_url="https://cn.bing.com")
