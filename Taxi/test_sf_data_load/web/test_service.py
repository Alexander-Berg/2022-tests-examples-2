import pytest


@pytest.fixture
def taxi_sf_data_load_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_sf_data_load_mocks')
async def test_ping(taxi_sf_data_load_web):
    response = await taxi_sf_data_load_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
