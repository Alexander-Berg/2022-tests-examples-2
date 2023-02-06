import pytest


@pytest.fixture
def taxi_dldmitry_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_dldmitry_mocks')
async def test_ping(taxi_dldmitry_test_service_web):
    response = await taxi_dldmitry_test_service_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
