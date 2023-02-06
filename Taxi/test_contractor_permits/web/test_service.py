import pytest


@pytest.fixture
def taxi_contractor_permits_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_contractor_permits_mocks')
async def test_ping(taxi_contractor_permits_web):
    response = await taxi_contractor_permits_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
