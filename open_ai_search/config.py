from pydantic import BaseModel, Field


class OpenAIConfig(BaseModel):
    api_key: str
    model: str = Field(default="gpt-3.5-turbo")
    base_url: str = Field(default="https://api.openai.com/v1")


class SearchConfig(BaseModel):
    max_results: int = Field(default=10)


class Config(BaseModel):
    openai: OpenAIConfig
    search: SearchConfig = Field(default_factory=SearchConfig)
