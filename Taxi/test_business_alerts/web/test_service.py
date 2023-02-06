import pytest


@pytest.fixture
def taxi_business_alerts_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_business_alerts_mocks')
async def test_ping(taxi_business_alerts_web):
    response = await taxi_business_alerts_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
