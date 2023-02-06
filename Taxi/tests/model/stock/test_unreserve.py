from stall.model.stock import Stock


async def test_unreserve(tap, dataset):
    '''Дерезервировать'''
    with tap.plan(12):
        stock = await dataset.stock(count=227)
        tap.ok(stock, 'остаток сгенерирован')
        tap.eq(stock.count, 227, 'количество')
        tap.eq(stock.reserve, 0, 'резерв')

        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, stock.store_id, 'на складе')

        with await stock.do_reserve(order, 123) as stock:
            tap.eq(stock.count, 227, f'count={stock.count}')
            tap.eq(stock.reserve, 123, f'reserve={stock.reserve}')

        with await stock.do_unreserve(order) as stock:
            tap.eq(stock.count, 227, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')

        with (await stock.list_log()).list[-1] as log:
            tap.eq(log.type, 'unreserve', f'log type={log.type}')
            tap.eq(log.count, stock.count, f'log count={log.count}')
            tap.eq(log.reserve, stock.reserve, f'log reserve={log.reserve}')


async def test_unreserve_update(tap, dataset):
    '''Дерезервировать с полки несколько раз'''
    with tap.plan(15):

        stock = await dataset.stock(count=200)
        tap.ok(stock, 'остаток сгенерирован')
        tap.eq(stock.count, 200, 'количество')
        tap.eq(stock.reserve, 0, 'резерв')

        order1 = await dataset.order(store_id=stock.store_id)
        tap.ok(order1, 'ордер 1 создан')

        with await stock.do_reserve(order1, 100) as stock:
            tap.eq(stock.count, 200, f'count={stock.count}')
            tap.eq(stock.reserve, 100, f'reserve={stock.reserve}')

        order2 = await dataset.order(store_id=stock.store_id)
        tap.ok(order2, 'ордер 2 создан')

        with await stock.do_reserve(order2, 50) as stock:
            tap.eq(stock.count, 200, f'count={stock.count}')
            tap.eq(stock.reserve, 100 + 50, f'reserve={stock.reserve}')

        with await stock.do_unreserve(order1) as stock:
            tap.eq(stock.count, 200, f'count={stock.count}')
            tap.eq(stock.reserve, 50, f'reserve={stock.reserve}')

        with await stock.do_unreserve(order2) as stock:
            tap.eq(stock.count, 200, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')

        with await stock.do_unreserve(order1) as stock:
            tap.eq(stock.count, 200, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')


async def test_unreserve_too_many(tap, dataset):
    '''Дерезервировать очень много'''
    with tap.plan(17):
        stock_main = await dataset.stock(count=100)
        with stock_main as stock:
            tap.ok(stock, 'остаток сгенерирован')
            tap.eq(stock.count, 100, 'количество')
            tap.eq(stock.reserve, 0, 'резерв')

            order = await dataset.order(store_id=stock.store_id)
            tap.ok(order, 'ордер создан')
            tap.eq(order.store_id, stock_main.store_id, 'на складе')

        with await stock_main.do_reserve(order, 50) as stock:
            tap.eq(stock.count, 100, f'count={stock.count}')
            tap.eq(stock.reserve, 50, f'reserve={stock.reserve}')

        stock_parallel = await Stock.load(stock_main.stock_id)
        with stock_parallel as stock:
            tap.ok(stock, 'остаток сгенерирован')
            tap.eq(stock.count, 100, 'количество')
            tap.eq(stock.reserve, 50, 'резерв')

        with await stock_parallel.do_unreserve(order) as stock:
            tap.eq(stock.count, 100, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')

        with stock_main as stock:
            tap.ok(stock, 'остаток сгенерирован')
            tap.eq(stock.count, 100, 'количество')
            tap.eq(stock.reserve, 50, 'резерв устарел')

        with await stock_main.do_unreserve(order) as stock:
            tap.eq(stock.count, 100, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')
