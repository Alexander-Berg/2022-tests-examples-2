import pytest


@pytest.fixture
def taxi_crm_efficiency_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_crm_efficiency_mocks')
async def test_ping(taxi_crm_efficiency_web):
    response = await taxi_crm_efficiency_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
