import asyncio
import datetime as dt

import pytest
import yarl
from aiohttp import web

from libstall.util import now
from libstall.util.token import pack
from stall.client.support_chat_client import client


async def test_get_url(tap, api, cfg):
    chats_url = cfg(f"support_chat.url.{cfg('mode')}").format(lang='ru_ru')

    with tap:
        t = await api(role='admin')

        await t.post_ok('api_support_url', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('url', rf'^{chats_url}\?token=\S+$')


async def test_get_url_no_store(tap, api, dataset):
    with tap:
        user = await dataset.user(store_id=None, role='admin')
        t = await api(user=user)

        await t.post_ok('api_support_url', json={})
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_NO_STORE')
        t.json_is('message', 'No store')


@pytest.mark.parametrize(
    'headers,message',
    [
        [
            {
                'Authorization': 'x',
            },
            "'X-WMS-SupportChatPath' is a required property",
        ],
        [
            {
                'Authorization': 'x',
                'X-WMS-SupportChatPath': '',
            },
            "'' does not match '\\S+'",
        ],
        [
            {
                'X-WMS-SupportChatPath': 'x',
            },
            "'Authorization' is a required property",
        ],
        [
            {
                'Authorization': '',
                'X-WMS-SupportChatPath': 'x',
            },
            "'' does not match '\\S+'",
        ],
    ],
)
async def test_chat_no_header(tap, api, headers, message):
    with tap:
        t = await api()

        await t.post_ok(
            'api_support_chat',
            headers=headers,
            json={'key': 'value'},
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')
        t.json_like('details.errors.0.message', message)

        await t.get_ok('api_support_chat', headers=headers)
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')
        t.json_like('details.errors.0.message', message)


@pytest.mark.parametrize('header', ['x', 'bearer x', 'bearer x.y'])
async def test_invalid_token(tap, api, header):
    with tap:
        t = await api()

        await t.post_ok(
            'api_support_chat',
            json={'key': 'value'},
            headers={'X-WMS-SupportChatPath': '/some/path/',
                     'Authorization': header},
        )
        t.status_is(401, diag=True)
        t.json_is('code', 'ER_AUTH')

        await t.get_ok(
            'api_support_chat',
            headers={'X-WMS-SupportChatPath': '/some/path/',
                     'Authorization': 'x.y'},
        )
        t.status_is(401, diag=True)
        t.json_is('code', 'ER_AUTH')


# pylint: disable=unused-argument
async def test_chat_timeout(tap, api, ext_api, tvm_ticket):
    async def handler(request):
        path = request.path

        if path == '/timeout':
            raise asyncio.TimeoutError('Connection timeout test')

        return web.json_response(status=404)

    with tap:
        async with await ext_api(client, handler):
            chat_token = await get_chat_token(api)

            t = await api()

            await t.post_ok(
                'api_support_chat',
                json={'key': 'value'},
                headers={'X-WMS-SupportChatPath': '/timeout',
                         'Authorization': f'bearer {chat_token}'},
            )
            tap.in_ok(t.res['status'], (502, 504), 'Ошибка')

            await t.get_ok(
                'api_support_chat',
                headers={'X-WMS-SupportChatPath': '/timeout',
                         'Authorization': f'bearer {chat_token}'},
            )
            tap.in_ok(t.res['status'], (502, 504), 'Ошибка')


# pylint: disable=unused-argument
async def test_chat_400(tap, api, ext_api, tvm_ticket):
    async def handler(request):
        path = request.path

        if path == '/400':
            return web.json_response(status=400, data={})

        return web.json_response(status=404, data={})

    with tap:
        async with await ext_api(client, handler):
            chat_token = await get_chat_token(api)

            t = await api()

            await t.post_ok(
                'api_support_chat',
                json={'key': 'value'},
                headers={'X-WMS-SupportChatPath': '/400',
                         'Authorization': f'bearer {chat_token}'},
            )
            t.status_is(400, diag=True)

            await t.get_ok(
                'api_support_chat',
                headers={'X-WMS-SupportChatPath': '/400',
                         'Authorization': f'bearer {chat_token}'},
            )
            t.status_is(400, diag=True)


# pylint: disable=unused-argument
async def test_chat_500(tap, api, ext_api, tvm_ticket):
    async def handler(request):
        path = request.path

        if path == '/500':
            return web.json_response(status=500)

        return web.json_response(status=404)

    with tap:
        async with await ext_api(client, handler):
            chat_token = await get_chat_token(api)

            t = await api()

            await t.post_ok(
                'api_support_chat',
                json={'key': 'value'},
                headers={'X-WMS-SupportChatPath': '/500',
                         'Authorization': f'bearer {chat_token}'},
            )
            t.status_is(500, diag=True)

            await t.get_ok(
                'api_support_chat',
                headers={'X-WMS-SupportChatPath': '/500',
                         'Authorization': f'bearer {chat_token}'},
            )
            t.status_is(500, diag=True)


# pylint: disable=unused-argument
async def test_chat(tap, api, ext_api, tvm_ticket):
    async def handler(request):
        method = request.method.upper()
        path = request.path
        data = await request.read()
        headers = request.headers

        if method == 'POST':
            tap.ok(data, 'POST data is not empty')

        tap.ok(headers.get('X-Taxi-Storage-Id'),
               'X-Taxi-Storage-Id is set')

        tap.ok('X-WMS-SupportChatPath' not in headers,
               'X-WMS-SupportChatPath header removed')

        if method == 'GET' and path == '/chat/1':
            return web.json_response({
                'k1_1': 'v1_1', 'k1_2': 'v1_2'
            }, headers={
                'header1': 'value1',
                'header2': 'value2',
            })

        if method == 'POST' and path == '/chat/1':
            return web.json_response({
                'k2_1': 'v2_1', 'k2_2': 'v2_2'
            }, headers={
                'header1': 'value1',
                'header2': 'value2',
            })

        if method == 'GET' and path == '/chat/2':
            return web.json_response({
                'k3_1': 'v3_1', 'k3_2': 'v3_2'
            }, headers={
                'header1': 'value1',
                'header2': 'value2',
            })

        if method == 'POST' and path == '/chat/2':
            return web.json_response({
                'k4_1': 'v4_1', 'k4_2': 'v4_2'
            }, headers={
                'header1': 'value1',
                'header2': 'value2',
            })

        return web.json_response(status=404)

    with tap:
        async with await ext_api(client, handler):
            chat_token = await get_chat_token(api)

            t = await api()

            await t.post_ok(
                'api_support_chat',
                json={'key': 'value'},
                headers={'X-WMS-SupportChatPath': '/chat/1',
                         'Authorization': f'bearer {chat_token}'},
            )
            t.status_is(200, diag=True)
            t.json_is('k2_1', 'v2_1')
            t.json_is('k2_2', 'v2_2')
            tap.ok('Transfer-Encoding' not in t.res['headers'],
                   'hop-by-hop заголовок Transfer-Encoding отсутствует')

            await t.get_ok(
                'api_support_chat',
                headers={'X-WMS-SupportChatPath': '/chat/1',
                         'Authorization': f'bearer {chat_token}'},
            )
            t.status_is(200, diag=True)
            t.json_is('k1_1', 'v1_1')
            t.json_is('k1_2', 'v1_2')
            tap.ok('Transfer-Encoding' not in t.res['headers'],
                   'hop-by-hop заголовок Transfer-Encoding отсутствует')


async def test_chat_token_expired(tap, api, monkeypatch, cfg):
    with tap:
        chat_token = await get_chat_token(api)

        t = await api()

        def mock_now():
            return now() + dt.timedelta(
                seconds=cfg('support_chat.token_ttl') + 1)

        monkeypatch.setattr('stall.api.support.chat.now', mock_now)

        await t.post_ok(
            'api_support_chat',
            json={'key': 'value'},
            headers={'X-WMS-SupportChatPath': '/some/path1/',
                     'Authorization': f'bearer {chat_token}'},
        )
        t.status_is(401, diag=True)
        t.json_is('code', 'ER_AUTH')

        await t.get_ok(
            'api_support_chat',
            headers={'X-WMS-SupportChatPath': '/some/path1/',
                     'Authorization': f'bearer {chat_token}'},
        )
        t.status_is(401, diag=True)
        t.json_is('code', 'ER_AUTH')


# small but correct PNG file
PNG_FILE = (
    b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A\x00\x00\x00\x0D\x49\x48\x44\x52'
    b'\x00\x00\x01\x00\x00\x00\x01\x00\x01\x03\x00\x00\x00\x66\xBC\x3A'
    b'\x25\x00\x00\x00\x03\x50\x4C\x54\x45\xB5\xD0\xD0\x63\x04\x16\xEA'
    b'\x00\x00\x00\x1F\x49\x44\x41\x54\x68\x81\xED\xC1\x01\x0D\x00\x00'
    b'\x00\xC2\xA0\xF7\x4F\x6D\x0E\x37\xA0\x00\x00\x00\x00\x00\x00\x00'
    b'\x00\xBE\x0D\x21\x00\x00\x01\x9A\x60\xE1\xD5\x00\x00\x00\x00\x49'
    b'\x45\x4E\x44\xAE\x42\x60\x82'
)


# pylint: disable=unused-argument
async def test_chat_attachment(tap, api, ext_api, tvm_ticket):
    async def handler(request):
        method = request.method.upper()
        path = request.path
        data = await request.read()
        headers = request.headers

        tap.ok(data, 'POST data is not empty')

        tap.ok(headers.get('X-Taxi-Storage-Id'),
               'X-Taxi-Storage-Id is set')

        tap.ok('X-WMS-SupportChatPath' not in headers,
               'X-WMS-SupportChatPath header removed')

        if method == 'POST' and path == '/chat/image':
            return web.Response(
                body=PNG_FILE,
                content_type='image/png'
            )

        return web.json_response(status=404)

    with tap:
        async with await ext_api(client, handler):
            chat_token = await get_chat_token(api)

            t = await api()

            await t.post_ok(
                'api_support_chat',
                data=PNG_FILE,
                headers={'X-WMS-SupportChatPath': '/chat/image',
                         'Authorization': f'bearer {chat_token}',
                         'Content-Type': 'image/png'},
            )
            t.status_is(200, diag=True)
            tap.ok('Transfer-Encoding' not in t.res['headers'],
                   'hop-by-hop заголовок Transfer-Encoding отсутствует')


async def test_chat_path_params(tap, api, ext_api, tvm_ticket):
    with tap:
        async def handle(request):
            tap.eq_ok(
                request.params,
                {
                    'services': 'lavka_storages',
                    'status': 'opened%2Cclosed',
                    'start_date': '2021-03-16',
                },
                'query ok'
            )
            return web.json_response(status=404)

        async with await ext_api(client, handle):
            chat_token = await get_chat_token(api)

            t = await api()

            chat_path = '/chat?services=lavka_storages&' \
                        'status=opened%2Cclosed&' \
                        'start_date=2021-03-16'

            await t.post_ok(
                'api_support_chat',
                data=PNG_FILE,
                headers={
                    'X-WMS-SupportChatPath': chat_path,
                    'Authorization': f'bearer {chat_token}',
                    'Content-Type': 'image/png'
                },
            )


async def get_chat_token(api):
    t = await api(role='admin')

    await t.post_ok('api_support_url', json={})
    t.status_is(200, diag=True)
    t.json_is('code', 'OK')
    t.json_has('url')
    url = t.res['json']['url']
    token = yarl.URL(url).query.get('token')

    return token


async def test_chat_company_cluster(tap, api, ext_api, dataset):
    with tap.plan(11, 'company_id, cluster_id, cluster в query params'):
        cluster = await dataset.cluster(title='Москва')
        store = await dataset.store(cluster=cluster)
        user = await dataset.user(store_id=store.store_id,
                                  company_id=store.company_id,
                                  role='admin')

        async def handle(request):
            tap.eq(request.query.get('services'), 'lavka_storages',
                   'services query param')
            tap.eq(request.query.get('status'), 'opened,closed',
                   'status query param')
            tap.eq(request.query.get('start_date'), '2021-03-16',
                   'start_date query param')
            tap.eq(request.query.get('company_id'), store.company_id,
                   'company_id query param')
            tap.eq(request.query.get('cluster_id'), cluster.cluster_id,
                   'cluster_id query param')
            tap.eq(request.query.get('cluster'), cluster.title,
                   'cluster query param')
            return web.json_response(status=200)

        t = await api(user=user)

        await t.post_ok('api_support_url', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('url')
        url = t.res['json']['url']
        chat_token = yarl.URL(url).query.get('token')

        async with await ext_api(client, handle):
            t = await api()

            chat_path = '/chat?services=lavka_storages&' \
                        'status=opened%2Cclosed&' \
                        'start_date=2021-03-16'

            await t.post_ok(
                'api_support_chat',
                data=PNG_FILE,
                headers={
                    'X-WMS-SupportChatPath': chat_path,
                    'Authorization': f'bearer {chat_token}',
                    'Content-Type': 'image/png'
                },
            )


async def test_no_chat_company_cluster(tap, api, ext_api, dataset, cfg):
    with tap.plan(8, 'в токене нет company_id, cluster_id, cluster'):
        cluster = await dataset.cluster(title='Москва')
        store = await dataset.store(cluster=cluster)

        async def handle(request):
            tap.eq(request.headers.get('X-Taxi-Storage-Id'), store.store_id,
                   'X-Taxi-Storage-Id is set')
            tap.eq(request.query.get('services'), 'lavka_storages',
                   'services query param')
            tap.eq(request.query.get('status'), 'opened,closed',
                   'status query param')
            tap.eq(request.query.get('start_date'), '2021-03-16',
                   'start_date query param')
            tap.ok('company_id' not in request.query,
                   'company_id not in query param')
            tap.ok('cluster_id' not in request.query,
                   'cluster_id query param')
            tap.ok('cluster' not in request.query,
                   'cluster query param')
            return web.json_response(status=200)

        chat_token = pack(
            cfg('web.auth.secret'),
            store_id=store.store_id,
            expires=(now() + dt.timedelta(hours=8)).isoformat(),
        )

        async with await ext_api(client, handle):
            t = await api()

            chat_path = '/chat?services=lavka_storages&' \
                        'status=opened%2Cclosed&' \
                        'start_date=2021-03-16'

            await t.post_ok(
                'api_support_chat',
                data=PNG_FILE,
                headers={
                    'X-WMS-SupportChatPath': chat_path,
                    'Authorization': f'bearer {chat_token}',
                    'Content-Type': 'image/png'
                },
            )
