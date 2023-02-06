import random

async def test_shipment(tap, dataset, wait_order_status):
    with tap.plan(19):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        shelf = await dataset.shelf(store=store, type='collection')
        tap.eq(shelf.store_id, store.store_id, 'полка создана')
        tap.eq(shelf.type, 'collection', 'тип полки')


        stocks = {}
        with tap.subtest(30, 'Создаём стоки') as taps:
            for i in range(1, 11):
                stock = await dataset.stock(store=store, product=product)
                taps.eq(stock.store_id, store.store_id, 'остаток создан')
                stocks[stock.stock_id] = stock
                taps.eq(len(stocks.keys()), i, f'всего стоков {i}')
                taps.eq(stock.product_id, product.product_id, 'товар')

        stock = await dataset.stock(store=store, shelf=shelf, product=product)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')
        tap.eq(stock.shelf_type, 'collection', 'тип полки')
        tap.eq(stock.shelf_id, shelf.shelf_id, 'id полки')
        tap.eq(stock.product_id, product.product_id, 'товар')


        stock_store = random.choice(list(stocks.values()))
        tap.ok(stock_store, 'Выбран и обычный сток для отгрузки')


        order = await dataset.order(
            type='shipment',
            store=store,
            acks=[user.user_id],
            approved=True,
            required=[
                {
                    'product_id': product.product_id,
                    'count': stock_store.count,
                    'shelf_id': stock_store.shelf_id,
                },
                {
                    'product_id': product.product_id,
                    'count': stock.count,
                    'price_type': 'collection',
                    'shelf_id': stock.shelf_id,
                }
            ]
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')
        await wait_order_status(order, ('processing', 'waiting'))

        stocks = await dataset.Stock.list_by_order(order)
        tap.eq(len(stocks), 2, 'два стока зарезервировано')


        with [s for s in stocks if s.stock_id == stock.stock_id][0] as s:
            tap.eq(
                s.reserves.get(order.order_id),
                stock.count, 'количество резерва на стоке 1')
            tap.eq(s.shelf_type, 'collection', 'тип полки')

        with [s for s in stocks if s.stock_id == stock_store.stock_id][0] as s:
            tap.eq(
                s.reserves.get(order.order_id),
                stock_store.count, 'количество резерва на стоке 2')
            tap.eq(s.shelf_type, 'store', 'тип полки')

        await wait_order_status(order, ('complete', 'done'), user_done=user)
