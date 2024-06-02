from pydantic import BaseModel, Field
from typing import Optional


class Retrieval(BaseModel):
    title: str = Field(description="Title")
    link: str = Field(description="Link of retrival")
    snippet: str = Field(description="Snippet from search engine")
    content: Optional[str] = Field(description="Full content", default=None)
    record_date: Optional[str] = Field(description="Record date", default=None)
