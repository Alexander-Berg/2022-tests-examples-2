from aiohttp import web
import pytest


@pytest.fixture(name='client')
def da_client_fixture(web_context):
    return web_context.clients.driver_authorizer


async def test_happy_path(client, mock_driver_authorizer):
    @mock_driver_authorizer('/driver/sessions')
    async def handler(request):
        assert request.query.get('int_param') is None
        return web.json_response(
            data={'ttl': 3600}, headers={'X-Driver-Session': '100500'},
        )

    response = await client.driver_sessions_get(
        uuid='1111', _sep_thread_deserialize=True,
    )

    assert response.status == 200
    assert response.body.ttl == 3600
    assert response.headers.x_driver_session == '100500'

    assert handler.times_called == 1
