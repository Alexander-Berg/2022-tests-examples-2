# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
# from driver_weariness_plugins.generated_tests import *  # noqa

import pytest


# Every service must have this handler
@pytest.mark.unique_drivers(
    stream={
        'licenses_by_unique_drivers': {'last_revision': '0_0', 'items': []},
        'license_by_driver_profile': {'last_revision': '0_0', 'items': []},
    },
)
@pytest.mark.servicetest
async def test_ping(taxi_driver_weariness):
    response = await taxi_driver_weariness.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''
