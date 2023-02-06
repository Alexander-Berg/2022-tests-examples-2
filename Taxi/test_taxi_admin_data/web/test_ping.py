import pytest


@pytest.fixture
def taxi_admin_data_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_admin_data_mocks')
async def test_ping(web_app_client):
    response = await web_app_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
