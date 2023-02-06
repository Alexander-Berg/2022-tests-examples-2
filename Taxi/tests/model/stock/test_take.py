async def test_take(tap, dataset):
    '''Взять с полки'''
    with tap.plan(8):
        stock = await dataset.stock()
        tap.ok(stock, 'остаток создан')
        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер создан')

        count = stock.count

        with await stock.do_take(order, 7) as stock:
            tap.ok(stock, 'Товар взят')
            tap.eq(stock.count, count - 7, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')

        with (await stock.list_log()).list[-1] as log:
            tap.eq(log.type, 'take', f'log type={log.type}')
            tap.eq(log.count, stock.count, f'log count={log.count}')
            tap.eq(log.reserve, stock.reserve, f'log reserve={log.reserve}')


async def test_take_too_many(tap, dataset):
    '''Взять с полки очень много'''
    with tap.plan(3):
        stock = await dataset.stock()
        tap.ok(stock, 'остаток создан')
        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер создан')

        count = stock.count
        tap.eq(await stock.do_take(order, count + 1), None, 'не удалось взять')


async def test_take_update(tap, dataset):
    '''Взять с полки несколько раз'''
    with tap.plan(12):

        stock = await dataset.stock(count=300, reserve=100)
        tap.ok(stock, 'остаток создан')

        order1 = await dataset.order(store_id=stock.store_id)
        tap.ok(order1, 'ордер 1 создан')
        order2 = await dataset.order(store_id=stock.store_id)
        tap.ok(order2, 'ордер 2 создан')

        with await stock.do_take(order1, 7) as stock:
            tap.ok(stock, 'Товар взят')
            tap.eq(stock.count, 300 - 7, f'count={stock.count}')
            tap.eq(stock.reserve, 100, f'reserve={stock.reserve}')

        with await stock.do_take(order2, 19) as stock:
            tap.ok(stock, 'Товар взят')
            tap.eq(stock.count, 300 - 7 - 19, f'count={stock.count}')
            tap.eq(stock.reserve, 100, f'reserve={stock.reserve}')

        with await stock.do_take(order1, 5) as stock:
            tap.ok(stock, 'Товар взят ещё раз')
            tap.eq(stock.count, 300 - 5 - 19, f'count={stock.count}')
            tap.eq(stock.reserve, 100, f'reserve={stock.reserve}')


async def test_take_negative_zero(tap, dataset):
    with tap.plan(2, 'Взять с полки очень много'):
        store = await dataset.store()
        stock = await dataset.stock(store=store)
        order = await dataset.order(store=store)

        with tap.raises(AssertionError, 'отрицательное число'):
            await stock.do_take(order, -1)
        with tap.raises(AssertionError, 'нуль'):
            await stock.do_take(order, 0)
