import pytest


@pytest.fixture
def taxi_clowny_alert_manager_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_clowny_alert_manager_mocks')
async def test_ping(taxi_clowny_alert_manager_web):
    response = await taxi_clowny_alert_manager_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
