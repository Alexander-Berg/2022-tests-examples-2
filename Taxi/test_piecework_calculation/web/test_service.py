import pytest


@pytest.fixture
def piecework_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('piecework_mocks')
async def test_ping(taxi_piecework_calculation_web):
    response = await taxi_piecework_calculation_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
