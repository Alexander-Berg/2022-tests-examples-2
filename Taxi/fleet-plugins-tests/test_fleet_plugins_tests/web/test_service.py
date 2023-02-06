import pytest


@pytest.fixture
def taxi_fleet_plugins_tests_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_fleet_plugins_tests_mocks')
async def test_ping(taxi_fleet_plugins_tests_web):
    response = await taxi_fleet_plugins_tests_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
