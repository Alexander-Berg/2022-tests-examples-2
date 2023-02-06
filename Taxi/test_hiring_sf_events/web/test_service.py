import pytest

from test_hiring_sf_events import conftest


@pytest.fixture
def taxi_hiring_sf_events_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_hiring_sf_events_mocks', 'fill_initial_data')
@conftest.main_configuration
async def test_ping(taxi_hiring_sf_events_web):
    response = await taxi_hiring_sf_events_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
