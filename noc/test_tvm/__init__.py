import sys

import envtoml as toml
from box import Box

from balancer_agent.core import config
from balancer_agent.schemas.utils import SchemaHandler


# Patching config.init_base_config, because by default it loads config file from BASE_CONFIG_PATH
# which may be not available in test/dev env
def patched_init_base_config(version, *args):
    config_schema = SchemaHandler("agent_config.json", version)
    base_config = toml.load(sys.modules["balancer_agent.definitions"].PROJECT_ROOT + "/config_testenv.toml")
    config_schema.validate(base_config)

    base_config = Box(base_config)
    base_config.auth.tvm.enabled = False

    return base_config


config.init_base_config = patched_init_base_config
