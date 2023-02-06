import pytest


@pytest.fixture
def taxi_mia_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_mia_mocks')
async def test_ping(taxi_mia_web):
    response = await taxi_mia_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
