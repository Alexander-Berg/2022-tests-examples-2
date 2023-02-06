import pytest


@pytest.fixture
def taxi_form_builder_mocks():
    """Put your mocks here"""


@pytest.mark.servicetest
@pytest.mark.usefixtures('taxi_form_builder_mocks')
async def test_ping(taxi_form_builder_web):
    response = await taxi_form_builder_web.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''


async def test_ping_simple(web_app_client):
    response = await web_app_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
