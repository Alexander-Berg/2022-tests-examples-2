import pytest


@pytest.fixture
def taxi_passenger_profile_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_passenger_profile_mocks')
@pytest.mark.usefixtures('client_experiments3')
async def test_ping(taxi_passenger_profile_web):
    response = await taxi_passenger_profile_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
