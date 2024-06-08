import unittest
from open_ai_search.search_engine import BingSearchEngine
from concurrent.futures import ThreadPoolExecutor

CN = "https://cn.bing.com"


class BingSearchTestCase(unittest.TestCase):
    def search(self, base_url: str = None):
        b = BingSearchEngine(base_url=base_url)
        result = b.search("魏则西事件")
        self.assertGreater(len(result), 0)

    def test_bing_search(self):
        self.search()

    def test_cn_bing_search(self):
        self.search(base_url=CN)

    def test_parallel_search(self):
        b = BingSearchEngine(base_url=CN)
        pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=1)
        retrieval_list = sum(pool.map(lambda x: x.search("魏则西事件"), [b]), [])
        self.assertGreater(len(retrieval_list), 0)

    def test_max_answer_cnt(self):
        cnt: int = 15
        b = BingSearchEngine(base_url=CN, max_answer_cnt=cnt)
        result = b.search("魏则西事件")
        self.assertEqual(cnt, len(result))
