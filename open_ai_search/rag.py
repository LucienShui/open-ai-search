import os
from functools import partial
from typing import Optional, List, Iterable, Dict, Union

from duckduckgo_search import DDGS
from openai import OpenAI
from pydantic import BaseModel, Field

from config import OPENAI_BASE_URL, OPENAI_API_KEY, OPENAI_MODEL_NAME
from open_ai_search.iterator_tool import merge_iterators


class Retrieval(BaseModel):
    title: str = Field(description="Title")
    link: str = Field(description="URL", alias="href")
    snippet: str = Field(description="Summary from search engine", alias="body")
    content: Optional[str] = Field(description="Full content", default=None)
    record_date: Optional[str] = Field(description="Record data", default=None)


class RAG:

    def __init__(self):
        self.search_engine: DDGS = DDGS()
        self.client = OpenAI(base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)
        self.chat = partial(self.client.chat.completions.create, model=OPENAI_MODEL_NAME)

        prompt_base_dir = "resource/prompt"
        self.prompt_dict = {
            "qa": "qa.txt",
            "summary": "summary.txt",
            "table": "table.txt",
            "related_question": "related_question.txt"
        }
        for key, filename in self.prompt_dict.items():
            with open(os.path.join(prompt_base_dir, filename)) as f:
                self.prompt_dict[key] = f.read()

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
            if retrieval.record_date:
                prompt_list.append(f"Record date: {retrieval.record_date}")
            retrival_prompt_list.append("\n".join(prompt_list))
        return "\n\n".join(retrival_prompt_list)

    def messages_prepare(self, query: str, template: str, retrieval_list: List[Retrieval]) -> List[dict]:
        context = self.build_context(retrieval_list)
        messages = [
            {"role": "system", "content": template.format_map({"context": context})},
            {"role": "user", "content": query}
        ]
        return messages

    def search(self, query: str, region: str = "cn-zh") -> Iterable[Dict[str, Union[str, int]]]:
        search_result_list: List[Dict] = self.search_engine.text(query, region=region)
        retrival_list: List[Retrieval] = [Retrieval(**result) for result in search_result_list]
        iterator = merge_iterators([
            self.chat(messages=self.messages_prepare(query, prompt, retrival_list), stream=True)
            for prompt in self.prompt_dict.values()
        ])

        citations: List[Dict] = [{"i": i + 1, "title": retrieval.title, "link": retrieval.link}
                                 for i, retrieval in enumerate(retrival_list)]
        yield {
            "block": "citation",
            "data": citations
        }

        for idx, response in iterator:
            yield {
                "block": list(self.prompt_dict.keys())[idx],
                "delta": response.choices[0].delta.content
            }
