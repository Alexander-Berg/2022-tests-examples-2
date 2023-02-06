import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from grocery_performer_communications_plugins import *  # noqa: F403 F401

import tests_grocery_performer_communications.constants as consts


@pytest.fixture(autouse=True)
async def add_depot(grocery_depots):
    grocery_depots.clear_depots()
    grocery_depots.add_depot(
        depot_test_id=int(consts.DEPOT_ID_LEGACY),
        region_id=consts.REGION_ID,
        timezone=consts.TIMEZONE,
        short_address=consts.DEPOT_SHORT_ADDRESS,
        auto_add_zone=False,
    )
