import pytest


@pytest.fixture
def taxi_corp_requests_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_corp_requests_mocks')
async def test_ping(taxi_corp_requests_web):
    response = await taxi_corp_requests_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
