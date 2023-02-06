import pytest


@pytest.fixture
def taxi_feeds_admin_mocks():
    pass


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_feeds_admin_mocks')
async def test_ping(taxi_feeds_admin_web):
    response = await taxi_feeds_admin_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
