import pytest


@pytest.fixture
def taxi_pro_test_order_maker_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_pro_test_order_maker_mocks')
async def test_ping(taxi_pro_test_order_maker_web):
    response = await taxi_pro_test_order_maker_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
