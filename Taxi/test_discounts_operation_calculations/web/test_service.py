import pytest


@pytest.fixture
def taxi_discounts_operation_calculations_mocks():  # pylint: disable=C0103
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_discounts_operation_calculations_mocks')
async def test_ping(taxi_discounts_operation_calculations_web):
    response = await taxi_discounts_operation_calculations_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
