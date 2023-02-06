import pytest


@pytest.fixture
def taxi_atlas_etl_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_atlas_etl_mocks')
async def test_ping(taxi_atlas_etl_web):
    response = await taxi_atlas_etl_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
