import pytest


@pytest.fixture
def taxi_dispatch_settings_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_dispatch_settings_mocks')
async def test_ping(taxi_dispatch_settings_web):
    response = await taxi_dispatch_settings_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
