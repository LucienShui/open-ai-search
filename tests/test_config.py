from open_ai_search.common.config_loader import Loader
from open_ai_search.config import Config


def test_load_config():
    loader = Loader(Config, env_prefix="OAS")
    config = loader.load()
    print(config.model_dump_json())
