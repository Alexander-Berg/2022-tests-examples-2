import pytest


@pytest.fixture
def taxi_admin_personal_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_admin_personal_mocks')
async def test_ping(taxi_admin_personal):
    response = await taxi_admin_personal.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
