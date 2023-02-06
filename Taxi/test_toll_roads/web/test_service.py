import pytest


@pytest.fixture
def taxi_toll_roads_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_toll_roads_mocks')
async def test_ping(taxi_toll_roads_web):
    response = await taxi_toll_roads_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
