# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
# from driver_priority_plugins.generated_tests import *  # noqa

import pytest


# Every service must have this handler
@pytest.mark.servicetest
async def test_ping(taxi_driver_priority):
    response = await taxi_driver_priority.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''
