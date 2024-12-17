import asyncio
import json
import os
import re
from datetime import datetime
from typing import List, Dict, Union, Any, AsyncIterable

from openai import AsyncOpenAI

from open_ai_search.common import project_root
from open_ai_search.common.async_parallel_iterator import AsyncParallelIterator
from open_ai_search.common.trace_info import TraceInfo
from open_ai_search.config import OpenAIConfig
from open_ai_search.entity import Retrieval
from open_ai_search.retriever.base import BaseRetriever


class RAG:

    def __init__(self, search_engine_list: List[BaseRetriever], config: OpenAIConfig):
        self.retriever_list: List[BaseRetriever] = search_engine_list

        self.client = AsyncOpenAI(base_url=config.base_url, api_key=config.api_key)
        self.model = config.model

        prompt_base_dir = "resource/prompt"
        self.prompt_filename: Dict[str, str] = {
            "qa": "qa.txt",
            "summary": "summary.txt",
            "entity": "entity.txt",
            "related_question": "related_question.txt"
        }

        self.task_prompt_dict: Dict[str, Dict[str, str]] = {}
        self.query_rewrite_prompt: Dict[str, str] = {}

        for lang in ["en", "zh"]:
            for key, filename in self.prompt_filename.items():
                with open(os.path.join(prompt_base_dir, lang, filename)) as f:
                    self.task_prompt_dict.setdefault(lang, {})[key] = f.read()

            with project_root.open(os.path.join(prompt_base_dir, lang, "rewrite.md")) as f:
                self.query_rewrite_prompt[lang] = f.read()

        self.zh_pattern: re.Pattern = re.compile(r"[\u4e00-\u9fa5]")
        self.json_pattern: re.Pattern = re.compile(r"```json\n(.*)\n```", re.DOTALL)

        self.rewrite_count: int = 3

    def _lang_detector(self, text: str) -> str:
        if self.zh_pattern.search(text):
            return "zh"
        return "en"

    @classmethod
    def _build_context(cls, retrieval_list: List[Retrieval]) -> str:
        retrival_prompt_list: List[str] = [
            "\n".join([f"[[{i + 1}]]", retrieval.to_prompt()])
            for i, retrieval in enumerate(retrieval_list)
        ]
        return "\n\n".join(retrival_prompt_list)

    @classmethod
    def _messages_prepare(cls, query: str, template: str, mapping: Dict[str, str | int]) -> List[Dict[str, str]]:
        system = template.format_map({"now": datetime.now().strftime("%Y-%m-%d %H:%M:%S")} | mapping)
        messages = [{"role": "system", "content": system}, {"role": "user", "content": query}]
        return messages

    async def _rewrite(self, query: str, trace_info: TraceInfo) -> List[str]:
        lang: str = self._lang_detector(query)
        messages = self._messages_prepare(query, self.query_rewrite_prompt[lang], {"max_num": self.rewrite_count})
        openai_response = await self.client.chat.completions.create(
            model=self.model, messages=messages, stream=False, temperature=0
        )
        str_response = openai_response.choices[0].message.content
        query_list = [query]
        try:
            if (match := self.json_pattern.search(str_response)) is not None:
                json_str_response: str = match.group(1).strip(" \n\r\t`")
                query_list = json.loads(json_str_response)
        except (json.JSONDecodeError,):
            trace_info.warning({"query": query, "response": str_response, "message": "query_rewrite_failed"})
        return query_list[:self.rewrite_count]

    async def _sub_search(self, sub_query: str, max_results: int, trace_info: TraceInfo) -> List[Retrieval]:
        retrieval_list: List[Retrieval] = sum(await asyncio.gather(*(
            retriever.search(sub_query, max_results)
            for retriever in self.retriever_list
        )), [])
        (trace_info.info if len(retrieval_list) > 0 else trace_info.warning)({  # noqa
            "sub_query": sub_query, "retrieval_cnt": len(retrieval_list)
        })
        return retrieval_list

    async def _search(self, query_list: List[str], max_results: int, trace_info: TraceInfo) -> List[Retrieval]:
        retrieval_list_list: List[List[Retrieval]] = await asyncio.gather(*(
            self._sub_search(sub_query, max_results, trace_info)
            for sub_query in query_list
        ))
        vis = []
        result_list: List[Retrieval] = []
        for retrieval_list in retrieval_list_list:
            for retrieval in retrieval_list:
                if retrieval.link not in vis:
                    result_list.append(retrieval)
                    vis.append(retrieval.link)
        (trace_info.info if len(result_list) > 0 else trace_info.warning)({  # noqa
            "query_list": query_list, "retrieval_cnt": len(result_list)
        })
        return result_list

    async def _answer(self, query: str, retrieval_list: List[Retrieval]) -> AsyncIterable[Dict[str, str]]:
        lang: str = self._lang_detector(query)
        context = self._build_context(retrieval_list)

        async_iter = AsyncParallelIterator({
            name: await self.client.chat.completions.create(
                model=self.model,
                messages=self._messages_prepare(query, template, {"context": context}),
                stream=True
            )
            for name, template in self.task_prompt_dict[lang].items()
        })

        async for name, response in async_iter:
            if delta := response.choices[0].delta.content:
                yield {"block": name, "delta": delta}

    async def search(
            self, query: str,
            max_results: int,
            trace_info: TraceInfo
    ) -> AsyncIterable[Dict[str, Union[str, Dict]]]:
        try:
            query_list: List[str] = await self._rewrite(query, trace_info)
            trace_info.info({"query_list": query_list})
            retrieval_list: List[Retrieval] = await self._search(query_list, max_results, trace_info)
            assert len(retrieval_list) > 0, "Empty retrieval result"

            citations: List[Dict[str, Any]] = [{
                "i": i + 1, **r.model_dump(exclude={"snippet", "content"})
            } for i, r in enumerate(retrieval_list)]
            yield {"block": "citation", "data": citations}

            async for block in self._answer(query, retrieval_list):
                yield block
        except Exception as e:
            yield {"error": str(e)}
