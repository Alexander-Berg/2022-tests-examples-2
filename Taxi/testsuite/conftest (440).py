import pytest

# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from grocery_surge_plugins import *  # noqa: F403 F401


# root conftest for service grocery-surge
pytest_plugins = ['grocery_surge_plugins.pytest_plugins']


@pytest.fixture(autouse=True)
@pytest.mark.yt(dyn_table_data=['yt_orders_empty.yaml'])
def yt_orders_empty():
    pass
