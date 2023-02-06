import pytest


@pytest.fixture
def taxi_workforce_metrics_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_workforce_metrics_mocks')
async def test_ping(taxi_workforce_metrics_web):
    response = await taxi_workforce_metrics_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
