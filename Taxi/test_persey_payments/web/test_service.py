import pytest


@pytest.fixture
def taxi_persey_payments_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_persey_payments_mocks')
async def test_ping(taxi_persey_payments_web):
    response = await taxi_persey_payments_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
