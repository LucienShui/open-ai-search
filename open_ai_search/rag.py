import os
import re
from functools import partial
from typing import List, Iterable, Dict, Union, Any

from openai import OpenAI

from config import OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL_NAME
from open_ai_search.entity import Retrieval
from open_ai_search.iterator_tool import merge_iterators
from open_ai_search.search_engine import SearchEngine
from concurrent.futures import ThreadPoolExecutor


class RAG:

    def __init__(self, search_engine_list: List[SearchEngine]):
        self.search_engine_list: List[SearchEngine] = search_engine_list
        self.pool: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=len(self.search_engine_list))

        self.client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)
        self.chat = partial(self.client.chat.completions.create, model=OPENAI_MODEL_NAME)

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
        retrival_prompt_list: List[str] = []
        for i, retrieval in enumerate(retrieval_list):
            prompt_list: List[str] = [
                f"[[{i + 1}]]",
                f"Title: {retrieval.title}",
                f"Snippet: {retrieval.snippet}"
            ]
            if retrieval.content:
                prompt_list.append(f"Content: {retrieval.content}")
            if retrieval.date:
                prompt_list.append(f"Record date: {retrieval.date}")
            retrival_prompt_list.append("\n".join(prompt_list))
        return "\n\n".join(retrival_prompt_list)

    def messages_prepare(self, query: str, template: str, retrieval_list: List[Retrieval]) -> List[dict]:
        context = self.build_context(retrieval_list)
        messages = [
            {"role": "system", "content": template.format_map({"context": context})},
            {"role": "user", "content": query}
        ]
        return messages

    def search(self, query: str) -> Iterable[Dict[str, Union[str, Dict]]]:
        retrieval_list: List[Retrieval] = sum(self.pool.map(lambda x: x.search(query), self.search_engine_list), [])
        assert len(retrieval_list) > 0, "Empty retrieval result"

        citations: List[Dict[str, Any]] = [{
            "i": i + 1, **r.model_dump(exclude={"snippet", "content"})
        } for i, r in enumerate(retrieval_list)]
        yield {
            "block": "citation",
            "data": citations
        }

        lang: str = self.lang_detector(query)
        iterator: Iterable[Dict] = merge_iterators([
            self.chat(messages=self.messages_prepare(query, prompt, retrieval_list), stream=True)
            for prompt in self.prompt_dict[lang].values()
        ])

        for idx, response in iterator:
            yield {
                "block": list(self.prompt_filename.keys())[idx],
                "delta": response.choices[0].delta.content or ""
            }
