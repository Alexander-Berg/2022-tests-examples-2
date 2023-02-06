# pylint: disable=C0103
import pytest


@pytest.fixture
def taxi_driver_ratings_storage_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_driver_ratings_storage_mocks')
async def test_ping(taxi_driver_ratings_storage_web):
    response = await taxi_driver_ratings_storage_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
