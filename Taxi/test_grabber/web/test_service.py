import pytest


@pytest.fixture
def taxi_grabber_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_grabber_mocks')
async def test_ping(taxi_grabber_web):
    response = await taxi_grabber_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
