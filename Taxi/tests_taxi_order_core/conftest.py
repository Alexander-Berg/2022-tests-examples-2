# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from order_core_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture
def service_client_default_headers():
    return {'Accept-Language': 'en'}


@pytest.fixture(scope='session')
def regenerate_config_hooks(regenerate_stat_client_config):
    return [regenerate_stat_client_config]
