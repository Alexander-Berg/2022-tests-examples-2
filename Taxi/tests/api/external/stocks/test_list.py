# pylint: disable=too-many-locals,too-many-statements,unused-variable

import pytest


@pytest.mark.parametrize('subscribe', [True, False])
async def test_list_store(tap, dataset, api, subscribe):
    with tap.plan(9, f'{"подписка" if subscribe else "проход"} по складу'):
        stock = await dataset.stock()
        tap.ok(stock, 'остаток создан')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_stocks_list',
                        json={'cursor': None,
                              'subscribe': subscribe,
                              'store_id': stock.store_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stocks.0.stock_id')
        t.json_has('cursor')

        t.json_hasnt('stocks.1')

        t.json_is('stocks.0.stock_id', stock.stock_id)
        t.json_is('stocks.0.shelf_type', stock.shelf_type)


@pytest.mark.parametrize('subscribe', [True, False])
async def test_list_common(tap, dataset, api, subscribe):
    with tap.plan(6, f'{"подписка" if subscribe else "проход"} по складу'):
        stock = await dataset.stock()
        tap.ok(stock, 'остаток создан')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_stocks_list',
                        json={'cursor': None,
                              'subscribe': subscribe})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stocks.0.stock_id')
        t.json_has('cursor')


async def test_list_company(tap, dataset, api):
    with tap.plan(8, 'Список по компании'):

        company1 = await dataset.company()
        company2 = await dataset.company()
        store1  = await dataset.store(company=company1)
        store2  = await dataset.store(company=company2)

        stock1 = await dataset.stock(store=store1)
        stock2 = await dataset.stock(store=store2)

        t = await api(token=company1.token)

        await t.post_ok('api_external_stocks_list', json={'cursor': None})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('stocks.0.stock_id', stock1.stock_id)
        t.json_is('stocks.0.store_id', store1.store_id)
        t.json_is('stocks.0.company_id', company1.company_id)
        t.json_hasnt('stocks.1')


async def test_list_shelf_type(tap, dataset, api):
    with tap.plan(8, 'Список остатков по типу полки'):

        company = await dataset.company()

        store = await dataset.store(company=company)

        stock1 = await dataset.stock(store=store, shelf_type='parcel')
        stock2 = await dataset.stock(store=store, shelf_type='markdown')

        t = await api(token=company.token)

        await t.post_ok('api_external_stocks_list',
                        json={'cursor': None,
                              'shelf_type': 'parcel',
                              'store_id': store.store_id,
                              })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('stocks.0.stock_id', stock1.stock_id)
        t.json_is('stocks.0.store_id', store.store_id)
        t.json_is('stocks.0.shelf_type', stock1.shelf_type)
        t.json_hasnt('stocks.1')


async def test_list_product_id(tap, dataset, api):
    with tap.plan(8, 'Список остатков по продуктам'):

        company = await dataset.company()

        store = await dataset.store(company=company)

        stock1 = await dataset.stock(store=store)
        stock2 = await dataset.stock(store=store)

        t = await api(token=company.token)

        await t.post_ok('api_external_stocks_list',
                        json={'cursor': None,
                              'product_id': stock1.product_id,
                              'store_id': store.store_id,
                              })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('stocks.0.stock_id', stock1.stock_id)
        t.json_is('stocks.0.store_id', store.store_id)
        t.json_is('stocks.0.product_id', stock1.product_id)
        t.json_hasnt('stocks.1')


async def test_no_store_id(tap, dataset, api):
    with tap.plan(3, 'Запрос остатков по типу полки без склада'):

        company = await dataset.company()

        store = await dataset.store(company=company)

        await dataset.stock(store=store,
                            shelf_type='parcel')

        t = await api(token=company.token)

        await t.post_ok('api_external_stocks_list',
                        json={'cursor': None,
                              'shelf_type': 'parcel',
                              })

        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
