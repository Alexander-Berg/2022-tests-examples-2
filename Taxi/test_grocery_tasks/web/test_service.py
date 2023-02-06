import pytest


@pytest.fixture
def taxi_grocery_tasks_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_grocery_tasks_mocks')
async def test_ping(taxi_grocery_tasks_web):
    response = await taxi_grocery_tasks_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
