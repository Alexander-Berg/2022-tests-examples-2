import pytest


@pytest.fixture
def mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('mocks')
async def test_ping(taxi_fleet_drivers_scoring_web):
    response = await taxi_fleet_drivers_scoring_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
