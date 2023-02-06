# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from eats_full_text_search_plugins import *  # noqa: F403 F401


def pytest_configure(config):
    config.addinivalue_line(
        'markers',
        'smart_prices_cache: [smart_prices_cache] ' 'fixture fo service cache',
    )
    config.addinivalue_line(
        'markers',
        'smart_prices_items: [smart_prices_items] ' 'fixture fo service cache',
    )
