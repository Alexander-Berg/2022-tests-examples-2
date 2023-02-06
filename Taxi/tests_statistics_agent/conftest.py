# pylint: disable=redefined-outer-name
import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from statistics_agent_plugins import *  # noqa: F403 F401


@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]
