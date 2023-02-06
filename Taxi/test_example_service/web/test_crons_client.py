import datetime
import json

from aiohttp import web
import pytest

from generated import models
from generated.clients import crons as crons_module
from taxi.util import dates


DATE = '2017-11-01T01:10:00+03:00'
DATE_IN_ONE_DAY = '2017-11-02T01:10:00+03:00'


@pytest.fixture(name='client')
def crons_fixture(web_context):
    return web_context.clients.crons


async def test_ping(client, mockserver):
    @mockserver.json_handler('/crons/ping')
    async def handler(request):
        return web.Response()

    response = await client.ping()

    assert response.status == 200
    assert response.body is None
    assert handler.times_called == 1


async def test_is_enabled(client, mockserver):
    @mockserver.json_handler('/crons/v1/task/something/is-enabled/')
    async def handler(request):
        return web.json_response({'is_enabled': True})

    response = await client.is_enabled(name='something')

    assert response.status == 200
    assert response.body.is_enabled is True
    assert handler.times_called == 1


@pytest.mark.now(DATE)
async def test_lock_acquire(client, mockserver):
    @mockserver.json_handler('/crons/v1/task/something/lock/aquire/')
    def handler(request):
        assert request.json == {
            'owner': 'owner',
            'key': 'key',
            'now': DATE,
            'till': DATE_IN_ONE_DAY,
        }
        return web.Response()

    response = await client.lock_aquire(
        name='something',
        body=models.crons.LockAquireRequest(
            owner='owner',
            key='key',
            now=dates.localize(),
            till=dates.localize() + datetime.timedelta(days=1),
        ),
    )

    assert response.status == 200
    assert response.body is None
    assert handler.times_called == 1


async def test_expected_error(client, mockserver):
    @mockserver.json_handler('/crons/v1/task/something/lock/release/')
    def handler(request):
        assert request.json == {'owner': 'owner', 'key': 'key'}
        return web.json_response({'code': 1, 'success': True}, status=404)

    with pytest.raises(crons_module.LockRelease404) as exc_info:
        await client.lock_release(
            name='something',
            body=models.crons.LockReleaseRequest(owner='owner', key='key'),
        )

    resp = exc_info.value
    assert (
        str(resp) == 'crons response, status: 404, '
        'body: LockResponse4XX(success=True, code=1)'
    )
    assert resp.status == 404
    assert resp.body.code == 1
    assert resp.body.success
    assert handler.times_called == 1


async def test_unexpected_error(client, mockserver):
    @mockserver.json_handler('/crons/ping')
    async def handler(request):
        return web.json_response(status=403)

    exc_class = crons_module.NotDefinedResponse
    with pytest.raises(exc_class) as exc_info:
        await client.ping()

    resp = exc_info.value
    assert (
        str(resp)
        == 'Not defined in schema crons response, status: 403, body: b\'\''
    )
    assert resp.status == 403
    assert resp.body == b''
    assert handler.times_called == 1


async def test_invalid_no_schema(client, mockserver):
    @mockserver.json_handler('/crons/ping')
    async def handler(request):
        return web.json_response({})

    resp = await client.ping()

    assert resp.status == 200
    assert resp.body is None
    assert handler.times_called == 1


async def test_invalid_with_schema(client, mockserver):
    @mockserver.json_handler('/crons/v1/task/something/is-enabled/')
    async def handler(request):
        return web.json_response({'is_enabled': 1})

    exc_class = crons_module.IsEnabledInvalidResponse
    with pytest.raises(exc_class) as exc_info:
        await client.is_enabled(name='something')

    resp = exc_info.value
    assert (
        str(resp) == 'crons invalid response: '
        'Invalid value for is_enabled: 1 is not instance of bool, '
        'status: 200, '
        'body: b\'{"is_enabled": 1}\''
    )
    assert resp.status == 200
    assert json.loads(resp.body) == {'is_enabled': 1}
    assert handler.times_called == 1


async def test_extra_keys(client, mock_crons):
    @mock_crons('/v1/task/something/is-enabled/')
    async def handler(request):
        return web.json_response({'is_enabled': True, 'a': 'b', 'x': [1, 2]})

    response = await client.is_enabled(name='something')

    assert response.status == 200
    assert response.body.is_enabled is True
    assert handler.times_called == 1
