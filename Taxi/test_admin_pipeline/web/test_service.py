import pytest


@pytest.fixture
def taxi_admin_pipeline_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_admin_pipeline_mocks')
async def test_ping(taxi_admin_pipeline_web):
    response = await taxi_admin_pipeline_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
