import asyncio

from stall.client.woody import WoodyClient


async def test_woody_timeout(tap, ext_api, uuid):
    with tap.plan(1, 'проверяем выход из вуди по таймауту'):
        client = WoodyClient(region='fr')
        client.timeout = 1
        res = 'something'

        async def handler(req):  # pylint: disable=unused-argument
            await asyncio.sleep(100)
            return 1

        async with await ext_api(client, handler) as badclient:
            res = await badclient.get_assortment_contractor(uuid(), uuid())

        tap.eq(res, None, 'ответ от сервра не пришел, получаем TimeoutError')
