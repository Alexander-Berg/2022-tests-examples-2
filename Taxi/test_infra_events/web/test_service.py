import pytest


@pytest.fixture
def taxi_infra_events_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_infra_events_mocks')
async def test_ping(taxi_infra_events_web):
    response = await taxi_infra_events_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
