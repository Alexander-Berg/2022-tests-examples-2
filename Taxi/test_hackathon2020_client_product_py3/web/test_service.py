import pytest


@pytest.fixture
def taxi_service_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_service_mocks')
async def test_ping(taxi_hackathon2020_client_product_py3_web):
    response = await taxi_hackathon2020_client_product_py3_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
