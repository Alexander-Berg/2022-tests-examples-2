import random


async def test_reserving(tap, dataset):
    with tap.plan(7):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stocks = {}
        with tap.subtest(30, 'Создаём стоки') as taps:
            for i in range(1, 11):
                stock = await dataset.stock(store=store, product=product)
                taps.eq(stock.store_id, store.store_id, 'остаток создан')
                stocks[stock.stock_id] = stock
                taps.eq(len(stocks.keys()), i, f'всего стоков {i}')
                taps.eq(stock.product_id, product.product_id, 'товар')

        stock = list(stocks.values())[random.randrange(len(stocks.values()))]

        order = await dataset.order(
            approved=True,
            type='order',
            acks=[user.user_id],
            required=[
                {
                    'product_id': product.product_id,
                    'count': stock.count,
                    'shelf_id': stock.shelf_id,
                }
            ],
            store=store,
        )

        # pylint: disable=protected-access
        await order.business._reserve_product(
            product_id=product.product_id,
            count=stock.count,
            price_type=stock.shelf_type,
            shelf_id=stock.shelf_id,
        )

        stocks = await dataset.Stock.list_by_order(order)
        tap.eq(len(stocks), 1, 'один сток зарезервирован')
        with stocks[0] as s:
            tap.eq(s.stock_id, stock.stock_id, 'stock_id')
            tap.eq(s.reserves.get(order.order_id),
                   stock.count,
                   'всё зарезервировано для нас')


async def test_reserving_order(tap, dataset, wait_order_status):
    with tap.plan(8):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        stocks = {}
        with tap.subtest(30, 'Создаём стоки') as taps:
            for i in range(1, 11):
                stock = await dataset.stock(store=store, product=product)
                taps.eq(stock.store_id, store.store_id, 'остаток создан')
                stocks[stock.stock_id] = stock
                taps.eq(len(stocks.keys()), i, f'всего стоков {i}')
                taps.eq(stock.product_id, product.product_id, 'товар')

        stock = list(stocks.values())[random.randrange(len(stocks.values()))]

        order = await dataset.order(
            approved=True,
            type='order',
            acks=[user.user_id],
            required=[
                {
                    'product_id': product.product_id,
                    'count': stock.count,
                    'shelf_id': stock.shelf_id,
                }
            ],
            store=store,
        )

        await wait_order_status(order, ('processing', 'begin'))

        stocks = await dataset.Stock.list_by_order(order)
        tap.eq(len(stocks), 1, 'один сток зарезервирован')
        with stocks[0] as s:
            tap.eq(s.stock_id, stock.stock_id, 'stock_id')
            tap.eq(s.reserves.get(order.order_id),
                   stock.count,
                   'всё зарезервировано для нас')
