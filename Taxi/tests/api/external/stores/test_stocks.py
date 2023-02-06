import pytest

# pylint: disable=too-many-statements,unused-variable


@pytest.mark.parametrize('subscribe', [True, False, None])
async def test_stores(api, tap, dataset, subscribe, uuid):
    with tap.plan(38 + (4 if subscribe else 0),
                  'Запрос остатков по одному складу'):
        stock = await dataset.stock()
        tap.ok(stock, 'остаток сгенерирован')

        t = await api(role='token:web.external.tokens.0')

        stock2 = await dataset.stock(store_id=stock.store_id, count=0)
        tap.eq(stock2.store_id, stock.store_id, 'второй сток сгенерирован')
        tap.eq(stock2.count, 0, 'нет в этом стоке количества')

        request = {'cursor': None, 'store_id': stock.store_id}
        if subscribe is not None:
            request['subscribe'] = subscribe

        await t.post_ok('api_external_stores_stocks', json=request)
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stocks')
        t.json_has('stocks.0.store_id')
        t.json_has('stocks.0.product_id')
        t.json_has('stocks.0.shelf_type')
        t.json_has('stocks.0.count')

        t.json_has('stocks.1.store_id')
        t.json_has('stocks.1.product_id')
        t.json_has('stocks.1.shelf_type')
        t.json_has('stocks.1.count')

        t.json_hasnt('stocks.2')

        t.json_has('cursor', 'курсор в ответе')

        stock_other = await dataset.stock()
        tap.ok(stock_other, 'Другой сток сгенерирован')
        tap.ne(stock_other.store_id, stock.store_id, 'На другом складе')

        cursor = t.res['json']['cursor']
        await t.post_ok('api_external_stores_stocks',
                        json={
                            'cursor': cursor,
                            # специально невалидный store_id
                            # в повторном запросе игнор
                            'store_id': uuid(),
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stocks')

        t.json_has('cursor', 'курсор в ответе')
        t.json_hasnt('stocks.0')

        stock2 = await dataset.stock(store_id=stock.store_id)
        tap.eq(stock2.store_id, stock.store_id, 'Ещё сток сгенерирован')

        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер для модификации первого стока сгенерирован')

        tap.ok(await stock.do_put_exists(order, 27),
               'товар на первый сток добавлен')

        await t.post_ok('api_external_stores_stocks',
                        json={
                            'cursor': cursor,
                            # специально невалидный store_id
                            # в повторном запросе игнор
                            'store_id': uuid(),
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stocks')

        t.json_has('cursor', 'курсор в ответе')
        if subscribe:
            t.json_has('stocks.1')
            t.json_hasnt('stocks.2')

            if t.res['json']['stocks'][0]['product_id'] == stock2.product_id:
                f, s = 0, 1
            else:
                f, s = 1, 0

            t.json_is(f'stocks.{f}.store_id', order.store_id)
            t.json_is(f'stocks.{f}.product_id', stock2.product_id)
            t.json_is(f'stocks.{f}.count', stock2.left)
            t.json_is(f'stocks.{s}.store_id', order.store_id)
            t.json_is(f'stocks.{s}.product_id', stock.product_id)
            t.json_is(f'stocks.{s}.shelf_type', stock.shelf_type)
            t.json_is(f'stocks.{s}.count', stock.left)
        else:
            t.json_hasnt('stocks.1')

            t.json_is('stocks.0.store_id', order.store_id)
            t.json_is('stocks.0.product_id', stock2.product_id)
            t.json_is('stocks.0.shelf_type', stock2.shelf_type)
            t.json_is('stocks.0.count', stock2.left)


async def test_list_unknown(tap, api, uuid):
    with tap.plan(3, 'Неизвестные id по умолчанию обрабатываются'):
        # UGLY: т.к. это просто фильтр для списка то получается мы прпускаем
        # в базу любой id даже если у нас его нет

        t = await api(role='token:web.external.tokens.0')

        await t.post_ok(
            'api_external_stores_stocks',
            json={'cursor': None, 'store_id': uuid()},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


async def test_shelf_type(api, tap, dataset):
    with tap.plan(5):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='store')
        stock = await dataset.stock(shelf=shelf)
        shelf1 = await dataset.shelf(store=store, type='markdown')
        stock1 = await dataset.stock(shelf=shelf1)
        shelf2 = await dataset.shelf(store=store, type='trash')
        _ = await dataset.stock(shelf=shelf2)

        t = await api(role='token:web.external.tokens.0')

        request = {'cursor': None, 'store_id': store.store_id}

        await t.post_ok('api_external_stores_stocks', json=request)
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.eq_ok(
            {
                t.res['json']['stocks'][0]['product_id'],
                t.res['json']['stocks'][0]['shelf_type'],
            },
            {
                stock.product_id,
                stock.shelf_type,
            },
            'Correct resp',
        )
        t.json_hasnt('stocks.1')


async def test_no_office(api, tap, dataset):
    with tap.plan(7):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='office')
        stock = await dataset.stock(store_id=store.store_id,
                                    shelf_id=shelf.shelf_id)
        tap.ok(stock, 'остаток сгенерирован')

        t = await api(role='token:web.external.tokens.0')

        await t.post_ok('api_external_stores_stocks',
                        json={'store_id': store.store_id,
                              'cursor': None})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('stocks')
        t.json_hasnt('stocks.0')
        t.json_has('cursor', 'курсор в ответе')


async def test_list_company(tap, dataset, api):
    with tap.plan(10, 'Получение списка для компании, по ее ключу'):

        company1 = await dataset.company()
        company2 = await dataset.company()
        store1  = await dataset.store(company=company1)
        store2  = await dataset.store(company=company2)

        stock1 = await dataset.stock(store=store1)
        stock2 = await dataset.stock(store=store2)

        t = await api(token=company1.token)

        await t.post_ok(
            'api_external_stores_stocks',
            json={'cursor': None, 'store_id': store1.store_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor', 'курсор в ответе')
        t.json_has('stocks')
        t.json_is('stocks.0.store_id', stock1.store_id)
        t.json_is('stocks.0.product_id', stock1.product_id)
        t.json_is('stocks.0.shelf_type', stock1.shelf_type)
        t.json_is('stocks.0.count', stock1.count)
        t.json_hasnt('stocks.1')


async def test_list_company_forbidden(tap, dataset, api):
    with tap.plan(3, 'Нельзя запрашивать не по своему складу'):

        company1 = await dataset.company()
        company2 = await dataset.company()
        store2  = await dataset.store(company=company2)

        t = await api(token=company1.token)

        await t.post_ok(
            'api_external_stores_stocks',
            json={'cursor': None, 'store_id': store2.store_id},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_list_company_unknown(tap, dataset, api, uuid):
    with tap.plan(3, 'неизвестный идентификатор склада'):

        company1 = await dataset.company()

        t = await api(token=company1.token)

        await t.post_ok(
            'api_external_stores_stocks',
            json={'cursor': None, 'store_id': uuid()},
        )
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')


async def test_list_filters(tap, dataset, uuid, api):
    with tap.plan(19, 'Работа фильтров'):
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
                'api_external_stores_stocks',
                json={
                    'cursor': None,
                    'store_id': store.store_id,
                    'filter': filter_value
                }
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            return t.res['json']['stocks']

        stocks = await get_stocks('store_stocks')

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
            'Получили только остатки parcel'
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
            {product.product_id: 10}
        )
        t = await api(token=company.token)
        await t.post_ok(
            'api_external_stores_stocks',
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
