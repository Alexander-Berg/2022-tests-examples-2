import pytest


@pytest.fixture
def taxi_davos_landing_proxy_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_davos_landing_proxy_mocks')
async def test_ping(taxi_davos_landing_proxy_web):
    response = await taxi_davos_landing_proxy_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
