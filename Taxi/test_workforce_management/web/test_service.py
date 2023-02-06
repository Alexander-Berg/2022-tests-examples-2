import pytest


@pytest.fixture
def taxi_workforce_management_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_workforce_management_mocks')
async def test_ping(taxi_workforce_management_web):
    response = await taxi_workforce_management_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
