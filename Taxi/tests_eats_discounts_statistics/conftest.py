import pytest
# pylint: disable=wildcard-import, unused-wildcard-import, import-error

from eats_discounts_statistics_plugins import *  # noqa: F403 F401


@pytest.fixture()
def client(taxi_eats_discounts_statistics):
    return taxi_eats_discounts_statistics
