async def test_write_off(tap, dataset):
    '''Продано'''
    with tap.plan(15):
        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        shelf = await dataset.shelf(store_id=store.store_id, type='trash')
        tap.ok(shelf, 'полка создана')
        tap.eq(shelf.store_id, store.store_id, 'На складе')

        stock = await dataset.stock(shelf=shelf, count=345)
        tap.ok(stock, 'остаток сгенерирован')
        tap.eq(stock.count, 345, 'количество')
        tap.eq(stock.reserve, 0, 'резерв')

        order = await dataset.order(store=store)
        tap.ok(order, 'ордер сгенерирован')

        with await stock.do_reserve(order, 123) as stock:
            tap.eq(stock.count, 345, f'count={stock.count}')
            tap.eq(stock.reserve, 123, f'reserve={stock.reserve}')

        with await stock.do_write_off(order, 5) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 345 - 5, f'count={stock.count}')
            tap.eq(stock.reserve, 123 - 5, f'reserve={stock.reserve}')

        with (await stock.list_log()).list[-1] as log:
            tap.eq(log.type, 'write_off', f'log type={log.type}')
            tap.eq(log.count, stock.count, f'log count={log.count}')
            tap.eq(log.reserve, stock.reserve, f'log reserve={log.reserve}')
