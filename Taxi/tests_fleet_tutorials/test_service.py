import pytest

# Feel free to provide your custom implementation to override generated tests.

# pylint: disable=import-error,wildcard-import
from fleet_tutorials_plugins.generated_tests import *  # noqa


# Every service must have this handler
@pytest.mark.servicetest
async def test_ping(mock_feeds, taxi_fleet_tutorials):

    response = await taxi_fleet_tutorials.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''
