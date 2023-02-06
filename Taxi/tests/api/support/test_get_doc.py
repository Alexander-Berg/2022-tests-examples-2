from aiohttp import web

from stall.client.get_doc_client import getdocclient


async def test_get_doc(tap, api, ext_api, dataset):
    with tap.plan(5, 'тестируем get_doc'):

        user = await dataset.user(role='admin')
        json = {
            'path': 'somepath',
            'data': {
                'tld': 'ru',
                'doccenterParams': {},
            },
        }

        async def gdoc_handler(req):
            rj = await req.json()
            tap.eq(rj['tld'], 'ru', 'параметры приехали')

            return web.json_response(
                status=200,
                data={
                    'description': 'OK',
                    'doccenterResponse': 'js ==== ?????'
                },
            )

        async with await ext_api(getdocclient, handler=gdoc_handler):
            t = await api(user=user)
            await t.post_ok(
                'api_support_get_doc',
                json=json
            )

            tap.eq_ok(t.res['status'], 200, 'response OK')

            await t.post_ok(
                'api_support_get_doc',
                json={'tld': 'ru'},
            )

            tap.eq_ok(t.res['status'], 400, 'response BAD_REQUEST')
