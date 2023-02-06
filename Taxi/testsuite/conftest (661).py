# root conftest for service vgw-api
import pytest


pytest_plugins = ['vgw_api_plugins.pytest_plugins']


@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]
