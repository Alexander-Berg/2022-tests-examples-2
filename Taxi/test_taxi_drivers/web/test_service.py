import pytest


@pytest.fixture
def taxi_drivers_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_drivers_mocks')
async def test_ping(taxi_drivers_web):
    response = await taxi_drivers_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
