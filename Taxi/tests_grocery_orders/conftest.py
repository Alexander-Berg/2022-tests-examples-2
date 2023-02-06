# pylint: disable=wildcard-import, unused-wildcard-import, import-error

from grocery_orders_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture(name='grocery_depots', autouse=True)
def mock_grocery_depots(grocery_depots):
    class Context:
        def add_depot(self, legacy_depot_id, **kwargs):
            grocery_depots.add_depot(
                int(legacy_depot_id),
                legacy_depot_id=legacy_depot_id,
                **kwargs,
            )

        def clear_depots(self):
            grocery_depots.clear_depots()

    context = Context()

    return context
