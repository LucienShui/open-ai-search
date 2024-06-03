from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class Retrieval(BaseModel):
    title: str = Field(description="Title")
    link: str = Field(description="Link of retrival")
    snippet: str = Field(description="Snippet from search engine")
    content: Optional[str] = Field(description="Full content", default=None)
    date: Optional[str] = Field(description="Scraped date", default=None)

    def to_citation_dict(self, i: int) -> Dict[str, Any]:
        citation_dict: Dict[str, Any] = {"i": i, "title": self.title, "link": self.link}
        if self.content:
            citation_dict["content"] = self.content
        if self.date:
            citation_dict["date"] = self.date
        return citation_dict
