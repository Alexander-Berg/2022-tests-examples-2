# root conftest for service subvention-view
import pytest

pytest_plugins = ['subvention_view_plugins.pytest_plugins']


@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]
