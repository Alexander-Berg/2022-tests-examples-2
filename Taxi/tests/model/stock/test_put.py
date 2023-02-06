# pylint: disable=too-many-statements

import pytest

from stall.model.stock import Stock


async def test_put_load(tap, dbh, dataset):
    '''Положить на полку'''
    with tap.plan(27):
        product = await dataset.product()
        tap.ok(product, 'продукт сгенерирован')

        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        shelf = await dataset.shelf(store_id=store.store_id)
        tap.ok(shelf, 'полка создана')
        tap.eq(shelf.store_id, store.store_id, 'На складе')

        order = await dataset.order(store_id=store.store_id)
        tap.ok(order, 'заказ создан')

        with await Stock.do_put(order, shelf, product, 3) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 3, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')

            tap.eq(stock.product_id, product.product_id, 'product_id')
            tap.eq(stock.quants, 1, 'quants')
            tap.eq(stock.company_id, store.company_id, 'company_id')
            tap.eq(stock.store_id, store.store_id, 'store_id')
            tap.eq(stock.shelf_id, shelf.shelf_id, 'shelf_id')

            tap.ok(stock.stock_id, 'id появился')
            tap.eq(len(stock.stock_id), 32 + 4 + 4 + 4, 'длина')
            tap.ok(stock.shardno in range(dbh.nshards('main')),
                   'шард в списке')
            tap.eq(stock.shelf_type, shelf.type, 'тип полки попал в сток')

        logs = (await stock.list_log()).list
        tap.eq(len(logs), 1, 'Только основная запись')

        with logs[-1] as log:
            tap.eq(log.type, 'put', f'log type={log.type}')
            tap.eq(log.count, 3, f'log count={log.count}')
            tap.eq(log.reserve, 0, f'log reserve={log.reserve}')
            tap.eq(log.delta_count, 3, f'log delta_count={log.delta_count}')
            tap.eq(log.delta_reserve, 0,
                   f'log delta_reserve={log.delta_reserve}')
            tap.eq(log.recount, None, 'основная запись')
            tap.eq(log.quants, 1, 'дефолтный квант')

        with await Stock.load(stock.stock_id) as loaded:
            tap.ok(loaded, 'Загружено')
            tap.eq(loaded.pure_python(), stock.pure_python(), 'значение')


async def test_put_update(tap, dataset):
    '''Положить на полку'''
    with tap.plan(62):

        product = await dataset.product()
        tap.ok(product, 'продукт сгенерирован')

        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        shelf = await dataset.shelf(store_id=store.store_id)
        tap.ok(shelf, 'полка создана')
        tap.eq(shelf.store_id, store.store_id, 'На складе')

        order = await dataset.order(store_id=store.store_id)
        tap.ok(order, 'заказ создан')

        with await Stock.do_put(order, shelf, product, 3) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 3, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')
            stock_id = stock.stock_id
            lsn = stock.lsn

            logs = (await stock.list_log()).list
            tap.eq(len(logs), 1, 'Записи лога')

            with logs[-1] as log:
                tap.eq(log.type, 'put', f'log type={log.type}')
                tap.eq(log.count, 3, f'log count={log.count}')
                tap.eq(log.reserve, 0, f'log reserve={log.reserve}')
                tap.eq(log.reserves, {}, 'резервы')
                tap.eq(log.delta_count, 3, f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, 0,
                       f'log delta_reserve={log.delta_reserve}')
                tap.eq(log.recount, None, 'основная запись')

        with await Stock.do_put(order, shelf, product, 2) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 2, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')
            tap.eq(stock.stock_id, stock_id, 'stock_id')
            tap.ok(stock.lsn > lsn, 'lsn проинкрементился')
            lsn = stock.lsn

            logs = (await stock.list_log()).list
            tap.eq(len(logs), 3, 'Записи лога')

            with logs[-1] as log:
                tap.eq(log.type, 'put', f'log type={log.type}')
                tap.eq(log.count, 2, f'log count={log.count}')
                tap.eq(log.reserve, 0, f'log reserve={log.reserve}')
                tap.eq(log.reserves, {}, 'резервы')
                tap.eq(log.delta_count, 2, f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, 0,
                       f'log delta_reserve={log.delta_reserve}')
                tap.eq(log.recount, None, 'основная запись')
            with logs[-2] as log:
                tap.eq(log.type, 'put', f'log type={log.type}')
                tap.eq(log.count, 0, f'log count={log.count}')
                tap.eq(log.reserve, 0, f'log reserve={log.reserve}')
                tap.eq(log.reserves, {}, 'резервы')
                tap.eq(log.delta_count, -3,
                       f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, 0,
                       f'log delta_reserve={log.delta_reserve}')
                tap.ok(log.recount, 'корректирующая запись')

        with await Stock.do_put(order, shelf, product, 2) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 2, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')
            tap.eq(stock.stock_id, stock_id, 'stock_id')
            tap.ok(stock.lsn > lsn, 'lsn проинкрементился')
            lsn = stock.lsn

            logs = (await stock.list_log()).list
            tap.eq(len(logs), 3, 'Записи лога')

        with await Stock.do_put(order, shelf, product, 10) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 10, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')
            tap.eq(stock.stock_id, stock_id, 'stock_id')
            tap.ok(stock.lsn > lsn, 'lsn проинкрементился')

            logs = (await stock.list_log()).list
            tap.eq(len(logs), 5, 'Записи лога')

            with logs[-1] as log:
                tap.eq(log.type, 'put', f'log type={log.type}')
                tap.eq(log.count, 10, f'log count={log.count}')
                tap.eq(log.reserve, 0, f'log reserve={log.reserve}')
                tap.eq(log.reserves, {}, 'резервы')
                tap.eq(log.delta_count, 10,
                       f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, 0,
                       f'log delta_reserve={log.delta_reserve}')
                tap.eq(log.recount, None, 'основная запись')
            with logs[-2] as log:
                tap.eq(log.type, 'put', f'log type={log.type}')
                tap.eq(log.count, 0, f'log count={log.count}')
                tap.eq(log.reserve, 0, f'log reserve={log.reserve}')
                tap.eq(log.reserves, {}, 'резервы')
                tap.eq(log.delta_count, -2,
                       f'log delta_count={log.delta_count}')
                tap.eq(log.delta_reserve, 0,
                       f'log delta_reserve={log.delta_reserve}')
                tap.ok(log.recount, 'корректирующая запись')


async def test_put_more(tap, dataset):
    '''Положить на полку'''
    with tap.plan(15):

        product = await dataset.product()
        tap.ok(product, 'продукт сгенерирован')

        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        shelf = await dataset.shelf(store_id=store.store_id)
        tap.ok(shelf, 'полка создана')
        tap.eq(shelf.store_id, store.store_id, 'На складе')

        order1 = await dataset.order(store_id=store.store_id)
        tap.ok(order1, 'заказ 1 создан')
        order2 = await dataset.order(store_id=store.store_id)
        tap.ok(order2, 'заказ 2 создан')

        with await Stock.do_put(order1, shelf, product, 3) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 3, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')

        with await Stock.do_put(order2, shelf, product, 2) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 3 + 2, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')

        with await Stock.do_put(order1, shelf, product, 10) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, 10 + 2, f'count={stock.count}')
            tap.eq(stock.reserve, 0, f'reserve={stock.reserve}')


@pytest.mark.parametrize(
    'counts', [
        ((20, 0), (10, 0), 'Уменьшение количества'),
        ((20, 2), (10, 2), 'Фикс резерв'),
        ((20, 2), (20, 7), 'увеличиваем резерв'),
        ((20, 0), (20, 7), 'увеличиваем резерв с нуля'),
        ((20, 20), (20, 0), 'уменьшаем резерв в ноль'),
        ((20, 20), (10, 10), 'Меняем резерв и количество синхронно'),
        ((20, 20), (0, 0), 'Меняем резерв и количество синхронно в 0'),
        ((0, 0), (0, 0), 'Из нулей в нули'),
        ((0, 0), (20, 10), 'Из нулей в значения'),
    ]
)
async def test_put_changes(tap, dataset, counts):
    with tap.plan(16, counts[-1]):
        product = await dataset.product()
        tap.ok(product, 'продукт сгенерирован')

        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        shelf = await dataset.shelf(store_id=store.store_id)
        tap.ok(shelf, 'полка создана')
        tap.eq(shelf.store_id, store.store_id, 'На складе')

        order = await dataset.order(store_id=store.store_id)
        tap.ok(order, 'заказ 1 создан')
        tap.eq(order.store_id, shelf.store_id, 'на складе')

        count, reserve = counts[0]
        with await Stock.do_put(order,
                                shelf,
                                product,
                                count,
                                reserve=reserve) as stock:
            tap.ok(stock, 'Сохранен')
            tap.eq(stock.count, count,
                   f'count={stock.count}')
            tap.eq(stock.reserve, reserve,
                   f'reserve={stock.reserve}')

            reserved = await Stock.list_by_order(order)
            if reserve:
                tap.eq(len(reserved), 1, 'Один резерв')
            else:
                tap.in_ok(len(reserved), (0, 1), 'Число резервов')
            if reserved:
                with reserved[0] as r:
                    tap.eq(
                        r.reserves[order.order_id],
                        reserve,
                        'Количество в резерерве'
                    )
            else:
                tap.ok(reserve == 0, 'Количество в резерве')

        count, reserve = counts[1]
        with await Stock.do_put(order,
                                shelf,
                                product,
                                count,
                                reserve=reserve) as stock:
            tap.ok(stock, 'Сохранен с изменением')
            tap.eq(stock.count, count,
                   f'count={stock.count}')
            tap.eq(stock.reserve, reserve,
                   f'reserve={stock.reserve}')
            reserved = await Stock.list_by_order(order)
            if reserve:
                tap.eq(len(reserved), 1, 'Один резерв')
            else:
                tap.in_ok(len(reserved), (0, 1), 'Число резервов')
            if reserved:
                with reserved[0] as r:
                    tap.eq(
                        r.reserves[order.order_id],
                        reserve,
                        'Количество в резерерве'
                    )
            else:
                tap.ok(reserve == 0, 'Количество в резерве')


async def test_put_negative(tap, dataset):
    '''Отрицательная дельта запрещена'''
    with tap.plan(6):

        product = await dataset.product()
        tap.ok(product, 'продукт сгенерирован')

        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        shelf = await dataset.shelf(store_id=store.store_id)
        tap.ok(shelf, 'полка создана')
        tap.eq(shelf.store_id, store.store_id, 'На складе')

        order = await dataset.order(store_id=store.store_id)
        tap.ok(order, 'заказ создан')

        with tap.raises(AssertionError, 'отрицательное количество нельзя'):
            await Stock.do_put(order, shelf, product, -3)


async def test_put_zero(tap, dataset):
    '''Отрицательная дельта запрещена'''
    with tap.plan(6):

        product = await dataset.product()
        tap.ok(product, 'продукт сгенерирован')

        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        shelf = await dataset.shelf(store_id=store.store_id)
        tap.ok(shelf, 'полка создана')
        tap.eq(shelf.store_id, store.store_id, 'На складе')

        order = await dataset.order(store_id=store.store_id)
        tap.ok(order, 'заказ создан')

        with await Stock.do_put(order, shelf, product, 0) as stock:
            tap.ok(stock, 'сток с нулём создан')


async def test_dataset(tap, dataset):
    with tap.plan(2):
        stock = await dataset.stock(count=327)
        tap.ok(stock, 'остатки сгенерированы')
        tap.isa_ok(stock, Stock, 'тип модели')


# pylint: disable=too-many-locals
@pytest.mark.parametrize(
    'variant',
    [
        (
            'store',
            'kitchen_components',
            1,
            2,
            'обычная полка -> ПФ полка (используем квант)',
        ),
        (
            None,
            'kitchen_components',
            1,
            1,
            'неизвестная полка -> ПФ полка (используем квант)',
        ),
        (
            'kitchen_components',
            'store',
            1,
            1,
            'ПФ полка -> обычная полка (округление до кванта)',
        ),
        (
            'kitchen_components',
            'store',
            2,
            1,
            'ПФ полка -> обычная полка (без округления до кванта)',
        ),
        (
            'kitchen_components',
            'store',
            3,
            2,
            'ПФ полка -> обычная полка (округление до кванта)',
        ),
        (
            'kitchen_components',
            'kitchen_components',
            1,
            1,
            'ПФ полка -> ПФ полка (используем квант)',
        ),
    ],
)
async def test_put_components(tap, dataset, variant):
    src_type, dst_type, count_before, count_after, msg = variant

    with tap.plan(11, msg):
        store = await dataset.store()

        if src_type:
            src_shelf = await dataset.shelf(store=store, type=src_type)
        else:
            src_shelf = None
        dst_shelf = await dataset.shelf(store=store, type=dst_type)

        product = await dataset.product(quants=2, quant_unit='milligram')

        order = await dataset.order(store=store)
        with await Stock.do_put(
                order, dst_shelf, product, count_before, src_shelf=src_shelf,
        ) as stock:
            tap.eq_ok(stock.count, count_after, 'остаток')
            tap.eq_ok(stock.reserve, 0, 'резерв')
            tap.eq_ok(stock.quants, product.quants, 'кванты')

            logs = (await stock.list_log()).list
            tap.eq(len(logs), 1, 'основная запись')

            with logs[-1] as log:
                tap.eq(log.recount, None, 'log recount')
                tap.eq(log.type, 'put', 'log type')
                tap.eq(log.count, count_after, 'log count')
                tap.eq(log.reserve, 0, 'log reserve')
                tap.eq(log.delta_count, count_after, 'log delta_count')
                tap.eq(log.delta_reserve, 0, 'log delta_reserve')
                tap.eq(log.quants, product.quants, 'log quants')
