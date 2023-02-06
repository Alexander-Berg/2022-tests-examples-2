import asyncio
import argparse
from aiohttp import web
from stall.client.md_audit import MDAuditClient
from scripts.dev.md_audit_update_stores import md_audit_append_stores


async def test_md_audit_append_stores(tap, dataset, uuid, ext_api):
    requests = []
    external_id1 = uuid()
    external_id2 = uuid()
    id1 = 1234
    id2 = 4321
    args = argparse.Namespace(apply=True, )

    async def handler(request):
        requests.append(request)
        if len(requests) == 1:
            data = [{
                        "id": id1,
                        "active": True,
                        "sap": external_id1,
                        "regionId": 167,
                        "clusterId": 167,
                        "dir": {"login": "name@yandex.ru"}
                },
                {
                    "id": id2,
                    "active": False,
                    "sap": external_id2,
                    "regionId": 167,
                    "clusterId": 167,
                    "dir": {"login": "cat@yandex.ru"}
                }, ]

            return web.json_response(
                data
            )
        if len(requests) == 2:

            return web.json_response(
                [

                ]
            )

    md_audit = MDAuditClient(region='russia')

    with tap.plan(4, 'добаволение vars["md_audit_store"] в store'):
        async with await ext_api(md_audit, handler) as client:
            md_audit = await client.get_all_stores()

        store_1 = await dataset.store(
            external_id=external_id1,
        )
        store_2 = await dataset.store(
            external_id=external_id2,
        )

        await md_audit_append_stores(md_audit, args)

        await store_1.reload()
        await store_2.reload()
        tap.ok(store_1.vars['md_audit_store'],
               'store.vars обновлены полем md_audit')
        tap.ok(store_2.vars['md_audit_store'],
               'store.vars обновлены полем md_audit')
        tap.eq(store_1.vars['md_audit_store']['login'], 'name@yandex.ru',
               'информация верно обновелна')
        tap.eq(store_2.vars['md_audit_store']['login'], 'cat@yandex.ru',
               'информация верно обновелна')


async def test_client_timeout(tap, ext_api):
    with tap.plan(1, 'проверяем выход из md_audit по таймауту'):
        client = MDAuditClient(region='russia')
        client.timeout = 1
        res = 'something'

        async def handler(req):    # pylint: disable=unused-argument
            await asyncio.sleep(100)
            return 1

        async with await ext_api(client, handler) as bad_client:
            res = await bad_client.get_all_stores()
        tap.eq(res, None, 'ответ от сервра не пришел, получаем TimeoutError')
