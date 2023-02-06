from aiohttp import web

from stall.client.onec import client as onec_client
from stall.client.true_client import TrueClient


async def test_happy_flow(tap, dataset, ext_api, uuid):
    with tap.plan(1, 'проверяем что если все хорошо то все хорошо'):
        cid = uuid()
        true_client = TrueClient(cid)
        await dataset.stash(
            name=f'true_mark_token_1c_{cid}',
            value={'true_mark_token': 'lalala'},
        )

        async def handler(req):
            assert req.headers['Authorization'] == 'Bearer lalala', 'токен тот'
            return web.json_response(status=200)

        async with await ext_api(true_client, handler):
            res = await true_client.get_info_about_product('some_id')

        tap.eq(res.status, 200, 'статус 200')


async def test_wrong_token(tap, ext_api, uuid, cfg):
    with tap.plan(4, 'проверяем что токен обновляется на верный'):
        cfg.set('sync.1c.login', 'admin')
        cfg.set('sync.1c.password', 'admin')
        cfg.set('sync.1c.update_true_token_timeout', 0)

        cid = uuid()
        true_client = TrueClient(cid)
        some_token = 'lalala'
        some_token2 = 'lalala'

        async def onec_handler(req):  # pylint: disable=unused-argument
            return web.json_response(
                status=200,
                data={'token': some_token},
            )

        async def true_mark_handler(req):
            if req.headers['Authorization'] != f'Bearer {some_token2}':
                return web.json_response(status=401)
            return web.json_response(status=200)

        for i in range(3):
            async with await ext_api(onec_client, onec_handler):
                async with await ext_api(true_client, true_mark_handler):
                    res = await true_client.get_info_about_product('some_id')

            tap.eq(res.status, 200, 'статус 200')

            true_client.true_token = 'lala'
            if i == 1:
                some_token = 'la'
                some_token2 = 'la'

        some_token = uuid()
        async with await ext_api(onec_client, onec_handler):
            async with await ext_api(true_client, true_mark_handler):
                res = await true_client.get_info_about_product('some_id')

        tap.ok(not res, 'все сломалось')
