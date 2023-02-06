import pytest


@pytest.mark.servicetest
async def test_ping(web_app_client):
    response = await web_app_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
