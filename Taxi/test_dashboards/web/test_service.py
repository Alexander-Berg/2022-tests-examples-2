import pytest


@pytest.fixture
def taxi_dashboards_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_dashboards_mocks')
async def test_ping(taxi_dashboards_web):
    response = await taxi_dashboards_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
