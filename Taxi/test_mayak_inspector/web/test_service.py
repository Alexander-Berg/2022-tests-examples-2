import pytest


@pytest.fixture
def taxi_mayak_inspector_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_mayak_inspector_mocks')
async def test_ping(taxi_mayak_inspector_web):
    response = await taxi_mayak_inspector_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
