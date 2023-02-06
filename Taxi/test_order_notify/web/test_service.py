import pytest


@pytest.fixture
def taxi_order_notify_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_order_notify_mocks')
async def test_ping(taxi_order_notify_web):
    response = await taxi_order_notify_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
