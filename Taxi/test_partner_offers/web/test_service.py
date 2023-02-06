import pytest


@pytest.fixture
def taxi_partner_offers_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_partner_offers_mocks')
async def test_ping(taxi_partner_offers_web):
    response = await taxi_partner_offers_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
