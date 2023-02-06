import pytest


@pytest.fixture
def taxi_duty_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_duty_mocks')
async def test_ping(taxi_duty_web):
    response = await taxi_duty_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
