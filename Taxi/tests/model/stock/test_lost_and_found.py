import pytest


async def test_lost(tap, dataset):
    '''Продано'''
    with tap.plan(15):
        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        shelf = await dataset.shelf(store_id=store.store_id, type='store')
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

        with await stock.do_lost(order, 5) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 345 - 5, f'count={stock.count}')
            tap.eq(stock.reserve, 123 - 5, f'reserve={stock.reserve}')

        with (await stock.list_log()).list[-1] as log:
            tap.eq(log.type, 'lost', f'log type={log.type}')
            tap.eq(log.count, stock.count, f'log count={log.count}')
            tap.eq(log.reserve, stock.reserve, f'log reserve={log.reserve}')


@pytest.mark.parametrize('shelf_type, expected_quants', [
    ('store', 1),
    ('kitchen_components', 101)
])
async def test_found(tap, dataset, shelf_type, expected_quants):
    '''Полка находки.'''
    with tap.plan(16):
        product = await dataset.product(quants=101)
        tap.ok(product, 'продукт сгенерирован')

        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        shelf = await dataset.shelf(store_id=store.store_id, type=shelf_type)
        tap.ok(shelf, 'полка создана')
        tap.eq(shelf.store_id, store.store_id, 'На складе')

        stock = await dataset.stock(shelf=shelf, count=100)
        tap.ok(stock, 'остаток сгенерирован')
        tap.eq(stock.count, 100, 'количество')
        tap.eq(stock.reserve, 0, 'резерв')

        order = await dataset.order(store=store)
        tap.ok(order, 'ордер сгенерирован')

        with await stock.do_found(order, shelf, product, 20) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 20, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')
            tap.eq(stock.quants, expected_quants, f'quants={stock.quants}')

        with (await stock.list_log()).list[-1] as log:
            tap.eq(log.type, 'found', f'log type={log.type}')
            tap.eq(log.count, stock.count, f'log count={log.count}')
            tap.eq(log.reserve, stock.reserve, f'log reserve={log.reserve}')
            tap.eq(log.quants, stock.quants, f'log quants={stock.quants}')
