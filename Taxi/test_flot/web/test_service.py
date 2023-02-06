import pytest


@pytest.fixture
def flot_flot_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('flot_flot_mocks')
async def test_ping(taxi_flot_web):
    response = await taxi_flot_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
