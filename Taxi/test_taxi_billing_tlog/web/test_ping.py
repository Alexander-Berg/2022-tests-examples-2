import pytest


async def test_ping(web_app_client):
    response = await web_app_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''


@pytest.mark.config(TVM_ENABLED=True)
async def test_ping_tvm_enabled(web_app_client):
    response = await web_app_client.get('/ping')
    assert response.status == 200
    content = await response.text()
    assert content == ''
