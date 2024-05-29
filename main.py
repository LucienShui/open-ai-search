from duckduckgo_search import DDGS
from typing import Optional, List
from pydantic import BaseModel, Field


class Retrieval(BaseModel):
    title: str = Field(description="")
    link: str = Field(description="", alias="href")
    snippet: str = Field(description="", alias="body")
    content: Optional[str] = Field(description="", default=None)


def main():
    se = DDGS()
    retrievals: List[Retrieval] = [Retrieval(**result) for result in se.text("今日新闻", region="cn-zh")]


if __name__ == '__main__':
    main()
