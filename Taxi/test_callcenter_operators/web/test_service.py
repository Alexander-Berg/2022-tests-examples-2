import pytest


@pytest.fixture
def taxi_callcenter_operators_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_callcenter_operators_mocks')
async def test_ping(taxi_callcenter_operators_web):
    response = await taxi_callcenter_operators_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
