from open_ai_search.retriever.ddg import DuckDuckGo


async def test_ddg():
    ddg = DuckDuckGo()
    results = await ddg.search("hello world", max_results=30)
    print(results)
