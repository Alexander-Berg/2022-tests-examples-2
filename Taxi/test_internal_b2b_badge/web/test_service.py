import pytest


@pytest.fixture
def taxi_internal_b2b_badge_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_internal_b2b_badge_mocks')
async def test_ping(taxi_internal_b2b_badge_web):
    response = await taxi_internal_b2b_badge_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
