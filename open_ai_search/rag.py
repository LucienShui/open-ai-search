import asyncio
import os
import re
from typing import List, Dict, Union, Any, AsyncIterable

from openai import AsyncOpenAI

from open_ai_search.common.async_parallel_iterator import AsyncParallelIterator
from open_ai_search.common.trace_info import TraceInfo
from open_ai_search.config import OpenAIConfig
from open_ai_search.entity import Retrieval
from open_ai_search.retriever.base import RetrieverBase


class RAG:

    def __init__(self, search_engine_list: List[RetrieverBase], config: OpenAIConfig):
        self.retriever_list: List[RetrieverBase] = search_engine_list

        self.client = AsyncOpenAI(base_url=config.base_url, api_key=config.api_key)
        self.model = config.model

        prompt_base_dir = "resource/prompt"
        self.prompt_filename: Dict[str, str] = {
            "qa": "qa.txt",
            "summary": "summary.txt",
            "entity": "entity.txt",
            "related_question": "related_question.txt"
        }
        self.prompt_dict: Dict[str, Dict[str, str]] = {}
        for lang in ["en", "zh"]:
            for key, filename in self.prompt_filename.items():
                with open(os.path.join(prompt_base_dir, lang, filename)) as f:
                    self.prompt_dict.setdefault(lang, {})[key] = f.read()

        self.zh_pattern: re.Pattern = re.compile(r"[\u4e00-\u9fa5]")

    def lang_detector(self, text: str) -> str:
        if self.zh_pattern.search(text):
            return "zh"
        return "en"

    @classmethod
    def build_context(cls, retrieval_list: List[Retrieval]) -> str:
        retrival_prompt_list: List[str] = [
            "\n".join([f"[[{i + 1}]]", retrieval.to_prompt()])
            for i, retrieval in enumerate(retrieval_list)
        ]
        return "\n\n".join(retrival_prompt_list)

    def messages_prepare(self, query: str, template: str, retrieval_list: List[Retrieval]) -> List[dict]:
        context = self.build_context(retrieval_list)
        messages = [
            {"role": "system", "content": template.format_map({"context": context})},
            {"role": "user", "content": query}
        ]
        return messages

    async def search(self, query: str, max_results: int, trace_info: TraceInfo) -> AsyncIterable[Dict[str, Union[str, Dict]]]:
        try:
            retrieval_list: List[Retrieval] = sum(await asyncio.gather(*(
                retriever.search(query, max_results)
                for retriever in self.retriever_list
            )), [])
            trace_info.info({"retrieval_cnt": len(retrieval_list)})
            assert len(retrieval_list) > 0, "Empty retrieval result"

            citations: List[Dict[str, Any]] = [{
                "i": i + 1, **r.model_dump(exclude={"snippet", "content"})
            } for i, r in enumerate(retrieval_list)]
            yield {"block": "citation", "data": citations}

            lang: str = self.lang_detector(query)

            async_iter = AsyncParallelIterator({
                key: await self.client.chat.completions.create(
                    model=self.model, messages=self.messages_prepare(query, prompt, retrieval_list), stream=True
                ) for key, prompt in self.prompt_dict[lang].items()
            })

            async for name, response in async_iter:
                if delta := response.choices[0].delta.content:
                    yield {"block": name, "delta": delta}
        except Exception as e:
            yield {"error": str(e)}
