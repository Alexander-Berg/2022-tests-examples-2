import pytest

from test_hiring_sf_loader import conftest


@pytest.fixture
def taxi_hiring_sf_loader_mocks(patch):
    pass


@pytest.mark.servicetest
@conftest.main_configuration
async def test_ping(taxi_hiring_sf_loader_web):
    response = await taxi_hiring_sf_loader_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
