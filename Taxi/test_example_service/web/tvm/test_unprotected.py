import pytest


async def check_get_handler(web_app_client):
    response = await web_app_client.get('/tvm/unprotected')
    assert response.status == 200
    content = await response.text()
    assert content == 'unprotected'


async def check_head_handler(web_app_client):
    response = await web_app_client.head('/tvm/unprotected')
    assert response.status == 200


@pytest.mark.config(TVM_ENABLED=True)
async def test_get_tvm_enabled_unprotected(web_app_client):
    await check_get_handler(web_app_client)


@pytest.mark.config(TVM_ENABLED=False)
async def test_get_tvm_disabled_unprotected(web_app_client):
    await check_get_handler(web_app_client)


@pytest.mark.config(TVM_ENABLED=True)
async def test_head_tvm_enabled_unprotected(web_app_client):
    await check_head_handler(web_app_client)


@pytest.mark.config(TVM_ENABLED=False)
async def test_head_tvm_disabled_unprotected(web_app_client):
    await check_head_handler(web_app_client)
