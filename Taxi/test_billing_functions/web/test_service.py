import pytest


@pytest.fixture
def taxi_billing_functions_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_billing_functions_mocks')
async def test_ping(taxi_billing_functions_web):
    response = await taxi_billing_functions_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
