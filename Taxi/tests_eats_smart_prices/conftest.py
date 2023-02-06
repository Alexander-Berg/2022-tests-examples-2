# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_catalog_storage_cache import (  # noqa: F403 F401
    eats_catalog_storage_cache,  # noqa: F403 F401
)
import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_smart_prices_plugins import *  # noqa: F403 F401


@pytest.fixture(name='eats_smart_prices_cursor')
def get_eats_smart_prices_cursor(pgsql):
    return pgsql['eats_smart_prices'].dict_cursor()


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'eats_catalog_storage_cache: [eats_catalog_storage_cache] '
        'fixture fo service cache',
    )
