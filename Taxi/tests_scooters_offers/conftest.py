# pylint: disable=wildcard-import, unused-wildcard-import, import-error

import pytest

from scooters_offers_plugins import *  # noqa: F403 F401

from tests_scooters_offers import consts


@pytest.fixture(autouse=True)
def mock_car_details(mockserver):
    # this endpoint is needed for cache filling
    @mockserver.json_handler('/scooter-backend/api/taxi/car/details')
    async def _car_details_mock(_):
        return mockserver.make_response(
            status=200, json={'timestamp': 1655758800, 'cars': consts.CARS},
        )


@pytest.fixture(autouse=True)
def mock_scooters_misc_areas(mockserver):
    # this endpoint is needed for scooters-polygons-cache filling
    @mockserver.json_handler('/scooters-misc/scooters-misc/v1/areas')
    async def _scooters_misc_areas(_):
        return mockserver.make_response(
            status=200, json={'areas': consts.AREAS},
        )
