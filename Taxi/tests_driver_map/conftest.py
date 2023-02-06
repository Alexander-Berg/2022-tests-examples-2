# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from driver_map_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]
