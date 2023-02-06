# pylint: disable=too-many-statements,unused-variable

import pytest


@pytest.mark.parametrize('subscribe', [True, False, None])
async def test_stores(api, tap, dataset, subscribe):
    with tap.plan(15, 'Запрос остатков сквозняком по всем складам'):
        stock = await dataset.stock()
        tap.ok(stock, 'остаток сгенерирован')

        t = await api(role='token:web.external.tokens.0')

        request = {'cursor': None}
        if subscribe is not None:
            request['subscribe'] = subscribe

        await t.post_ok('api_external_products_stocks', json=request)
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stocks')
        t.json_has('stocks.0.store_id')
        t.json_has('stocks.0.product_id')
        t.json_has('stocks.0.shelf_type')
        t.json_has('stocks.0.count')

        t.json_has('cursor', 'курсор в ответе')

        await t.post_ok('api_external_products_stocks',
                        json={'cursor': t.res['json']['cursor']})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stocks')

        t.json_has('cursor', 'курсор в ответе')


async def test_list_real_1(tap, dataset, uuid, api, now, wait_order_status):
    with tap.plan(33, 'Проверяем как работают списки при КСГ'):

        product1 = await dataset.product(valid=10)
        product2 = await dataset.product()

        store = await dataset.store()
        user = await dataset.user(store=store)

        shelf1 = await dataset.shelf(store=store, type='store', order=1)
        shelf2 = await dataset.shelf(store=store, type='store', order=2)
        await dataset.shelf(store=store, type='trash', order=3)

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok(
            'api_external_products_stocks',
            json={
                'cursor': None,
                'subscribe': True,
                'store_id': store.store_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')

        stocks = t.res['json']['stocks']
        tap.eq(len(stocks), 0, 'Остатков нет')

        await dataset.stock(
            store=store,
            shelf=shelf1,
            product=product1,
            count=100,
            valid='2020-01-01',
            lot=uuid(),
        )
        await dataset.stock(
            store=store,
            shelf=shelf2,
            product=product1,
            count=10,
            valid='2020-01-01',
            lot=uuid(),
        )

        await dataset.stock(
            store=store,
            shelf=shelf2,
            product=product2,
            count=200,
            valid='2020-01-01',
            lot=uuid(),
        )

        await t.post_ok(
            'api_external_products_stocks',
            json={
                'cursor': t.res['json']['cursor'],
                'subscribe': True,
                'store_id': store.store_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')

        stocks = t.res['json']['stocks']
        tap.eq(len(stocks), 2, 'Новые остатки')
        stocks = dict((x['product_id'], x) for x in stocks)

        tap.eq(stocks[product1.product_id]['shelf_type'], 'store', 'shelf_type')
        tap.eq(stocks[product1.product_id]['count'], 110, 'count')

        tap.eq(stocks[product2.product_id]['shelf_type'], 'store', 'shelf_type')
        tap.eq(stocks[product2.product_id]['count'], 200, 'count')

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='reserving',
            estatus='begin',
            target='complete',
            acks=[user.user_id],
            approved=now(),
        )

        await wait_order_status(
            order,
            ('processing', 'reserve_online'),
            user_done=user,
        )
        await wait_order_status(order, ('processing', 'waiting'))

        await t.post_ok(
            'api_external_products_stocks',
            json={
                'cursor': t.res['json']['cursor'],
                'subscribe': True,
                'store_id': store.store_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')

        stocks = t.res['json']['stocks']
        tap.eq(len(stocks), 1, 'Изменившиеся остатки')
        stocks = dict((x['product_id'], x) for x in stocks)

        tap.eq(stocks[product1.product_id]['shelf_type'], 'store', 'shelf_type')
        tap.eq(stocks[product1.product_id]['count'], 0, 'count')

        tap.ok(
            await order.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )

        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user,
        )

        await t.post_ok(
            'api_external_products_stocks',
            json={
                'cursor': t.res['json']['cursor'],
                'subscribe': True,
                'store_id': store.store_id,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')

        stocks = t.res['json']['stocks']
        tap.eq(len(stocks), 1, 'Изменившиеся остатки')
        stocks = dict((x['product_id'], x) for x in stocks)

        tap.eq(stocks[product1.product_id]['shelf_type'], 'store', 'shelf_type')
        tap.eq(stocks[product1.product_id]['count'], 0, 'count')


async def test_no_office(api, tap, dataset):
    with tap.plan(7):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='office')
        stock = await dataset.stock(store_id=store.store_id,
                                    shelf_id=shelf.shelf_id)
        tap.ok(stock, 'остаток сгенерирован')

        t = await api(role='token:web.external.tokens.0')

        await t.post_ok('api_external_products_stocks',
                        json={'store_id': store.store_id,
                              'cursor': None})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stocks')
        t.json_hasnt('stocks.0')
        t.json_has('cursor', 'курсор в ответе')


async def test_list_filters(tap, dataset, uuid, api):
    with tap.plan(29, 'Работа фильтров при получении остатков'):
        product_1 = await dataset.product()
        product_2 = await dataset.product()
        product_3 = await dataset.product()
        product_4 = await dataset.product()

        store = await dataset.store()
        parcel_shelf = await dataset.shelf(store=store, type='parcel')
        store_shelf = await dataset.shelf(store=store, type='store')
        markdown_shelf = await dataset.shelf(store=store, type='markdown')

        await dataset.stock()

        t = await api(role='token:web.external.tokens.0')

        async def get_stocks(filter_value: str) -> set:
            await t.post_ok(
                'api_external_products_stocks',
                json={
                    'cursor': None,
                    'store_id': store.store_id,
                    'filter': filter_value
                }
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            return t.res['json']['stocks']

        stocks = await get_stocks('store')

        tap.eq(stocks, [], 'Нет остатков')

        await dataset.StoreStock.update_kitchen_menu(
            store,
            {
                product_1.product_id: 10
            }
        )
        await dataset.stock(
            store=store,
            shelf=store_shelf,
            product=product_2,
            count=9,
            valid='2020-01-01',
            lot=uuid(),
        )
        await dataset.stock(
            store=store,
            shelf=parcel_shelf,
            product=product_3,
            count=8,
            valid='2020-01-01',
            lot=uuid(),
        )
        await dataset.stock(
            store=store,
            shelf=markdown_shelf,
            product=product_4,
            count=7,
            valid='2020-01-01',
            lot=uuid(),
        )

        stocks = await get_stocks('store')
        tap.eq(
            {stock['shelf_type'] for stock in stocks},
            {'markdown', 'store'},
            'Все полки типов markdown и store'
        )
        tap.eq(
            {stock['product_id'] for stock in stocks},
            {
                product_1.product_id,
                product_2.product_id,
                product_4.product_id
            },
            'Получили все остатки кроме parcel'
        )

        stocks = await get_stocks('parcel')

        tap.eq(
            all(stock['shelf_type'] == 'parcel' for stock in stocks),
            True,
            'Все полки типа parcel'
        )
        tap.eq(
            {stock['product_id'] for stock in stocks},
            {
                product_3.product_id
            },
            'Получили только остатки parcel'
        )

        stocks = await get_stocks('parcel_stocks')
        tap.eq(
            all(stock['shelf_type'] == 'parcel' for stock in stocks),
            True,
            'Все полки типа parcel'
        )
        tap.eq(
            {stock['product_id'] for stock in stocks},
            {
                product_3.product_id
            },
            'Получили только остатки parcel '
            '(фильтры parcel и parcel_stocks эквивалентны)'
        )

        stocks = await get_stocks('store_stocks')
        tap.eq(
            all(stock['shelf_type'] == 'store' for stock in stocks),
            True,
            'Все полки типа store'
        )

        tap.eq(
            {stock['product_id'] for stock in stocks},
            {
                product_1.product_id,
                product_2.product_id
            },
            'Остатки kitchen и store'
        )

        stocks = await get_stocks('markdown_stocks')

        tap.eq(
            all(stock['shelf_type'] == 'markdown' for stock in stocks),
            True,
            'Все полки типа markdown'
        )
        tap.eq(
            {stock['product_id'] for stock in stocks},
            {
                product_4.product_id,
            },
            'Остатки только markdown'
        )


async def test_list_company(tap, dataset, api):
    with tap.plan(10, 'Получение списка стоков для компании, по ее ключу'):

        company1 = await dataset.company()
        company2 = await dataset.company()
        store1  = await dataset.store(company=company1)
        store2  = await dataset.store(company=company2)

        stock = await dataset.stock(store=store1)
        await dataset.stock(store=store2)
        await dataset.stock()

        t = await api(token=company1.token)

        await t.post_ok(
            'api_external_products_stocks',
            json={'cursor': None},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor', 'курсор в ответе')
        t.json_has('stocks')
        t.json_is('stocks.0.store_id', stock.store_id)
        t.json_is('stocks.0.product_id', stock.product_id)
        t.json_is('stocks.0.shelf_type', stock.shelf_type)
        t.json_is('stocks.0.count', stock.count)
        t.json_hasnt('stocks.1')


async def test_list_company_unknown(tap, dataset, api, uuid):
    with tap.plan(5, 'неизвестный идентификатор склада'):

        company1 = await dataset.company()

        t = await api(token=company1.token)

        await t.post_ok(
            'api_external_products_stocks',
            json={'cursor': None, 'store_id': uuid()},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('cursor', None)
        t.json_is('stocks', [])


async def test_list_without_duplicates(tap, dataset, api):
    with tap.plan(8, 'Дубли меню на полке'):
        company = await dataset.company()
        store = await dataset.store(company=company)
        product = await dataset.product()
        await dataset.stock(
            store=store,
            shelf_type='store',
            product_id=product.product_id,
            count=33,
            reserve=1,
        )
        await dataset.StoreStock.update_kitchen_menu(
            store,
            {
                product.product_id: 10
            }
        )
        t = await api(token=company.token)
        await t.post_ok(
            'api_external_products_stocks',
            json={
                'cursor': None,
                'store_id': store.store_id,
                'filter': 'store_stocks',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_isnt('cursor', None)
        t.json_is('stocks.0.product_id', product.product_id, 'Продукт')
        t.json_is('stocks.0.shelf_type', 'store', 'Тип полки')
        t.json_is('stocks.0.count', 42, 'Количество правильное')
        t.json_hasnt('stocks.1')
