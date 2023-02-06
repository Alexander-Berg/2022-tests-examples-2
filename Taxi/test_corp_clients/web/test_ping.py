import pytest


@pytest.fixture
def taxi_corp_clients_mocks(personal_mock):
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_corp_clients_mocks')
async def test_ping(taxi_corp_clients_web):
    response = await taxi_corp_clients_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
