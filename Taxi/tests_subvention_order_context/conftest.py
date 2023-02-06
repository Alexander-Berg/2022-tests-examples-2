import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from subvention_order_context_plugins import *  # noqa: F403 F401


@pytest.fixture(name='unique_drivers_fixture', autouse=True)
def _unique_drivers_fixture(unique_drivers, request):
    unique_drivers.add_driver('dbid', 'uuid', 'unique_driver_id')
