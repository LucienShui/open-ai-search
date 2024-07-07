import argparse
import os
from typing import Dict

import yaml
from pydantic import BaseModel, Field


class Config(BaseModel):
    port: int = Field(default=8000)
    workers: int = Field(default=1)

    openai_api_key: str
    openai_model: str = Field(default="gpt-3.5-turbo")
    openai_base_url: str = Field(default="https://api.openai.com/v1")

    bing_search_base_url: str = Field(default="https://www.bing.com")
    bing_search_max_result_cnt: int = Field(default=20)

    bing_api_subscription_key: str = Field()
    bing_api_mkt: str = Field(default=None)


def load_from_config_file(yaml_path: str = "config.yaml") -> Dict[str, str]:
    if os.path.exists(yaml_path):
        with open(yaml_path) as f:
            return yaml.safe_load(f)
    return {}


def load_from_env() -> Dict[str, str]:
    _config: Dict[str, str] = {}

    for field_name in Config.__fields__.keys():
        _config[field_name] = os.getenv(field_name.upper(), None)
    return {k: v for k, v in _config.items() if v is not None}


def load_from_cli() -> Dict[str, str]:
    parser = argparse.ArgumentParser()
    for name, field in Config.__fields__.items():
        parser.add_argument(
            f"--{name}",
            dest=name,
            type=field.annotation,
            default=None,
            help=field.description,
        )
    args, _ = parser.parse_known_args()
    _config = vars(args)
    return {k: v for k, v in _config.items() if v is not None}


def load_config() -> Config:
    yaml_config: Dict[str, str] = load_from_config_file()
    env_config: Dict[str, str] = load_from_env()
    cli_config: Dict[str, str] = load_from_cli()
    config_merge: Dict[str, str] = {**yaml_config, **env_config, **cli_config}
    return Config.model_validate(config_merge)


config = load_config()
