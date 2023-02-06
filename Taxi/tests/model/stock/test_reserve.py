import pytest

from stall.model.stock import Stock


async def test_reserve(tap, dataset):
    '''Зарезервировать'''
    with tap.plan(11):
        stock = await dataset.stock(count=227)
        tap.ok(stock, 'остаток сгенерирован')
        tap.eq(stock.count, 227, 'количество')
        tap.eq(stock.reserve, 0, 'резерв')

        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, stock.store_id, 'на складе')

        lsn = stock.lsn

        with await stock.do_reserve(order, 27) as stock:
            tap.eq(stock.count, 227, f'count={stock.count}')
            tap.eq(stock.reserve, 27, f'reserve={stock.reserve}')
            tap.ok(stock.lsn > lsn, 'lsn увеличился')

        with (await stock.list_log()).list[-1] as log:
            tap.eq(log.type, 'reserve', f'log type={log.type}')
            tap.eq(log.count, stock.count, f'log count={log.count}')
            tap.eq(log.reserve, stock.reserve, f'log reserve={log.reserve}')


async def test_reserve_condition(tap, dataset):
    '''Зарезервировать с условием'''
    with tap.plan(13):
        stock = await dataset.stock(count=227)
        tap.ok(stock, 'остаток сгенерирован')
        tap.eq(stock.count, 227, 'количество')
        tap.eq(stock.reserve, 0, 'резерв')

        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, stock.store_id, 'на складе')

        lsn = stock.lsn

        with await stock.do_reserve(order, 27, conditions=[
                ('lsn', '=', lsn),
        ]) as stock:
            tap.eq(stock.count, 227, f'count={stock.count}')
            tap.eq(stock.reserve, 27, f'reserve={stock.reserve}')
            tap.ok(stock.lsn > lsn, 'lsn увеличился')

        lsn = stock.lsn
        res = await stock.do_reserve(
            order,
            27,
            conditions=[
                ('lsn', '=', lsn - 1),
            ]
        )
        tap.eq(res, None, 'Не сработал condition')
        tap.ok(await stock.reload(), 'перегружен')
        tap.eq(stock.count, 227, f'count={stock.count}')
        tap.eq(stock.reserve, 27, f'reserve={stock.reserve}')
        tap.eq(stock.lsn, lsn, 'lsn не менялся')


@pytest.mark.parametrize(
    'counts',
    [   # кол, рез, зк1, зк2, зк1
        ((123, 0),   25, 23,   25, 'Резервируем от нуля число'),
        ((123, 0),   25, 23,    0, 'Резервируем от нуля число в ноль'),
        ((123, 10),  25, 23,   25, 'Резервируем от нуля число'),
        ((123, 10),  0,  23,    0, 'Резервируем от нуля ноль в число'),
    ]
)
async def test_reserve_update(tap, dataset, counts):
    with tap.plan(11, counts[-1]):

        stock = await dataset.stock(count=counts[0][0], reserve=counts[0][1])
        tap.ok(stock, 'остаток сгенерирован')
        tap.eq(stock.count,
               counts[0][0],
               f'начальное количество {counts[0][0]}')
        tap.eq(stock.reserve,
               counts[0][1],
               f'начальный резерв {counts[0][1]}')

        order1 = await dataset.order(store_id=stock.store_id)
        tap.ok(order1, 'ордер 1 создан')

        order2 = await dataset.order(store_id=stock.store_id)
        tap.ok(order2, 'ордер 2 создан')

        with await stock.do_reserve(order1, counts[1]) as stock:
            tap.eq(stock.count, counts[0][0],
                   f'количество {counts[0][0]} => count={stock.count}')
            tap.eq(stock.reserve,
                   counts[0][1] + counts[1],
                   f'резервировали {counts[0][1]} => {stock.reserve}')

        with await stock.do_reserve(order2, counts[2]) as stock:
            tap.eq(stock.count, counts[0][0], f'count={stock.count}')
            tap.eq(stock.reserve,
                   counts[0][1] + sum(counts[1:3]),
                   f'reserve={stock.reserve}')

        with await stock.do_reserve(order1, counts[3]) as stock:
            tap.eq(stock.count, counts[0][0], f'count={stock.count}')
            tap.eq(stock.reserve,
                   counts[0][1] + sum(counts[2:4]),
                   f'reserve={stock.reserve}')


async def test_reserve_negative(tap, dataset):
    with tap.plan(3, 'попытка зарезервировать отр значение'):
        stock = await dataset.stock(count=227)
        tap.ok(stock, 'остаток сгенерирован')

        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер создан')

        with tap.raises(AssertionError, 'отрицательный резерв'):
            await stock.do_reserve(order, -27)


async def test_reserve_too_many(tap, dataset):
    '''Зарезервировать'''
    with tap.plan(6):
        stock = await dataset.stock(count=227)
        tap.ok(stock, 'остаток сгенерирован')
        tap.eq(stock.count, 227, 'количество')
        tap.eq(stock.reserve, 0, 'резерв')

        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, stock.store_id, 'на складе')

        tap.ok(not await stock.do_reserve(order, 827), 'слишком много резерва')


async def test_reserve_other_order(tap, dataset):
    '''Зарезервировать'''
    with tap.plan(23):
        stock = await dataset.stock(count=227)
        tap.ok(stock, 'остаток сгенерирован')
        tap.eq(stock.count, 227, 'количество')
        tap.eq(stock.reserve, 0, 'резерв')

        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, stock.store_id, 'на складе')

        order2 = await dataset.order(store_id=stock.store_id)
        tap.ok(order2, 'второй ордер создан')
        tap.eq(order2.store_id, stock.store_id, 'на складе')

        with await stock.do_reserve(order2, 15) as stock:
            tap.eq(stock.count, 227, f'count={stock.count}')
            tap.eq(stock.reserve, 15, f'reserve={stock.reserve}')

        reserve2 = await Stock.list_by_order(order2)
        tap.ok(reserve2, 'Резервы ордера получены')
        tap.isa_ok(reserve2, list, 'тип')
        tap.eq(len(reserve2), 1, 'Один резерв')
        tap.eq(reserve2[0].reserves[order2.order_id], 15, 'Штук')

        with await stock.do_reserve(order, 27) as stock:
            tap.eq(stock.count, 227, f'count={stock.count}')
            tap.eq(stock.reserve, 27+15, f'reserve={stock.reserve}')

        reserve = await Stock.list_by_order(order)
        tap.ok(reserve, 'Резервы ордера получены')
        tap.isa_ok(reserve, list, 'тип')
        tap.eq(len(reserve), 1, 'Один резерв')
        tap.eq(reserve[0].reserves[order.order_id], 27, 'Штук')

        reserve2_repeat = await Stock.list_by_order(order2)
        tap.ok(reserve2_repeat, 'Резервы ордера получены')
        tap.isa_ok(reserve2_repeat, list, 'тип')
        tap.eq(len(reserve2_repeat), 1, 'Один резерв')
        tap.eq(reserve2_repeat[0].reserves[order2.order_id], 15, 'Штук')


async def test_reserve_many(tap, dataset):
    '''Зарезервировать последовательно несколько раз'''
    with tap.plan(16):
        stock = await dataset.stock(count=200)
        tap.ok(stock, 'остаток сгенерирован')
        tap.eq(stock.count, 200, 'количество')
        tap.eq(stock.reserve, 0, 'резерв')

        order = await dataset.order(store_id=stock.store_id)
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, stock.store_id, 'на складе')

        with await stock.do_reserve(order, 20) as stock:
            tap.eq(stock.count, 200, f'count={stock.count}')
            tap.eq(stock.reserve, 20, f'reserve={stock.reserve}')

        with await stock.do_reserve(order, 2) as stock:
            tap.eq(stock.count, 200, f'count={stock.count}')
            tap.eq(stock.reserve, 2, f'reserve={stock.reserve}')

        with await stock.do_reserve(order, 24) as stock:
            tap.eq(stock.count, 200, f'count={stock.count}')
            tap.eq(stock.reserve, 24, f'reserve={stock.reserve}')

        tap.eq(await stock.do_reserve(order, 201), None, 'Нельзя')
        tap.eq(stock.count, 200, f'count={stock.count}')
        tap.eq(stock.reserve, 24, f'reserve={stock.reserve}')

        with await stock.do_reserve(order, 0) as stock:
            tap.eq(stock.count, 200, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')


async def test_reserve_drop(tap, dataset):
    '''Разрезервирование после создания с резервированием'''
    with tap.plan(7):
        store = await dataset.store()

        order = await dataset.order(store=store)
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, store.store_id, 'на складе')

        stock = await dataset.stock(
            store=store, order=order, count=100, reserve=100)
        tap.ok(stock, 'остаток сгенерирован')
        tap.eq(stock.count, 100, 'количество')
        tap.eq(stock.reserve, 100, 'резерв')

        # Новый тип операции не влияет на предыдущую
        with await stock.do_reserve(order, 0) as stock:
            tap.eq(stock.count, 100, f'count={stock.count}')
            tap.eq(stock.reserve, 100, f'reserve={stock.reserve}')


async def test_reserve_drop_sale(tap, dataset):
    '''Разрезервирование после создания с резервированием'''
    with tap.plan(11):
        store = await dataset.store()

        order = await dataset.order(store=store)
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, store.store_id, 'на складе')

        stock = await dataset.stock(store=store, order=order, count=100)
        tap.ok(stock, 'остаток сгенерирован')
        tap.eq(stock.count, 100, 'количество')
        tap.eq(stock.reserve, 0, 'резерв')

        with await stock.do_reserve(order, 50) as stock:
            tap.eq(stock.count, 100, f'count={stock.count}')
            tap.eq(stock.reserve, 50, f'reserve={stock.reserve}')

        with await stock.do_sale(order, 49) as stock:
            tap.eq(stock.count, 51, f'count={stock.count}')
            tap.eq(stock.reserve, 1, f'reserve={stock.reserve}')

        # Новый тип операции не влияет на предыдущую
        with await stock.do_reserve(order, 0) as stock:
            tap.eq(stock.count, 51, f'count={stock.count}')
            tap.eq(stock.reserve, 1, f'reserve={stock.reserve}')
