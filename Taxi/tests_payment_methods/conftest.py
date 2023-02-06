# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from payment_methods_plugins import *  # noqa: F403 F401


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker(
            pytest.mark.geoareas(filename='db_geoareas.json', db_format=True),
        )
        item.add_marker(pytest.mark.tariffs(filename='tariffs.json'))
        item.add_marker(
            pytest.mark.translations(
                client_messages={
                    'integration.cash': {'en': 'Cash', 'ru': 'Наличные'},
                    'payment_method.disabled': {
                        'en': 'Disabled',
                        'ru': 'Выключено',
                    },
                },
            ),
        )
