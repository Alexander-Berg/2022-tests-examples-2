import pytest


@pytest.fixture
def taxi_clowny_quotas_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_clowny_quotas_mocks')
async def test_ping(taxi_clowny_quotas_web):
    response = await taxi_clowny_quotas_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
