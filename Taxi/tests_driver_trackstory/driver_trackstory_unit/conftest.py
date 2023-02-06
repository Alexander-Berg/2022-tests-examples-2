# pylint: disable=wildcard-import, unused-wildcard-import, import-error
# pylint: disable=import-only-modules
from driver_trackstory_plugins import *  # noqa: F403 F401
from geobus_tools.geobus import geobus_publisher_extender  # noqa: F401 C5521
import pytest


# pylint: disable=redefined-outer-name
@pytest.fixture
def taxi_driver_trackstory_adv(
        taxi_driver_trackstory, geobus_publisher_extender,  # noqa: F811
):
    return geobus_publisher_extender(taxi_driver_trackstory)
