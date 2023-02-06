import pytest


@pytest.fixture
def taxi_agent_indicators_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_agent_indicators_mocks')
async def test_ping(taxi_agent_indicators_web):
    response = await taxi_agent_indicators_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
