from typing import Optional, List

from pydantic import BaseModel, Field


class Retrieval(BaseModel):
    title: str = Field(description="Title")
    link: str = Field(description="Link of retrival")
    snippet: str = Field(description="Snippet from search engine")
    source: str = Field(description="Source of retrival")
    content: Optional[str] = Field(description="Full content", default=None)
    date: Optional[str] = Field(description="Scraped date", default=None)
    icon_url: Optional[str] = Field(description="Scraped icon", default=None)
    author: Optional[str] = Field(description="Author", default=None)

    def to_prompt(self) -> str:
        prompt_list: List[str] = [
            f"title: {self.title}",
            f"snippet: {self.snippet}"
        ]
        if self.content:
            prompt_list.append(f"content: {self.content}")
        if self.date:
            prompt_list.append(f"date: {self.date}")
        prompt = "\n".join(prompt_list)
        return prompt
