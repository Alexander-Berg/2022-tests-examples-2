import pytest


@pytest.fixture
def taxi_hiring_partners_app_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_hiring_partners_app_mocks')
async def test_ping(taxi_hiring_partners_app_web):
    response = await taxi_hiring_partners_app_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
