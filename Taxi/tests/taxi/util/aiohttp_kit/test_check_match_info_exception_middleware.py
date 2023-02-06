# pylint: disable=invalid-name
# pylint: disable=protected-access
from aiohttp import web
import pytest

from taxi import config
from taxi import web_app
from taxi.util.aiohttp_kit import middleware


@pytest.mark.parametrize(
    'url,enable_middleware,expected_status',
    [
        ('/test/path', True, 200),
        ('/test/path', False, 200),
        ('/test/wrong/path', True, 404),
        ('/test/wrong/path', False, 500),
    ],
)
async def test_middleware(
        aiohttp_client,
        loop,
        db,
        simple_secdist,
        url,
        enable_middleware,
        expected_status,
):
    app = _create_app(loop, db, enable_middleware)

    client = await aiohttp_client(app)
    response = await client.post(
        url, params={'arg1': 'some_value'}, json={'prop2': 123},
    )
    assert response.status == expected_status


def _create_app(loop, db, enable_middleware):
    @web.middleware
    async def _other_middleware(request, handler):
        assert request.match_info.http_exception is None
        return await handler(request)

    def _dummy_handler(request):
        return web.json_response({})

    app = web_app.TaxiApplication(
        config_cls=config.Config, loop=loop, db=db, service_name='TEST',
    )
    app.router.add_post('/test/path', _dummy_handler)
    if enable_middleware:
        app.middlewares.append(middleware.check_match_info_exception)
    app.middlewares.append(_other_middleware)
    return app
