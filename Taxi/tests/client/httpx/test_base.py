from aiohttp import web

from stall.client.httpx.base import BaseClient


class Client(BaseClient):
    base_params = {'x': '1'}
    base_headers = {'X-LAVKA': '42'}


async def test_req(tap, ext_api):
    with tap.plan(8, 'базовы запросы'):
        requests = []

        async def handler(request):
            request.payload = await request.text()
            requests.append(request)
            return web.json_response('ok')

        async with await ext_api(Client(), handler) as client:
            await client.req()
            tap.eq(requests[-1].method, 'GET', 'дефолтный метод')

            await client.req('post')
            tap.eq(requests[-1].method, 'POST', 'пост метод')

            await client.req('post', '/sosiska/')
            tap.eq(requests[-1].path, '/sosiska/', 'путь')

            await client.req('post', '/sosiska/', params={'y': '2'})
            tap.eq(
                requests[-1].query['x'],
                client.base_params['x'],
                'базовые параметры',
            )
            tap.eq(
                requests[-1].query['y'], '2', 'пололнительные параметры',
            )

            await client.req('post', '/sosiska/', headers={'Y-LAVKA': '2'})
            tap.eq(
                requests[-1].headers['X-LAVKA'],
                client.base_headers['X-LAVKA'],
                'базовые хедеры',
            )
            tap.eq(
                requests[-1].headers['Y-LAVKA'], '2', 'пололнительные хедеры',
            )

            await client.req('post', '/sosiska/', json={'a': 'b'})
            tap.eq(
                requests[-1].payload.replace(' ', ''),
                '{"a":"b"}',
                'джейсон прилетел',
            )
