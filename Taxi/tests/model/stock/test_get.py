# pylint: disable=too-many-statements


async def test_get(tap, dataset):
    '''Продано'''
    with tap.plan(38):
        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        shelf = await dataset.shelf(store_id=store.store_id)
        tap.ok(shelf, 'полка создана')
        tap.eq(shelf.store_id, store.store_id, 'На складе')

        stock = await dataset.stock(shelf=shelf, count=345)
        tap.ok(stock, f'остаток сгенерирован stock_id={stock.stock_id}')
        tap.eq(stock.count, 345, 'количество')
        tap.eq(stock.reserve, 0, 'резерв')

        order = await dataset.order(store=store)
        tap.ok(order, 'ордер сгенерирован')

        with await stock.do_reserve(order, 123) as stock:
            tap.eq(stock.count, 345, f'count={stock.count}')
            tap.eq(stock.reserve, 123, f'reserve={stock.reserve}')

        with await stock.do_get(order, 5) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 345 - 5, f'count={stock.count}')
            tap.eq(stock.reserve, 123 - 5, f'reserve={stock.reserve}')

        logs = (await stock.list_log()).list
        tap.eq(len(logs), 3, 'Записи лога')

        with logs[-1] as log:
            tap.eq(log.type, 'get', f'log type={log.type}')
            tap.eq(log.count, 345 - 5, f'log count={log.count}')
            tap.eq(log.reserve, 123 - 5, f'log reserve={log.reserve}')
            tap.eq(log.reserves, {order.order_id: log.reserve}, 'резервы')
            tap.eq(log.delta_count, -5,
                   f'log delta_count={log.delta_count}')
            tap.eq(log.delta_reserve, -5,
                   f'log delta_reserve={log.delta_reserve}')
            tap.eq(log.recount, None, 'основная запись')

        with await stock.do_get(order, 17) as stock:
            tap.ok(stock, 'Изменен')
            tap.eq(stock.count, 345 - 17, f'count={stock.count}')
            tap.eq(stock.reserve, 123 - 17, f'reserve={stock.reserve}')

        logs = (await stock.list_log()).list
        tap.eq(len(logs), 5, 'Записи лога')

        with logs[-1] as log:
            tap.eq(log.type, 'get', f'log type={log.type}')
            tap.eq(log.count, 345 - 17, f'log count={log.count}')
            tap.eq(log.reserve, 123 - 17, f'log reserve={log.reserve}')
            tap.eq(log.reserves, {order.order_id: log.reserve}, 'резервы')
            tap.eq(log.delta_count, -17,
                   f'log delta_count={log.delta_count}')
            tap.eq(log.delta_reserve, -17,
                   f'log delta_reserve={log.delta_reserve}')
            tap.eq(log.recount, None, 'основная запись')

        with logs[-2] as log:
            tap.eq(log.type, 'get', f'log type={log.type}')
            tap.eq(log.count, 345, f'log count={log.count}')
            tap.eq(log.reserve, 123, f'log reserve={log.reserve}')
            tap.eq(log.reserves, {order.order_id: log.reserve}, 'резервы')
            tap.eq(log.delta_count, 5,
                   f'log delta_count={log.delta_count}')
            tap.eq(log.delta_reserve, 5,
                   f'log delta_reserve={log.delta_reserve}')
            tap.ok(log.recount, 'корректирующая запись')


async def test_get_full(tap, dataset):
    '''Продано'''
    with tap.plan(27):
        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        shelf = await dataset.shelf(store_id=store.store_id)
        tap.ok(shelf, 'полка создана')
        tap.eq(shelf.store_id, store.store_id, 'На складе')

        stock = await dataset.stock(shelf=shelf, count=345)
        tap.ok(stock, 'остаток сгенерирован')
        tap.eq(stock.count, 345, 'количество')
        tap.eq(stock.reserve, 0, 'резерв')

        order = await dataset.order(store=store)
        tap.ok(order, 'ордер сгенерирован')

        with await stock.do_reserve(order, 345) as stock:
            tap.eq(stock.count, 345, f'count={stock.count}')
            tap.eq(stock.reserve, 345, f'reserve={stock.reserve}')

        with await stock.do_get(order, 345) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 345 - 345, f'count={stock.count}')
            tap.eq(stock.reserve, 345 - 345, f'reserve={stock.reserve}')

        with (await stock.list_log()).list[-1] as log:
            tap.eq(log.type, 'get', f'log type={log.type}')
            tap.eq(log.count, stock.count, f'log count={log.count}')
            tap.eq(log.reserve, stock.reserve, f'log reserve={log.reserve}')

        with await stock.do_get(order, 345) as stock:
            tap.ok(stock, 'Изменен')
            tap.eq(stock.count, 345 - 345, f'count={stock.count}')
            tap.eq(stock.reserve, 345 - 345, f'reserve={stock.reserve}')

        with (await stock.list_log()).list[-1] as log:
            tap.eq(log.type, 'get', f'log type={log.type}')
            tap.eq(log.count, stock.count, f'log count={log.count}')
            tap.eq(log.reserve, stock.reserve, f'log reserve={log.reserve}')

        with await stock.do_get(order, 300) as stock:
            tap.ok(stock, 'Изменен')
            tap.eq(stock.count, 345 - 300, f'count={stock.count}')
            tap.eq(stock.reserve, 345 - 300, f'reserve={stock.reserve}')

        with (await stock.list_log()).list[-1] as log:
            tap.eq(log.type, 'get', f'log type={log.type}')
            tap.eq(log.count, stock.count, f'log count={log.count}')
            tap.eq(log.reserve, stock.reserve, f'log reserve={log.reserve}')
