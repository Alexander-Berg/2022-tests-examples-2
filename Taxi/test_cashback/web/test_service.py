import pytest


@pytest.fixture
def taxi_cashback_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_cashback_mocks')
async def test_ping(taxi_cashback_web):
    response = await taxi_cashback_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
