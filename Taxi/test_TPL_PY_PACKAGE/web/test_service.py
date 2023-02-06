import pytest


@pytest.fixture
def TPL_WITH_TAXI_SNAKE_CASE_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('TPL_WITH_TAXI_SNAKE_CASE_mocks')
async def test_ping(TPL_WITH_TAXI_SNAKE_CASE_web):
    response = await TPL_WITH_TAXI_SNAKE_CASE_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
