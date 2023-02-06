import pytest


@pytest.fixture
def taxi_geotracks_admin_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_geotracks_admin_mocks')
async def test_ping(taxi_geotracks_admin_web):
    response = await taxi_geotracks_admin_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
