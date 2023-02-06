async def test_put_exists(tap, dataset):
    with tap.plan(9, 'Доложить на полку'):
        stock = await dataset.stock()
        tap.ok(stock, 'остаток создан')
        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер создан')

        count = stock.count
        lsn = stock.lsn

        with await stock.do_put_exists(order, 7) as stock:
            tap.ok(stock, 'Товар взят')
            tap.eq(stock.count, count + 7, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')
            tap.ok(lsn < stock.lsn, 'lsn увеличился')

        with (await stock.list_log()).list[-1] as log:
            tap.eq(log.type, 'put', f'log type={log.type}')
            tap.eq(log.count, stock.count, f'log count={log.count}')
            tap.eq(log.reserve, stock.reserve, f'log reserve={log.reserve}')


async def test_put_exists_update(tap, dataset):
    with tap.plan(19, 'Доложить на полку несколько раз'):

        stock = await dataset.stock(count=300, reserve=100)
        tap.ok(stock, 'остаток создан')

        order1 = await dataset.order(store_id=stock.store_id)
        tap.ok(order1, 'ордер 1 создан')
        order2 = await dataset.order(store_id=stock.store_id)
        tap.ok(order2, 'ордер 2 создан')

        lsn = stock.lsn

        with await stock.do_put_exists(order1, 7) as stock:
            tap.ok(stock, 'Товар взят')
            tap.eq(stock.count, 300 + 7, f'count={stock.count}')
            tap.eq(stock.reserve, 100, f'reserve={stock.reserve}')
            tap.ok(lsn < stock.lsn, 'lsn увеличился')
            lsn = stock.lsn

        with await stock.do_put_exists(order2, 19) as stock:
            tap.ok(stock, 'Товар взят')
            tap.eq(stock.count, 300 + 7 + 19, f'count={stock.count}')
            tap.eq(stock.reserve, 100, f'reserve={stock.reserve}')
            tap.ok(lsn < stock.lsn, 'lsn увеличился')
            lsn = stock.lsn

        with await stock.do_put_exists(order1, 5) as stock:
            tap.ok(stock, 'Товар взят ещё раз')
            tap.eq(stock.count, 300 + 5 + 19, f'count={stock.count}')
            tap.eq(stock.reserve, 100, f'reserve={stock.reserve}')
            tap.ok(lsn < stock.lsn, 'lsn увеличился')
            lsn = stock.lsn

        with await stock.do_put_exists(order1, 8, reserve=7) as stock:
            tap.ok(stock, 'Товар взят ещё раз')
            tap.eq(stock.count, 300 + 8 + 19, f'count={stock.count}')
            tap.eq(stock.reserve, 107, f'reserve={stock.reserve}')
            tap.ok(lsn < stock.lsn, 'lsn увеличился')
            lsn = stock.lsn


async def test_put_exists_negative_zero(tap, dataset):
    with tap.plan(3, 'Отрицательные числа'):
        stock = await dataset.stock()
        tap.ok(stock, 'остаток создан')
        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер создан')

        with tap.raises(AssertionError, 'отрицательное число'):
            await stock.do_put_exists(order, -1)


async def test_put_more(tap, dataset):
    '''Разрезервирование после создания с резервированием'''
    with tap.plan(9):
        store = await dataset.store()

        order = await dataset.order(store=store)
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, store.store_id, 'на складе')

        stock = await dataset.stock(store=store, order=order, count=100)
        tap.ok(stock, 'остаток сгенерирован')
        tap.eq(stock.count, 100, 'количество')
        tap.eq(stock.reserve, 0, 'резерв')

        with await stock.do_take(order, 50) as stock:
            tap.eq(stock.count, 50, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')

        with await stock.do_put_exists(order, 55) as stock:
            tap.eq(stock.count, 105, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')
