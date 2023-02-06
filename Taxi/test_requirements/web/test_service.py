import pytest


@pytest.fixture
def taxi_requirements_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_requirements_mocks')
async def test_ping(taxi_requirements_web):
    response = await taxi_requirements_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
