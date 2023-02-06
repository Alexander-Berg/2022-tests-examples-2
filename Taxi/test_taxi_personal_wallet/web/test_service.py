import pytest


@pytest.fixture
def taxi_personal_wallet_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_personal_wallet_mocks')
async def test_ping(test_wallet_client):
    response = await test_wallet_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
