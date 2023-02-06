import pytest


# root conftest for service superapp-misc
pytest_plugins = ['superapp_misc_plugins.pytest_plugins']


@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]
