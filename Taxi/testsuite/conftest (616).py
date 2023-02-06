# pylint: disable=redefined-outer-name
import pytest


# root conftest for service tags
pytest_plugins = ['tags_plugins.pytest_plugins']


@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]
