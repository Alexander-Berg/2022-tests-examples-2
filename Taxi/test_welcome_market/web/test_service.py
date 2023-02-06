import pytest


@pytest.fixture
def taxi_welcome_market_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_welcome_market_mocks')
async def test_ping(taxi_welcome_market_web):
    response = await taxi_welcome_market_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
