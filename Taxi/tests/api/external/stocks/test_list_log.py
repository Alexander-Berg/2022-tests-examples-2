# pylint: disable=unused-variable

import pytest


@pytest.mark.parametrize('subscribe', [True, False])
async def test_list_store(tap, dataset, api, subscribe):
    with tap.plan(9, f'{"подписка" if subscribe else "проход"} по складу'):
        stock = await dataset.stock()
        tap.ok(stock, 'остаток создан')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_stocks_log',
                        json={'cursor': None,
                              'subscribe': subscribe,
                              'store_id': stock.store_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stocks_log.0.stock_id')
        t.json_has('cursor')

        t.json_hasnt('stocks_log.1')

        t.json_is('stocks_log.0.stock_id', stock.stock_id)
        t.json_is('stocks_log.0.shelf_type', stock.shelf_type)


@pytest.mark.parametrize('subscribe', [True, False])
async def test_list_order(tap, dataset, api, subscribe):
    with tap.plan(6, f'{"подписка" if subscribe else "проход"} по заказу'):

        order1 = await dataset.order()
        order2 = await dataset.order()

        stock1 = await dataset.stock(order=order1)
        stock2 = await dataset.stock(order=order2)

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_stocks_log',
                        json={'cursor': None,
                              'subscribe': subscribe,
                              'order_id': order1.order_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')

        t.json_is('stocks_log.0.stock_id', stock1.stock_id)

        t.json_hasnt('stocks_log.1')


@pytest.mark.parametrize('subscribe', [True, False])
async def test_list_common(tap, dataset, api, subscribe):
    with tap.plan(6, f'{"подписка" if subscribe else "проход"} по складу'):
        stock = await dataset.stock()
        tap.ok(stock, 'остаток создан')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_stocks_log',
                        json={'cursor': None,
                              'subscribe': subscribe})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stocks_log.0.stock_id')
        t.json_has('cursor')


@pytest.mark.parametrize('subscribe', [True, False])
async def test_list_company(tap, dataset, api, subscribe):
    with tap.plan(8, 'Список по компании'):

        company1 = await dataset.company()
        company2 = await dataset.company()
        store1  = await dataset.store(company=company1)
        store2  = await dataset.store(company=company2)

        stock1 = await dataset.stock(store=store1)
        stock2 = await dataset.stock(store=store2)

        t = await api(token=company1.token)

        await t.post_ok(
            'api_external_stocks_log',
            json={
                'subscribe': subscribe,
                'cursor': None
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('stocks_log.0.stock_id', stock1.stock_id)
        t.json_is('stocks_log.0.store_id', store1.store_id)
        t.json_is('stocks_log.0.company_id', company1.company_id)
        t.json_hasnt('stocks_log.1')


@pytest.mark.parametrize('subscribe', [True, False])
async def test_list_store_company(tap, dataset, api, subscribe):
    with tap.plan(8, 'Список по компании для конкретного склада'):

        company = await dataset.company()
        store1  = await dataset.store(company=company)
        store2  = await dataset.store(company=company)

        stock1 = await dataset.stock(store=store1)
        stock2 = await dataset.stock(store=store2)

        t = await api(token=company.token)

        await t.post_ok(
            'api_external_stocks_log', json={
                'store_id': store1.store_id,
                'subscribe': subscribe,
                'cursor': None,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('stocks_log.0.stock_id', stock1.stock_id)
        t.json_is('stocks_log.0.store_id', store1.store_id)
        t.json_is('stocks_log.0.company_id', company.company_id)
        t.json_hasnt('stocks_log.1')
