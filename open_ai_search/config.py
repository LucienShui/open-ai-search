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

    bing_search_base_url: str = Field(default="https://www.bing.com")
    bing_search_max_results: int = Field(default=20)

    bing_api_subscription_key: str = Field()
    bing_api_mkt: str = Field(default=None)
