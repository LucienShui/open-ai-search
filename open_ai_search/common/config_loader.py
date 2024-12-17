import argparse
import os
from typing import Dict, Type, TypeVar, Optional

import yaml
from pydantic import BaseModel

from open_ai_search.common.logger import get_logger

logger = get_logger(__name__)

_Config = TypeVar("_Config", bound=BaseModel)


def load_from_config_file(config_path: Optional[str] = None) -> Dict[str, str]:
    with open(config_path) as f:
        return yaml.safe_load(f)


def dict_prefix_filter(prefix: str, data: dict) -> dict:
    return {k[len(prefix):]: v for k, v in data.items() if k.startswith(prefix)}


def dfs(config_model: Type[_Config], env_dict: Dict[str, str]) -> dict:
    result = {}
    for field_name, field_info in config_model.model_fields.items():
        filtered_env_dict = dict_prefix_filter(field_name.upper(), env_dict)
        if "" in filtered_env_dict:
            assert len(filtered_env_dict) == 1, f"Conflict name: {field_name}"
            value = filtered_env_dict.pop("")
            result[field_name] = field_info.annotation(value)  # noqa
            continue
        if filtered_env_dict:
            assert issubclass(field_info.annotation, BaseModel)
            result[field_name] = dfs(field_info.annotation, dict_prefix_filter("_", filtered_env_dict))
    return result


def load_from_env(config_model: Type[_Config], env_prefix: str) -> Dict[str, str]:
    env_dict: Dict[str, str] = dict_prefix_filter(env_prefix, dict(os.environ))
    if "" in env_dict:
        env_dict.pop("")

    result = dfs(config_model, dict_prefix_filter("_", env_dict))

    return result


def load_from_cli(config_model: Type[_Config]) -> Dict[str, str]:
    parser = argparse.ArgumentParser()
    for name, field in config_model.model_fields.items():
        parser.add_argument(
            f"--{name}",
            dest=name,
            type=field.annotation,
            default=None,
            help=field.description,
        )
    args, _ = parser.parse_known_args()
    c = vars(args)
    return {k: v for k, v in c.items() if v is not None}


def load_config(config_model: Type[_Config], env_prefix: Optional[str] = None,
                config_path: Optional[str] = None) -> _Config:
    config_merge: dict = {}
    if env_prefix is not None:
        env_config: Dict[str, str] = load_from_env(config_model, env_prefix)
        logger.debug({"env_config": env_config})
        config_merge = config_merge | env_config
    if config_path is not None:
        yaml_config: Dict[str, str] = load_from_config_file(config_path)
        logger.debug({"yaml_config": yaml_config})
        config_merge = config_merge | yaml_config
    cli_config: Dict[str, str] = load_from_cli(config_model)
    logger.debug({"cli_config": cli_config})
    config_merge = config_merge | cli_config
    logger.debug({"config_merge": config_merge})
    return config_model.model_validate(config_merge)


__all__ = ["load_config"]
