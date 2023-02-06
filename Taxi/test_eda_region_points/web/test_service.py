import pytest


@pytest.fixture
def eda_eda_region_points_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('eda_eda_region_points_mocks')
async def test_ping(taxi_eda_region_points_web):
    response = await taxi_eda_region_points_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
