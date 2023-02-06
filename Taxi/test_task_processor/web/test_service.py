import pytest


@pytest.fixture
def taxi_task_processor_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_task_processor_mocks')
async def test_ping(taxi_task_processor_web):
    response = await taxi_task_processor_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
