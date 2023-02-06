import pytest


@pytest.fixture
def taxi_eats_cc_monitoring_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_eats_cc_monitoring_mocks')
async def test_ping(taxi_eats_contact_center_monitoring_web):
    response = await taxi_eats_contact_center_monitoring_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
