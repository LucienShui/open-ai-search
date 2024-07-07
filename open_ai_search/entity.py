from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class Retrieval(BaseModel):
    title: str = Field(description="Title")
    link: str = Field(description="Link of retrival")
    snippet: str = Field(description="Snippet from search engine")
    source: str = Field(description="Source of retrival")
    content: Optional[str] = Field(description="Full content", default=None)
    date: Optional[str] = Field(description="Scraped date", default=None)
    icon_url: Optional[str] = Field(description="Scraped icon", default=None)
    author: Optional[str] = Field(description="Author", default=None)
