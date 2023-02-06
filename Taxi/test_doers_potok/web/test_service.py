import pytest


@pytest.fixture
def taxi_doers_potok_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_doers_potok_mocks')
async def test_ping(taxi_doers_potok_web):
    response = await taxi_doers_potok_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
