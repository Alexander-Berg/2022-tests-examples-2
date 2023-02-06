# pylint: disable=C5521, W0621
import pytest

# Every service must have this handler
@pytest.mark.pgsql('reposition', files=['config_main.sql'])
@pytest.mark.servicetest
async def test_ping(taxi_reposition_api):
    response = await taxi_reposition_api.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''
