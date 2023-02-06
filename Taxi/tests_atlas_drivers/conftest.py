# pylint: disable=wildcard-import, unused-wildcard-import, import-error
import pytest

from atlas_drivers_plugins import *  # noqa: F403 F401


def pytest_collection_modifyitems(config, items):
    for item in items:
        item.add_marker(
            pytest.mark.geoareas(filename='db_geoareas.json', db_format=True),
        )
        item.add_marker(pytest.mark.tariffs(filename='tariffs.json'))
