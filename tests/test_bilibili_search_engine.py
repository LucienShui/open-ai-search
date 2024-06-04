import unittest
from open_ai_search.bilibili_search_engine import BilibiliSearchEngine


class BilibiliSearchEngineTestCase(unittest.TestCase):

    def test_search(self):
        s = BilibiliSearchEngine()
        result = s.search("大模型")
        print(result)
        self.assertGreater(len(result), 0)
