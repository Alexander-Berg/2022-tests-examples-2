import asyncio

from stall.client.onec import client as onec_client


async def test_onec_timeout(tap, ext_api, uuid, cfg):
    with tap.plan(1, 'проверяем выход из onec по таймауту'):
        client = onec_client
        client.timeout = 1
        res = 'something'
        cfg.set('sync.1c.login', 'login')
        cfg.set('sync.1c.password', 12345)

        async def handler(req):  # pylint: disable=unused-argument
            await asyncio.sleep(100)
            return 1

        async with await ext_api(client, handler) as badclient:
            res = await badclient.get_assortment_contractor(uuid(), uuid())
        tap.eq(res, None, 'ответ от сервра не пришел, получаем TimeoutError')
