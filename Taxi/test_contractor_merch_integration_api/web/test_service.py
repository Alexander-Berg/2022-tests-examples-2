import pytest


@pytest.fixture
def api_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('api_mocks')
async def test_ping(taxi_contractor_merch_integration_api_web):
    response = await taxi_contractor_merch_integration_api_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
