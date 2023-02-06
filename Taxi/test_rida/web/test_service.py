import pytest


@pytest.fixture
def taxi_rida_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_rida_mocks')
async def test_ping(taxi_rida_web):
    response = await taxi_rida_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
