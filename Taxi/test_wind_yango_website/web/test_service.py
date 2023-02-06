import pytest


@pytest.fixture
def taxi_wind_yango_website_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_wind_yango_website_mocks')
async def test_ping(taxi_wind_yango_website_web):
    response = await taxi_wind_yango_website_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
