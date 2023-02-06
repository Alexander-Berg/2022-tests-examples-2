# pylint: disable=wildcard-import, unused-wildcard-import, import-error
from fleet_vehicles_plugins import *  # noqa: F403 F401
import pytest


@pytest.fixture
def sort_amenities():
    def _func(data: dict) -> None:
        for vehicle in data.get('vehicles', []):
            amenities = vehicle.get('data', {}).get('amenities')
            if amenities:
                amenities.sort()

    return _func
