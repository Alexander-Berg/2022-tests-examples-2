import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from grocery_delivery_conditions_plugins import *  # noqa: F403 F401

from .plugins import keys


@pytest.fixture(name='grocery_depots', autouse=True)
def mock_grocery_depots(grocery_depots):
    grocery_depots.add_depot(
        int(keys.DEFAULT_LEGACY_DEPOT_ID),
        legacy_depot_id=keys.DEFAULT_LEGACY_DEPOT_ID,
        depot_id=keys.DEFAULT_WMS_DEPOT_ID,
        location=keys.DEFAULT_DEPOT_LOCATION,
    )
    return grocery_depots
