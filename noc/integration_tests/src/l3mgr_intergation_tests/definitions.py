import os

from .core.config import init_base_config


PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_CONFIG = init_base_config(PROJECT_ROOT + "/config.toml")
