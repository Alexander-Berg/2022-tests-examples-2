# pylint: disable=unused-variable,too-many-statements

import pytest

from libstall.util import time2iso


@pytest.mark.parametrize('status', ('active', 'disabled', 'closed'))
async def test_simple(tap, api, dataset, status):
    with tap.plan(35, 'Список складов'):
        company = await dataset.company()
        store = await dataset.store(status=status, company=company)

        # В статусе, в котором не подгружаются
        await dataset.store(status='agreement', company=company)

        t = await api(token=company.token)

        await t.post_ok('api_external_stores_list', json={'cursor': None})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'Ответ получен')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_has('stores', 'Список присутствует')
        t.json_has('stores.0', 'Элементы есть')
        t.json_has('stores.0.cost_center', store.cost_center)
        t.json_is('stores.0.store_id', store.store_id)
        t.json_is('stores.0.external_id', store.external_id)
        t.json_is('stores.0.cluster_id', store.cluster_id)
        t.json_is('stores.0.company_id', store.company_id)
        t.json_is('stores.0.status', status)
        t.json_is('stores.0.type', store.type)
        t.json_is('stores.0.cluster', store.cluster)
        t.json_is('stores.0.title', store.title)
        t.json_is('stores.0.slug', store.slug)
        t.json_is('stores.0.address', store.address)
        t.json_is('stores.0.location', store.location)
        t.json_is('stores.0.assortment_id', store.assortment_id)
        t.json_is('stores.0.price_list_id', store.price_list_id)
        t.json_is('stores.0.group_id', store.group_id)
        t.json_has('stores.0.timetable')
        t.json_is('stores.0.currency', store.currency)
        t.json_is('stores.0.timezone', store.tz)
        t.json_is('stores.0.source', store.source)
        t.json_is('stores.0.region_id', store.region_id)
        t.json_is('stores.0.open_ts', time2iso(store.open_ts))
        t.json_has('stores.0.ezones')
        t.json_has('stores.0.options.tristero')
        t.json_has('stores.0.attr.telephone')
        t.json_has('stores.0.attr.telegram')
        t.json_has('stores.0.attr.email')
        t.json_has('stores.0.attr.directions')
        t.json_hasnt('stores.0.attr.do_not_show')
        t.json_hasnt('stores.1')


async def test_list_subscribe(tap, api, uuid, dataset):
    with tap.plan(25, 'Тесты на подписку'):
        stores = []
        for _ in range(3):
            store = await dataset.store(
                title='Склад %s' % uuid(),
                status='active',
            )
            tap.ok(store, f'Склад создан в статусе {store.status}')
            stores.append(store)
        for _ in range(3):
            store = await dataset.store(
                title='Склад %s' % uuid(),
                status='disabled',
            )
            tap.ok(store, f'Склад создан в статусе {store.status}')
            stores.append(store)
        for _ in range(4):
            store = await dataset.store(
                title='Склад %s' % uuid(),
                status='agreement',
                price_list_id=uuid(),
                assortment_id=uuid(),
                group_id=uuid(),
                attr={'do_not_show': 'hello'},
            )
            tap.ok(store, f'Склад создан в статусе {store.status}')
            stores.append(store)

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_stores_list',
                        json={'cursor': None, 'subscribe': True})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'Ответ получен')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_has('stores', 'Список присутствует')
        t.json_has('stores.0', 'Элементы есть')

        with tap.subtest(None, 'Дочитываем до конца') as taps:
            t.tap = taps

            while True:
                if not t.res['json']['stores']:
                    break

                cursor = t.res['json']['cursor']
                await t.post_ok('api_external_stores_list',
                                json={'cursor': cursor})
                t.status_is(200, diag=True)
                t.json_is('code', 'OK', 'Ответ получен')
                t.json_has('cursor', 'Курсор присутствует')
                cursor = t.res['json']['cursor']
        t.tap = tap

        t.json_has('cursor', 'Курсор присутствует')

        stores[0].title = uuid()
        store_id = stores[0].store_id
        tap.ok(await stores[0].save(), 'Сохранили один склад')

        await t.post_ok('api_external_stores_list',
                        json={'cursor': cursor})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'Ответ получен')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_has('stores.0', 'Есть склады в ответе')
        tap.ok([s for s in t.res['json']['stores']
                if s['store_id'] == store_id],
               'Изменённый склад есть в выдаче')


@pytest.mark.parametrize('cursor_start', [None, 'abc'])
async def test_list_once(tap, api, uuid, dataset, cursor_start):
    with tap.plan(12):
        stores = []
        for _ in range(5):
            store = await dataset.store(title='Склад %s' % uuid())
            tap.ok(store, 'Склад создан')
            stores.append(store)

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_stores_list',
                        json={'cursor': cursor_start, 'subscribe': False})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ответ получен')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_has('stores', 'Список присутствует')

        with tap.subtest(None, 'Дочитываем до конца') as taps:
            t.tap = taps

            while True:
                if not t.res['json']['stores']:
                    break

                cursor = t.res['json']['cursor']
                if not cursor:
                    break

                await t.post_ok('api_external_stores_list',
                                json={'cursor': cursor})
                t.status_is(200, diag=True)
                t.json_is('code', 'OK', 'ответ получен')
                t.json_has('cursor', 'Курсор присутствует')
        t.tap = tap

        t.json_is('cursor', None, 'Курсор пустой говорит что все забрали')


async def test_list_company(tap, dataset, api):
    with tap.plan(9, 'Получение списка для компании, по ее ключу'):

        company1 = await dataset.company()
        company2 = await dataset.company()
        store1  = await dataset.store(company=company1)
        store2  = await dataset.store(company=company2)

        t = await api(token=company1.token)

        await t.post_ok(
            'api_external_stores_list',
            json={'cursor': None, 'subscribe': True}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ответ получен')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_has('stores', 'Список присутствует')
        t.json_has('stores.0', 'элементы есть')
        t.json_is('stores.0.store_id', store1.store_id)
        t.json_is('stores.0.company_id', company1.company_id)
        t.json_hasnt('stores.1')


async def test_list_no_car(tap, dataset, api):
    with tap.plan(8):
        company = await dataset.company()
        await dataset.store(company=company)

        t = await api(token=company.token)

        await t.post_ok('api_external_stores_list', json={'cursor': None})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'ответ получен')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_has('stores.0', 'элементы есть')
        t.json_hasnt('stores.1')
        t.json_has('stores.0.ezones', 'Есть пустой список зон')
        t.json_hasnt('stores.0.ezones.0', 'Зон нет')
