from stall.model.stock import Stock


async def test_write_in(tap, dbh, dataset):
    '''Положить на полку'''
    with tap.plan(20):
        product = await dataset.product()
        tap.ok(product, 'продукт сгенерирован')

        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        shelf = await dataset.shelf(store_id=store.store_id, type='incoming')
        tap.ok(shelf, 'полка создана')
        tap.eq(shelf.store_id, store.store_id, 'На складе')

        order = await dataset.order(store_id=store.store_id)
        tap.ok(order, 'заказ создан')

        with await Stock.do_write_in(order, shelf, product, 3) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 3, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')

            tap.eq(stock.product_id, product.product_id, 'product_id')
            tap.eq(stock.store_id, store.store_id, 'store_id')
            tap.eq(stock.shelf_id, shelf.shelf_id, 'shelf_id')

            tap.ok(stock.stock_id, 'id появился')
            tap.eq(len(stock.stock_id), 32 + 4 + 4 + 4, 'длина')
            tap.ok(stock.shardno in range(dbh.nshards('main')),
                   'шард в списке')
            tap.eq(stock.shelf_type, shelf.type, 'тип полки попал в сток')

        with (await stock.list_log()).list[-1] as log:
            tap.eq(log.type, 'write_in', f'log type={log.type}')
            tap.eq(log.count, stock.count, f'log count={log.count}')
            tap.eq(log.reserve, stock.reserve, f'log reserve={log.reserve}')

        with await Stock.load(stock.stock_id) as loaded:
            tap.ok(loaded, 'Загружено')
            tap.eq(loaded.pure_python(), stock.pure_python(), 'значение')


async def test_negative(tap, dataset):
    with tap.plan(16, 'Отрицательный лог во время приема'):

        product = await dataset.product()
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='store')

        order_in    = await dataset.order(store=store, type='acceptance')
        order_sale  = await dataset.order(store=store, type='order')

        with await Stock.do_write_in(order_in, shelf, product, 10) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 10, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')
            tap.eq(stock.shelf_id, shelf.shelf_id, 'shelf_id')

        with await stock.do_reserve(order_sale, 7) as stock:
            tap.ok(stock, 'Зарезервировано')
            tap.eq(stock.count, 10, f'count={stock.count}')
            tap.eq(stock.reserve, 7, f'reserve={stock.reserve}')
            tap.eq(stock.shelf_id, shelf.shelf_id, 'shelf_id')

        with await stock.do_sale(order_sale, 3) as stock:
            tap.ok(stock, 'Продано')
            tap.eq(stock.count, 7, f'count={stock.count}')
            tap.eq(stock.reserve, 4, f'reserve={stock.reserve}')
            tap.eq(stock.shelf_id, shelf.shelf_id, 'shelf_id')

        with await Stock.do_write_in(order_in, shelf, product, 20) as stock:
            tap.ok(stock, 'Корректировка')
            tap.eq(stock.count, 17, f'count={stock.count}')
            tap.eq(stock.reserve, 4, f'reserve={stock.reserve}')
            tap.eq(stock.shelf_id, shelf.shelf_id, 'shelf_id')
