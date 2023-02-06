import pytest


@pytest.fixture
def taxi_preorder_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_preorder_mocks')
async def test_ping(taxi_preorder_web):
    response = await taxi_preorder_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
