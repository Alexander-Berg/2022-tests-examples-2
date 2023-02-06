import argparse
import asyncio

from aiohttp import web

from scripts.cron.store_append_md_audit import (
    store_add_md_audit_store,
    main,
    store_add_md_audit_user,
)

from stall.client.md_audit import MDAuditClient, MDAUDITCLIENT_DICT


# pylint: disable=too-many-locals
async def test_append_store_md_audit(tap, dataset, ext_api, uuid):
    # store1 status='active' + круглосуточный
    # store2 некруглосуточный
    external_id1 = uuid()
    external_id2 = uuid()

    requests = []

    async def handler(request):
        requests.append(request)
        if len(requests) == 1:
            data = {
                'id': 111,
                'active': True,
                'sap': external_id1,
                'regionId': 666,
            }
            return web.json_response(data)

        if len(requests) == 2:
            data = {
                'id': 222,
                'active': True,
                'sap': external_id2,
                'regionId': 666,
            }
            return web.json_response(data)

        if len(requests) == 3:
            return web.json_response(
                {}
            )

    md_audit = MDAuditClient(region='russia')

    with tap.plan(2, 'отправляем данные в md_audit, заполяем store.vars'):
        store1 = await dataset.store(
            external_id=external_id1,
            status='active',
            address='address',
            title='title',
            cluster='Таганрог',
            region_id=666,
            location={'lat': 8.0001, 'lon': 4.0001},
            timetable=[{
                'type': 'everyday',
                'begin': '00:00:00',
                'end': '00:00:00',
            }], )

        store2 = await dataset.store(
            external_id=external_id2,
            status='active',
            address='address',
            title='title',
            cluster='Таганрог',
            region_id=666,
            location={'lat': 8.5400, 'lon': 6.0001},
            timetable=[{
                'type': 'everyday',
                'begin': '07:00:00',
                'end': '23:00:00',
            }], )

        async with await ext_api(md_audit, handler) as client:
            md_audit_1 = await client.push_store(store1)
            md_audit_2 = await client.push_store(store2)

        data_1 = await store_add_md_audit_store(store1, md_audit_1)
        data_2 = await store_add_md_audit_store(store2, md_audit_2)

        tap.eq(data_1['sap'], external_id1,
               'правильные значения для md_audit на 1 складе')

        tap.eq(data_2['sap'], external_id2,
               'правильные значения для md_audit на 2 складе')


async def test_append_md_audit_user(tap, dataset, ext_api):
    requests = []

    async def handler(request):
        requests.append(request)
        if len(requests) == 1:
            data = {
                'id': 111,
                'businessDirId': 1234
            }
            return web.json_response(data)

        if len(requests) == 2:
            data = {
                'id': 222,
                'businessDirId': 1234
            }
            return web.json_response(data)

        if len(requests) == 3:
            return web.json_response(
                {}
            )

    md_audit = MDAuditClient(region='russia')

    with tap.plan(2, 'отправляем данные в md_audit, заполяем store.vars'):
        store1 = await dataset.store(
            attr={'email': 'test1@example.com'},
            address='address1',
            vars={'md_audit_store': {'id': 555}}, )

        store2 = await dataset.store(
            attr={'email': 'test2@example.com'},
            address='address2',
            vars={'md_audit_store': {'id': 444}}, )

        async with await ext_api(md_audit, handler) as client:
            md_audit_1 = await client.push_user(store1, data_store=None)
            md_audit_2 = await client.push_user(store2, data_store=None)

        data_1 = await store_add_md_audit_user(store1, md_audit_1)
        data_2 = await store_add_md_audit_user(store2, md_audit_2)

        tap.eq(data_1['id'], 111,
               'правильные значения для md_audit_user на 1 складе')

        tap.eq(data_2['id'], 222,
               'правильные значения для md_audit_user на 2 складе')


async def test_can_not_connect(tap, dataset, ext_api, uuid):
    external_id = uuid()

    # pylint: disable=unused-argument
    async def handler(request):
        headers={'x-error-text': 'не получается соединиться'}
        return web.json_response(status=400, headers=headers)

    md_audit = MDAuditClient(region='russia')

    with tap.plan(1, 'статус при post запросе не равен 200'):
        store = await dataset.store(
            location={'lat': 8.5400, 'lon': 6.0001},
            external_id=external_id,
            cluster='Таганрог',
            region_id=666, )

        async with await ext_api(md_audit, handler) as client:
            md_audit = await client.push_store(store)

        data = await store_add_md_audit_store(store, md_audit)

        tap.eq(data, None, 'изменения не были переданы')


async def test_md_audit_one_store(tap, dataset, ext_api, uuid):
    external_id = uuid()
    company = await dataset.company(
        products_scope=['russia', ])
    store = await dataset.store(
        company_id=company.company_id,
        external_id=external_id,
        status='active',
        address='address',
        title='title',
        cluster='Таганрог',
        region_id=666,
        location={'lat': 8.0001, 'lon': 4.0001},
        timetable=[{
            'type': 'everyday',
            'begin': '00:00:00',
            'end': '00:00:00',
        }],
        attr={'email': 'test@example.com'}
    )
    args = argparse.Namespace(apply=True, store_id=store.store_id,
                              mode='production')

    requests = []

    # pylint: disable=unused-argument
    async def handler(request):
        requests.append(request)
        if len(requests) == 1:
            data = {
                'id': 111,
                'active': True,
                'sap': external_id,
                'regionId': 666, }
            return web.json_response(status=200, data=data)
        if len(requests) == 2:
            data = {
                'id': 222,
                'businessDirId': 1234}
            return web.json_response(status=200, data=data)

    md_audit = MDAUDITCLIENT_DICT['russia']
    with tap.plan(3, 'проверка работы main с мокингом'):
        async with await ext_api(md_audit, handler):
            await main(args=args)
        await store.reload()
        tap.ok(store.vars, 'Vars были обновлены на 1 складе')
        tap.eq(store.vars['md_audit_store']['sap'], external_id,
               'правильные значения для md_audit_store на 1 складе')
        tap.eq(store.vars['md_audit_user']['id'], 222,
               'правильные значения для md_audit_user')


async def test_client_timeout(tap, ext_api, uuid, dataset):
    with tap.plan(1, 'проверяем выход из md_audit по таймауту'):
        external_id = uuid()

        store = await dataset.store(
            location={'lat': 8.5400, 'lon': 6.0001},
            external_id=external_id,
            cluster='Таганрог',
            region_id=666, )

        client = MDAuditClient(region='russia')
        client.timeout = 1
        res = 'something'

        async def handler(req):    # pylint: disable=unused-argument
            await asyncio.sleep(100)
            return 1

        async with await ext_api(client, handler) as bad_client:
            res = await bad_client.push_store(store)
        tap.eq(res, None, 'ответ от сервра не пришел, получаем TimeoutError')

