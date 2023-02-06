import asyncio

from aiohttp import web

from stall.client.falcon import client


async def test_ok(api, tap, ext_api):
    with tap.plan(4, 'Корректный ответ Сокола'):
        async def handle(request):
            tap.eq_ok(
                await request.json(),
                {
                    'erp_supply_id': 'abra',
                    'user': {'login': 'kadabra'},
                },
                'correct query'
            )
            return web.json_response(
                status=200,
                data={'url': 'https://example.com/?token=some-token'})

        async with await ext_api(client, handle):
            t = await api(role='store_admin')

            await t.post_ok('api_admin_falcon_auth',
                            json={'erp_supply_id': 'abra',
                                  'login': 'kadabra'})
            t.status_is(200, diag=True)
            t.json_is('url', 'https://example.com/?token=some-token')


async def test_timeout(api, tap, ext_api, monkeypatch):
    with tap.plan(3, 'Таймаут'):
        # pylint: disable=unused-argument
        async def handle(request):
            await asyncio.sleep(1)
            return web.json_response(
                status=200,
                data={'url': 'https://example.com/?token=some-token'})

        monkeypatch.setattr(client, 'timeout', 0.1)
        async with await ext_api(client, handle):
            t = await api(role='store_admin')
            await t.post_ok('api_admin_falcon_auth',
                            json={'erp_supply_id': 'abra',
                                  'login': 'kadabra'})
            t.status_is(504, diag=True)
            t.json_is('code', 'ER_GATEWAY_TIMEOUT')


async def test_500(api, tap, ext_api):
    with tap.plan(2, 'Сокол отвечает 500'):
        # pylint: disable=unused-argument
        async def handle(request):
            return web.json_response(status=500)

        async with await ext_api(client, handle):
            t = await api(role='store_admin')

            await t.post_ok('api_admin_falcon_auth',
                            json={'erp_supply_id': 'abra',
                                  'login': 'kadabra'})
            t.status_is(500, diag=True)
