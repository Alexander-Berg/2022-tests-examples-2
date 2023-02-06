import pytest


@pytest.fixture
def taxi_support_tags_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_support_tags_mocks')
async def test_ping(taxi_support_tags_web):
    response = await taxi_support_tags_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
