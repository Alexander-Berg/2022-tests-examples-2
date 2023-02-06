async def test_sale(tap, dataset):
    '''Продано'''
    with tap.plan(12):
        stock = await dataset.stock(count=345)
        tap.ok(stock, 'остаток сгенерирован')
        tap.eq(stock.count, 345, 'количество')
        tap.eq(stock.reserve, 0, 'резерв')

        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер сгенерирован')

        with await stock.do_reserve(order, 123) as stock:
            tap.eq(stock.count, 345, f'count={stock.count}')
            tap.eq(stock.reserve, 123, f'reserve={stock.reserve}')

        with await stock.do_sale(order, 5) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 345 - 5, f'count={stock.count}')
            tap.eq(stock.reserve, 123 - 5, f'reserve={stock.reserve}')

        with (await stock.list_log()).list[-1] as log:
            tap.eq(log.type, 'sale', f'log type={log.type}')
            tap.eq(log.count, stock.count, f'log count={log.count}')
            tap.eq(log.reserve, stock.reserve, f'log reserve={log.reserve}')


async def test_sale_update(tap, dataset):
    '''Продано'''
    with tap.plan(21):
        stock = await dataset.stock(count=345)
        tap.ok(stock, 'остаток сгенерирован')

        order1 = await dataset.order(store_id=stock.store_id)
        tap.ok(order1, 'ордер 1 сгенерирован')

        with await stock.do_reserve(order1, 123) as stock:
            tap.eq(stock.count, 345, f'count={stock.count}')
            tap.eq(stock.reserve, 123, f'reserve={stock.reserve}')
            tap.eq(
                stock.reserves,
                {order1.order_id: 123},
                'reserves'
            )

        order2 = await dataset.order(store_id=stock.store_id)
        tap.ok(order2, 'ордер 2 сгенерирован')

        with await stock.do_reserve(order2, 57) as stock:
            tap.eq(stock.count, 345, f'count={stock.count}')
            tap.eq(stock.reserve, 123 + 57, f'reserve={stock.reserve}')
            tap.eq(
                stock.reserves,
                {order1.order_id: 123, order2.order_id: 57},
                'reserves'
            )

        with await stock.do_sale(order1, 5) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 345 - 5, f'count={stock.count}')
            tap.eq(stock.reserve, 123 + 57 - 5, f'reserve={stock.reserve}')
            tap.eq(
                stock.reserves,
                {order1.order_id: 123 - 5, order2.order_id: 57},
                'reserves'
            )

        with await stock.do_sale(order2, 15) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 345 - 5 - 15, f'count={stock.count}')
            tap.eq(stock.reserve, 123 + 57 - 5 - 15, f'reserve={stock.reserve}')
            tap.eq(
                stock.reserves,
                {order1.order_id: 123 - 5, order2.order_id: 57 - 15},
                'reserves'
            )

        with await stock.do_sale(order1, 18) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 345 - 18 - 15, f'count={stock.count}')
            tap.eq(
                stock.reserve,
                123 + 57 - 18 - 15,
                f'reserve={stock.reserve}',
            )
            tap.eq(
                stock.reserves,
                {order1.order_id: 123 - 18, order2.order_id: 57 - 15},
                'reserves'
            )


async def test_sale_negative_zero(tap, dataset):
    '''Отрицательная дельта запрещена'''
    with tap.plan(4):
        stock = await dataset.stock(count=345, reserve=123)
        tap.ok(stock, 'остаток сгенерирован')
        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер сгенерирован')

        with tap.raises(AssertionError, 'меньше нуля'):
            await stock.do_sale(order, -5)

        tap.ok(await stock.do_sale(order, 0), 'ноль')


async def test_sale_too_many(tap, dataset):
    '''Берем с полки слишком много'''

    with tap.plan(3):
        stock = await dataset.stock(count=345, reserve=123)
        tap.ok(stock, 'остаток сгенерирован')
        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер сгенерирован')

        tap.eq(await stock.do_sale(order, 346), None, 'слишком много')


async def test_sale_no_reserve(tap, dataset):
    '''Продажа без резервирования невозможна'''
    with tap.plan(3):
        stock = await dataset.stock(count=345, reserve=123)
        tap.ok(stock, 'остаток сгенерирован')
        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер сгенерирован')

        tap.eq(await stock.do_sale(order, 340), None, 'слишком много')
