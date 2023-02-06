# pylint: disable=redefined-outer-name

import aiohttp.web
import pytest


@pytest.fixture
def handler():
    async def _handler(request):
        return aiohttp.web.json_response(
            {
                'login': request.cache.login,
                'uid': request.cache.uid,
                'token': request.cache.token,
            },
        )

    return _handler


@pytest.fixture
async def taxi_corp_admin_test_client(
        aiohttp_client, taxi_corp_admin_app, handler,
):
    taxi_corp_admin_app.router.add_get('/handler', handler)
    return await aiohttp_client(taxi_corp_admin_app)


async def test_request(taxi_corp_admin_test_client):
    from taxi_corp_admin.util import hdrs

    response = await taxi_corp_admin_test_client.get(
        '/handler',
        headers={
            hdrs.X_YATAXI_API_KEY: 'test_api_key',
            hdrs.X_YANDEX_LOGIN: 'test_login',
            hdrs.X_YANDEX_UID: 'test_uid',
        },
    )

    assert await response.json() == {
        'login': 'test_login',
        'uid': 'test_uid',
        'token': 'test_api_key',
    }
