import pytest


@pytest.fixture
def taxi_driver_metrics_mocks(taxi_driver_metrics):
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_driver_metrics_mocks')
async def test_ping(taxi_driver_metrics):
    response = await taxi_driver_metrics.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
