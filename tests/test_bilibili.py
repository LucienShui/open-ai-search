from open_ai_search.retriever import Bilibili


def test_search():
    s = Bilibili()
    result = s.search("大模型")
    assert len(result) > 0
