import pytest


@pytest.fixture
def taxi_eventus_orchestrator_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_eventus_orchestrator_mocks')
async def test_ping(taxi_eventus_orchestrator_web):
    response = await taxi_eventus_orchestrator_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
