import pytest


@pytest.fixture
def taxi_papersplease_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_papersplease_mocks')
async def test_ping(taxi_papersplease_web):
    response = await taxi_papersplease_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
