# pylint: disable=too-many-lines
import pytest

from stall.model.stock import Stock
from stall.model.stock_log import StockLog
from stall.model.suggest import Suggest


# pylint: disable=too-many-locals, too-many-statements
@pytest.mark.parametrize(
    'shelf_type', [
        'store',
        'markdown',
        'kitchen_components',
        'office'
    ],
)
@pytest.mark.parametrize(
    'counts',
    [
        [322, 322, 0, 'точное соответствие'],
        [321, 1279, 0, 'добавление'],
        [0, 123, 0, 'с нуля увеличиваем'],
        [0, 0, 0, 'было ноль осталось ноль'],
        [521, 27, 0, 'уменьшаем не до нуля (0 - резерв)'],
        [521, 27, 27, 'уменьшаем до резерва'],
    ]
)
async def test_check_product_one_stock(
        tap,
        dataset,
        wait_order_status,
        shelf_type,
        counts,
):
    with tap.plan(33, f'Чек по продукту ({counts[-1]})'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store   = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user    = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь на складе')

        order_stock = await dataset.order(store=store)
        store_id = order_stock.store_id
        tap.ok(order_stock, 'ордер для стока создан')
        tap.ok(store_id, 'склад')

        shelf = await dataset.shelf(store=store, type=shelf_type)

        stock = await dataset.stock(
            order=order_stock,
            shelf=shelf,
            product_id=product.product_id,
            count=counts[0],
            reserve=counts[2],
            valid='2020-11-12',
        )
        tap.ok(stock, 'остаток создан')
        tap.eq(stock.store_id, store_id, 'склад')
        tap.eq(stock.product_id, product.product_id, 'продукт')
        tap.eq(stock.count, counts[0], f'остаток {counts[0]}')
        tap.eq(stock.reserve, counts[2], f'резерв {counts[2]}')

        order = await dataset.order(
            type='check',
            required=[{
                'product_id': stock.product_id,
                'shelf_id': stock.shelf_id,
            }],
            acks=[user.user_id],
            status='reserving',
            estatus='begin',
            store_id=order_stock.store_id,
        )
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, store_id, 'на складе')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджесты')

        with suggests[0] as s:
            tap.ok(await s.done(count=counts[1]), 'закрыли саджест')
            tap.ok(await s.reload(), 'перегружен саджест')
            tap.eq(s.status, 'done', 'статус')
            tap.eq(s.type, 'check', 'тип')
            tap.eq(s.vars('stocks.0.0'), stock.stock_id, 'stock_id')
            tap.eq(s.vars('stocks.0.1'), stock.lsn, 'lsn')
            tap.eq(s.vars('stocks.0.2'), stock.count, 'count')
            tap.eq(s.result_count, counts[1], 'результирующее число')

        tap.ok(await order.done('complete', user=user), 'ордер закрыт')

        await wait_order_status(order, ('complete', 'begin'))

        tap.ok(await order.reload(), 'Ордер перегружен')
        tap.eq(order.fstatus, ('complete', 'begin'), 'статус')

        await wait_order_status(order, ('complete', 'done'))

        stocks = await Stock.list_by_product(
            product_id=product.product_id,
            store_id=order.store_id,
            shelf_type=shelf_type,
        )
        tap.eq(sum([s.count for s in stocks]),
               counts[1],
               'количество на складе итого')

        tap.eq(await Stock.list_by_order(order),
               [],
               'резервов на этот заказ нет')

        # Проверяем полку находок
        if counts[1] > counts[0]:
            stocks = await Stock.list_by_product(
                product_id=product.product_id,
                store_id=store.store_id,
                shelf_type=(
                    'kitchen_found' if shelf_type == 'kitchen_components'
                    else 'found'
                ),
            )
            tap.eq(len(stocks), 1, "Длина")
            tap.eq(sum(s.count for s in stocks),
                   counts[1] - counts[0],
                   'На полке находок')

            logs = await StockLog.list(
                conditions=[
                    ('order_id', order.order_id),
                    ('type', 'found')],
                by='look',
            )
            tap.eq(len(logs.list), 1, "Создан лог с типом found")

        elif counts[1] < counts[0]:
            # Проверяем полку потерь
            stocks = await Stock.list_by_product(
                product_id=product.product_id,
                store_id=store.store_id,
                shelf_type=(
                    'kitchen_lost' if shelf_type == 'kitchen_components'
                    else 'lost'
                ),
            )

            tap.eq(sum(s.count for s in stocks),
                   counts[0] - counts[1],
                   'На полке потерь')
            tap.eq(sum(s.reserve for s in stocks), 0, 'нет резерва')

            logs = await StockLog.list(
                conditions=[
                    ('order_id', order.order_id),
                    ('type', 'lost')],
                by='look',
            )
            tap.ne(len(logs.list), 0, "Создан лог с типом lost")
        elif counts[1] == counts[0]:
            tap.passed('')
            tap.passed('')
            tap.passed('')


# pylint: disable=too-many-locals,too-many-statements
@pytest.mark.parametrize(
    'shelf_type', ['store', 'markdown', 'kitchen_components', 'office'],
)
@pytest.mark.parametrize(
    'counts',
    [
        [(322 - 121, 121),  322,  (0, 0),   0,      'точное соответствие'],
        [(321, 255),        1279, (0, 0),   0,      'добавление'],

        [(521, 321),        27,   (0, 0),   815,    'уменьшаем не до нуля'],
        [(521, 321),        400,  (0, 0),   442,    'уменьшаем до промзн'],
        [(52, 21),          0,    (0, 0),   73,     'уменьшаем до нуля'],

        [(52, 21),          33,   (15, 5),  40,     'уменьшаем при резерве'],
        [(17, 15),          20,   (15, 5),  12,     'уменьшаем до резерва'],
    ]
)
async def test_check_product_stocks(
        tap,
        dataset,
        uuid,
        wait_order_status,
        shelf_type,
        counts,
):
    with tap.plan(39, f'Чек по продукту ({counts[-1]})'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store   = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user    = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order_stock = await dataset.order(store=store)
        store_id = order_stock.store_id
        tap.ok(order_stock, 'ордер для стока создан')
        tap.ok(store_id, 'склад')

        shelf = await dataset.shelf(store=store, type=shelf_type)

        stock = await dataset.stock(
            order=order_stock,
            shelf=shelf,
            product_id=product.product_id,
            count=counts[0][0],
            lot=uuid(),
            reserve=counts[2][0],
            valid='2021-11-01',
        )
        tap.ok(stock, 'остаток создан')
        tap.eq(stock.store_id, store_id, 'склад')
        tap.eq(stock.product_id, product.product_id, 'продукт')
        tap.eq(stock.count, counts[0][0], f'остаток {counts[0][0]}')
        tap.eq(stock.reserve, counts[2][0], f'резерв {counts[2][0]}')

        stock2 = await dataset.stock(
            order=order_stock,
            shelf=shelf,
            product_id=product.product_id,
            count=counts[0][1],
            shelf_id=stock.shelf_id,
            lot=uuid(),
            reserve=counts[2][1],
        )
        tap.ok(stock2, 'остаток создан')
        tap.eq(stock2.store_id, store_id, 'склад')
        tap.eq(stock2.product_id, product.product_id, 'продукт')
        tap.eq(stock2.count, counts[0][1], f'остаток {counts[0][1]}')
        tap.eq(stock2.reserve, counts[2][1], f'резерв {counts[2][1]}')
        tap.eq(stock2.shelf_id, stock.shelf_id, 'та же полка')
        tap.ne(stock2.stock_id, stock.stock_id, 'другой stock_id')
        tap.ne(stock2.lot, stock.lot, 'партии разные')

        order = await dataset.order(
            type='check',
            required=[
                {
                    'product_id': stock.product_id,
                    'shelf_id': stock.shelf_id,
                },
            ],
            status='reserving',
            estatus='begin',
            store_id=order_stock.store_id,
            acks=[user.user_id],
        )
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, store_id, 'на складе')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджесты')

        with suggests[0] as s:
            tap.ok(await s.done(count=counts[1]), 'закрыли саджест')
            tap.ok(await s.reload(), 'перегружен саджест')
            tap.eq(s.status, 'done', 'статус')
            tap.eq(s.type, 'check', 'тип')
            tap.eq(len(s.vars('stocks')), 2, 'по двум стокам')
            tap.eq(s.result_count, counts[1], 'результирующее число')

        tap.ok(await order.done('complete', user=user), 'ордер закрыт')

        await wait_order_status(order, ('complete', 'begin'))

        tap.ok(await order.reload(), 'Ордер перегружен')
        tap.eq(order.fstatus, ('complete', 'begin'), 'статус')

        await wait_order_status(order, ('complete', 'done'))

        stocks = await Stock.list_by_product(
            product_id=product.product_id,
            store_id=order.store_id,
            shelf_type=shelf_type,
        )
        tap.eq(sum([s.count for s in stocks]),
               counts[1],
               'количество на складе итого')
        tap.eq(await Stock.list_by_order(order),
               [],
               'резервов на этот заказ нет')

        # Проверяем полку находок
        if counts[1] > sum(counts[0]):
            stocks = await Stock.list_by_product(
                product_id=product.product_id,
                store_id=store.store_id,
                shelf_type=(
                    'kitchen_found' if shelf_type == 'kitchen_components'
                    else 'found'
                ),
            )
            tap.eq(len(stocks), 1, "Длина")
            tap.eq(sum(s.count for s in stocks),
                   counts[1] - sum(counts[0]),
                   'На полке находок')

            logs = await StockLog.list(
                conditions=[
                    ('order_id', order.order_id),
                    ('type', 'found')],
                by='look',
            )
            tap.eq(len(logs.list), 1, "Создан лог с типом found")
        elif counts[1] < sum(counts[0]):
            # Проверяем полку потерь
            stocks = await Stock.list_by_product(
                product_id=product.product_id,
                store_id=store.store_id,
                shelf_type=(
                    'kitchen_lost' if shelf_type == 'kitchen_components'
                    else 'lost'
                ),
            )

            tap.eq(sum(s.count for s in stocks),
                   counts[-2],
                   'На полке потерь')
            tap.eq(sum(s.reserve for s in stocks), 0, 'нет резерва')

            logs = await StockLog.list(
                conditions=[
                    ('order_id', order.order_id),
                    ('type', 'lost')],
                by='look',
            )
            tap.ne(len(logs.list), 0, "Создан лог с типом lost")
        elif counts[1] == sum(counts[0]):
            tap.passed('')
            tap.passed('')
            tap.passed('')


# pylint: disable=too-many-locals,too-many-statements
@pytest.mark.parametrize(
    'shelf_type', ['store', 'markdown', 'kitchen_components', 'office'],
)
@pytest.mark.parametrize(
    'counts',
    [   # кол-ва                  резрвы        враг
        [(322 - 121, 121),  321,  (0, 0),     (1, 1), 'change_do',
         'уменьшение'],
        [(322 - 121, 121),  321,  (0, 0),     (1, 1), 'change_prepare',
         'уменьшение'],
        [(322, 121),        200,  (300, 120), (1, 1), 'change_prepare',
         'уменьшение меньше резерва'],
        [(321, 255),        800,  (20, 55),  (2, 1), 'change_do',
         'добавление'],
        [(321, 255),        800,  (20, 55),  (2, 1), 'change_prepare',
         'добавление'],
    ]
)
async def test_check_rollback(
        tap,
        dataset,
        uuid,
        wait_order_status,
        shelf_type,
        counts,
):
    with tap.plan(56, f'{counts[-1]}: проблемы на {counts[-2]}'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store   = await dataset.store()
        user    = await dataset.user(store=store)

        order_stock = await dataset.order(store=store)
        store_id = order_stock.store_id
        tap.ok(order_stock, 'ордер для стока создан')
        tap.ok(store_id, 'склад')

        shelf = await dataset.shelf(store=store, type=shelf_type)

        stock = await dataset.stock(
            order=order_stock,
            shelf=shelf,
            product_id=product.product_id,
            count=counts[0][0],
            lot=uuid(),
            reserve=counts[2][0],
            valid='2012-01-02',
        )
        tap.ok(stock, 'остаток создан')
        tap.eq(stock.store_id, store_id, 'склад')
        tap.eq(stock.product_id, product.product_id, 'продукт')
        tap.eq(stock.count, counts[0][0], f'остаток {counts[0][0]}')
        tap.eq(stock.reserve, counts[2][0], f'резерв {counts[2][0]}')

        stock2 = await dataset.stock(
            order=order_stock,
            product_id=product.product_id,
            count=counts[0][1],
            shelf_id=stock.shelf_id,
            lot=uuid(),
            reserve=counts[2][1],
            valid='2012-01-02',
        )
        tap.ok(stock2, 'остаток создан')
        tap.eq(stock2.store_id, store_id, 'склад')
        tap.eq(stock2.product_id, product.product_id, 'продукт')
        tap.eq(stock2.count, counts[0][1], f'остаток {counts[0][1]}')
        tap.eq(stock2.reserve, counts[2][1], f'резерв {counts[2][1]}')
        tap.eq(stock2.shelf_id, stock.shelf_id, 'та же полка')
        tap.ne(stock2.stock_id, stock.stock_id, 'другой stock_id')
        tap.ne(stock2.lot, stock.lot, 'партии разные')

        stocks = await Stock.list_by_product(
            product_id=product.product_id,
            store_id=order_stock.store_id,
            shelf_type=shelf_type,
        )
        pre_count = sum([s.count for s in stocks])
        pre_reserve = sum([s.reserve for s in stocks])
        tap.eq(pre_count, counts[0][0] + counts[0][1],
               'количество на складе')
        tap.eq(pre_reserve, counts[2][0] + counts[2][1],
               'резервировано на складе')

        order = await dataset.order(
            type='check',
            required=[{
                'product_id': stock.product_id,
                'shelf_id': stock.shelf_id,
            }],
            shelves=[stock.shelf_id],
            products=[product.product_id],
            status='processing',
            estatus='begin',
            store_id=order_stock.store_id,
            attr={'request_type': 'from woody acc'}
        )
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, store_id, 'на складе')
        tap.eq(order.fstatus, ('processing', 'begin'), 'статус')

        order2 = await dataset.order(store_id=order.store_id)
        tap.eq(order2.store_id, order.store_id, 'заказ 2 создан')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджесты')

        with suggests[0] as s:
            tap.ok(await s.done(count=counts[1]), 'закрыли саджест')
            tap.ok(await s.reload(), 'перегружен саджест')
            tap.eq(s.status, 'done', 'статус')
            tap.eq(s.type, 'check', 'тип')
            tap.eq(len(s.vars('stocks')), 2, 'по двум стокам')
            tap.eq(s.result_count, counts[1], 'результирующее число')

        tap.ok(await order.done('complete', user=user), 'ордер закрыт')

        await wait_order_status(order, ('complete', 'begin'))

        tap.ok(await order.reload(), 'Ордер перегружен')
        tap.eq(order.fstatus, ('complete', 'begin'), 'статус')

        await wait_order_status(order, ('complete', counts[-2]))
        tap.ok(await stock.do_put_exists(order2,
                                         counts[3][0],
                                         reserve=counts[3][1]),
               'положили ещё товара')
        tap.ok(await stock.reload(), 'перегружен сток')
        slsn = dict((x[0], x[1]) for x in suggests[0].vars('stocks.*'))
        tap.ne(stock.lsn, slsn[stock.stock_id], 'lsn поменялся')

        await wait_order_status(order, ('complete', 'done'))

        stocks = await Stock.list_by_product(
            product_id=product.product_id,
            store_id=order_stock.store_id,
            shelf_type=shelf_type,
        )
        count = sum([s.count for s in stocks])
        reserve = sum([s.reserve for s in stocks])
        tap.eq(count, counts[0][0] + counts[0][1] + counts[3][0],
               'количество на складе не менялось')
        tap.eq(reserve, counts[2][0] + counts[2][1] + counts[3][1],
               'резервировано на складе не менялось')

        tap.ok(await order.reload(), 'ордер перегружен')
        tap.eq(len(order.problems), 1, 'Одна проблема')
        single_problem = order.problems[0]
        tap.eq(
            single_problem.product_id,
            product.product_id,
            'Продукт в проблеме'
        )
        tap.eq(single_problem.shelf_id, stock.shelf_id, 'Полка в проблеме')
        tap.eq(single_problem.type, 'stock_changed', 'Тот тип проблемы')
        child_id = order.vars('child.0', None)
        tap.ok(child_id, 'идентификатор дочернего заказа')

        child = await order.load(child_id)
        tap.ok(child, 'дочерний загружен')
        tap.eq(child.parent[0], order.order_id, 'parent')
        tap.eq(child.store_id, order.store_id, 'store_id')
        tap.eq(child.type, 'check', 'type')
        tap.eq(child.fstatus, ('reserving', 'begin'), 'full status')
        await wait_order_status(child, ('reserving', 'find_lost_and_found'))
        tap.eq(child.products, [product.product_id], 'продукт')
        tap.eq(child.shelves, [stock.shelf_id], 'полка')
        tap.eq(
            child.attr['request_type'],
            order.attr['request_type'],
            'прокидываем request_type',
        )


@pytest.mark.parametrize(
    'variant',
    [
        (3, 10, 12, 0, 'корректировка в большую сторону'),
        (3, 10, 6, 4, 'корректировка в меньшую сторону (без округлений)'),
    ],
)
async def test_kitchen(tap, dataset, wait_order_status, variant):
    quants, count_before, count_after, lf_count_after, msg = variant

    with tap.plan(20, msg):
        product = await dataset.product(quants=quants)

        store = await dataset.store()

        user = await dataset.user(store=store)

        lost = await dataset.shelf(
            store=store,
            type='kitchen_lost',
        )
        await dataset.shelf(
            store=store,
            type='kitchen_found',
        )

        k_comp = await dataset.shelf(store=store, type='kitchen_components')

        stock = await dataset.stock(
            shelf=k_comp,
            product_id=product.product_id,
            count=count_before,
            valid='2012-01-02',
        )
        tap.ok(stock, 'остаток создан')
        tap.eq(stock.count, count_before, 'остаток')
        tap.eq(stock.reserve, 0, 'резерв')

        order = await dataset.order(
            type='check',
            products=[product.product_id],
            shelves=[stock.shelf_id],
            required=[
                {
                    'product_id': product.product_id,
                    'shelf_id': stock.shelf_id,
                }
            ],
            status='processing',
            store_id=store.store_id,
        )
        tap.ok(order, 'ордер создан')
        tap.eq(order.fstatus, ('processing', 'begin'), 'статус')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджесты')

        with suggests[0] as s:
            tap.ok(await s.done(count=count_after), 'закрыли саджест')
            tap.ok(await s.reload(), 'перегружен саджест')
            tap.eq(s.status, 'done', 'статус')
            tap.eq(s.type, 'check', 'тип')
            tap.eq(s.result_count, count_after, 'результирующее число')

        tap.ok(await order.done('complete', user=user), 'ордер закрыт')

        await wait_order_status(order, ('complete', 'begin'))

        tap.ok(await order.reload(), 'ордер перегружен')
        tap.eq(order.fstatus, ('complete', 'begin'), 'статус')

        await wait_order_status(order, ('complete', 'done'))

        k_comp_stocks = await Stock.list_by_product(
            product_id=product.product_id,
            store_id=order.store_id,
            shelf_type=k_comp.type,
        )
        tap.eq(
            sum([s.count for s in k_comp_stocks]),
            count_after,
            'количество на полке компонент',
        )

        lf_stocks = await Stock.list_by_product(
            product_id=product.product_id,
            store_id=order.store_id,
            shelf_type=lost.type,
        )
        tap.eq(
            sum([s.count for s in lf_stocks]),
            lf_count_after,
            'количество на полке потерь',
        )

        tap.eq(
            await Stock.list_by_order(order),
            [],
            'резервов на заказ нет',
        )


async def test_check_no_suggests(tap, dataset, wait_order_status):
    with tap.plan(3, 'Ордер без саджестов'):
        product = await dataset.product()
        store = await dataset.store()
        shelf = await dataset.shelf(store=store)
        order = await dataset.order(
            type='check',
            products=[product.product_id],
            shelves=[shelf.shelf_id],
            required=[
                {
                    'product_id': product.product_id,
                    'shelf_id': shelf.shelf_id,
                },
            ],
            status='complete',
            store_id=store.store_id,
        )
        tap.ok(order, 'ордер создан')
        tap.ok(
            await wait_order_status(order, ('complete', 'done')),
            'Докатился до конца без ошибки'
        )


@pytest.mark.parametrize('set_required', [True, False])
@pytest.mark.parametrize(
    'counts',
    [
        [322, 322, 0, 'точное соответствие'],
        [321, 1279, 0, 'добавление'],
        [321, 1279, 10, 'добавление, ненулевой резерв'],
        [0, 123, 0, 'с нуля увеличиваем'],
        [0, 0, 0, 'было ноль осталось ноль'],

        [521, 27, 0, 'уменьшаем не до нуля (0 - резерв)'],
        [521, 27, 27, 'уменьшаем до резерва'],
    ]
)
# pylint: disable=too-many-statements, too-many-locals, too-many-branches
async def test_reserve(tap, dataset, wait_order_status, counts, set_required):
    with tap.plan(34, f'Чек по продукту ({counts[-1]})'):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.store()
        user = await dataset.user(store=store)
        await dataset.stock(store=store, product=product, count=0)

        order_stock = await dataset.order(store=store)
        store_id = order_stock.store_id
        tap.eq(order_stock.store_id, store.store_id, 'ордер для стока создан')
        tap.ok(store_id, 'склад')

        shelf = await dataset.shelf(store_id=order_stock.store_id)
        tap.ok(shelf, 'полка создана')

        lost = await dataset.shelf(store=store, type='lost')
        tap.eq(lost.store_id, store.store_id, 'полка создана')
        tap.eq(lost.type, 'lost', 'полка потерь')

        found = await dataset.shelf(
            store=store,
            type='found',
        )
        tap.eq(found.store_id, store.store_id, 'полка потерь')
        tap.eq(found.type, 'found', 'тип')

        with tap.subtest(6 if counts[0] else 1, 'создание стока') as taps:
            if counts[0]:
                stock = await dataset.stock(
                    order=order_stock,
                    product_id=product.product_id,
                    count=counts[0],
                    reserve=counts[2],
                    shelf=shelf,
                    valid='2022-01-02',
                )
                taps.ok(stock, 'остаток создан')
                taps.eq(stock.store_id, store_id, 'склад')
                taps.eq(stock.product_id, product.product_id, 'продукт')
                taps.eq(stock.count, counts[0], f'остаток {counts[0]}')
                taps.eq(stock.reserve, counts[2], f'резерв {counts[2]}')
                taps.eq(stock.shelf_id, shelf.shelf_id, 'полка')
            else:
                taps.passed('Сток создавать не надо')

        if set_required:
            products_and_shelves = {
                'required': [
                    {
                        'shelf_id': shelf.shelf_id,
                        'product_id': product.product_id,
                    }
                ],
            }
        else:
            products_and_shelves = {
                'products': [product.product_id],
                'shelves': [shelf.shelf_id],
            }

        order = await dataset.order(
            type='check',
            **products_and_shelves,
            status='reserving',
            estatus='begin',
            store_id=order_stock.store_id,
            vars={
                'reserve': True,
            }
        )
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, store_id, 'на складе')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')

        await wait_order_status(order, ('request', 'waiting'))
        await order.ack(user)

        await wait_order_status(order, ('processing', 'waiting'))
        if counts[0]:
            await stock.reload()
            tap.eq_ok(stock.reserves[order.order_id], counts[0] - counts[2],
                      'Зарезервировано все, что не было зарезервировано ранее')
        else:
            tap.passed('Нечего резервировать')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджесты')

        with suggests[0] as s:
            tap.ok(await s.done(count=counts[1], valid='2020-01-02'),
                   'закрыли саджест')
            tap.ok(await s.reload(), 'перегружен саджест')
            tap.eq(s.status, 'done', 'статус')
            tap.eq(s.type, 'check', 'тип')
            with tap.subtest(2 if counts[0] else 1, 'vars саджесте') as taps:
                if counts[0]:
                    taps.eq(s.vars('stocks.0.0'), stock.stock_id, 'stock_id')
                    taps.eq(s.vars('stocks.0.2'), stock.count, 'count')
                else:
                    taps.eq(s.vars('stocks'), [], 'пусто в стоках')
            tap.eq(s.result_count, counts[1], 'результирующее число')

        tap.ok(await order.done('complete', user=user), 'ордер закрыт')

        await wait_order_status(order, ('complete', 'begin'))

        tap.ok(await order.reload(), 'Ордер перегружен')
        tap.eq(order.fstatus, ('complete', 'begin'), 'статус')

        await wait_order_status(order, ('complete', 'done'))

        children = await order.list(
            by='full',
            conditions=(
                ('parent', '[1]=', order.order_id),
                ('type', order.type),
            ),
            sort=(),
        )
        tap.eq(len(children.list), 0, 'Дочерних ордеров не появилось')

        stocks = await Stock.list_by_product(
            product_id=product.product_id,
            store_id=order.store_id,
            shelf_id=shelf.shelf_id,
        )
        if counts[0] or counts[1]:
            tap.ok(len(stocks), 'стоки есть на полке')
        else:
            tap.ok(not len(stocks), 'стоков нет на полке')
        tap.eq(sum([s.count for s in stocks]),
               counts[1],
               'количество на складе итого')

        tap.eq(await Stock.list_by_order(order),
               [],
               'резервов на этот заказ нет')
        # Проверяем полку находок
        if counts[1] > counts[0]:
            stocks = await Stock.list_by_product(
                product_id=product.product_id,
                store_id=store.store_id,
                shelf_type='found',
            )
            tap.eq(len(stocks), 1, "Длина")
            tap.eq(sum(s.count for s in stocks),
                   counts[1] - counts[0],
                   'На полке находок')

            logs = await StockLog.list(
                conditions=[
                    ('order_id', order.order_id),
                    ('type', 'found')],
                by='look',
            )
            tap.eq(len(logs.list), 1, "Создан лог с типом found")

        elif counts[1] < counts[0]:
            # Проверяем полку потерь
            stocks = await Stock.list_by_product(
                product_id=product.product_id,
                store_id=store.store_id,
                shelf_type='lost',
            )

            tap.eq(sum(s.count for s in stocks),
                   counts[0] - counts[1],
                   'На полке потерь')
            tap.eq(sum(s.reserve for s in stocks), 0, 'нет резерва')

            logs = await StockLog.list(
                conditions=[
                    ('order_id', order.order_id),
                    ('type', 'lost')],
                by='look',
            )
            tap.ne(len(logs.list), 0, "Создан лог с типом lost")
        elif counts[1] == counts[0]:
            tap.passed('')
            tap.passed('')
            tap.passed('')


# pylint: disable=too-many-locals
async def test_2_stocks_on_shelf(tap, dataset, wait_order_status, uuid):
    with tap.plan(22, 'check на полке с двумя остатками'):
        product = await dataset.product()

        store = await dataset.store()
        user = await dataset.user(store=store)

        shelf = await dataset.shelf(store_id=store.store_id)
        await dataset.shelf(store=store, type='lost')
        await dataset.shelf(store=store, type='found')

        stock1 = await dataset.stock(
            product_id=product.product_id,
            count=10,
            reserve=10,
            shelf=shelf,
            valid='2022-01-02',
            lot=uuid(),
        )
        stock2 = await dataset.stock(
            product_id=product.product_id,
            count=9,
            reserve=5,
            shelf=shelf,
            valid='2022-01-02',
            lot=uuid(),
        )

        order = await dataset.order(
            type='check',
            products=[product.product_id],
            shelves=[shelf.shelf_id],
            status='reserving',
            estatus='begin',
            store_id=store.store_id,
            vars={
                'reserve': True,
            }
        )
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, store.store_id, 'на складе')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')

        await wait_order_status(order, ('request', 'waiting'))
        await order.ack(user)

        await wait_order_status(order, ('processing', 'waiting'))
        await stock2.reload()
        tap.eq_ok(
            stock2.reserves[order.order_id],
            4,
            'Зарезервировано все, что не было зарезервировано ранее'
        )

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджесты')

        with suggests[0] as s:
            tap.ok(await s.done(count=0, valid='2020-01-02'),
                   'закрыли саджест')
            tap.ok(await s.reload(), 'перегружен саджест')
            tap.eq(s.status, 'done', 'статус')
            tap.eq(s.type, 'check', 'тип')

            stocks_in_vars = s.vars('stocks')
            stocks_in_vars = {s[0]: s[2] for s in stocks_in_vars}
            tap.eq(stocks_in_vars.get(stock1.stock_id), stock1.count,
                   'stock1 in vars, correct count')
            tap.eq(stocks_in_vars.get(stock2.stock_id), stock2.count,
                   'stock2 in vars, correct count')

            tap.eq(s.result_count, 0, 'результирующее число')

        tap.ok(await order.done('complete', user=user), 'ордер закрыт')

        await wait_order_status(order, ('complete', 'begin'))

        tap.ok(await order.reload(), 'Ордер перегружен')
        tap.eq(order.fstatus, ('complete', 'begin'), 'статус')

        await wait_order_status(order, ('complete', 'done'))

        children = await order.list(
            by='full',
            conditions=(
                ('parent', '[1]=', order.order_id),
                ('type', order.type),
            ),
            sort=(),
        )
        tap.eq(len(children.list), 0, 'Дочерних ордеров не появилось')

        stocks = await Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=store.store_id,
            product_id=product.product_id,
        )
        stocks = {s.stock_id: s.count for s in stocks}
        tap.eq_ok(
            stocks.get(stock1.stock_id),
            10,
            'остаток 1 без изменений (был весь зарезервирован)'
        )
        tap.eq_ok(
            stocks.get(stock2.stock_id),
            5,
            'остаток 2 уменьшен до резерва'
        )


# pylint: disable=too-many-locals, too-many-statements
async def test_create_child(tap, dataset, uuid, wait_order_status):
    with tap.plan(35, 'создание дочернего ордера'):
        product = await dataset.product()

        store = await dataset.store()
        user = await dataset.user(store=store)

        shelf = await dataset.shelf(store_id=store.store_id)
        await dataset.shelf(store=store, type='lost')
        await dataset.shelf(store=store, type='found')

        stock1 = await dataset.stock(
            product_id=product.product_id,
            count=10,
            reserve=10,
            shelf=shelf,
            valid='2022-01-02',
            lot=uuid(),
        )
        stock2 = await dataset.stock(
            product_id=product.product_id,
            count=9,
            reserve=5,
            shelf=shelf,
            valid='2022-01-02',
            lot=uuid(),
        )

        order = await dataset.order(
            type='check',
            products=[product.product_id],
            shelves=[shelf.shelf_id],
            status='reserving',
            estatus='begin',
            store_id=store.store_id,
            vars={
                'reserve': True,
            },
            attr={'request_type': 'from woody acc'},
        )
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, store.store_id, 'на складе')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'статус')

        await wait_order_status(order, ('request', 'waiting'))
        await order.ack(user)

        await wait_order_status(order, ('processing', 'waiting'))
        await stock2.reload()
        tap.eq_ok(stock2.reserves[order.order_id], 4,
                  'Зарезервировано все, что не было зарезервировано ранее')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'саджесты')

        with suggests[0] as s:
            tap.ok(await s.done(count=0, valid='2020-01-02'),
                   'закрыли саджест')
            tap.ok(await s.reload(), 'перегружен саджест')
            tap.eq(s.status, 'done', 'статус')
            tap.eq(s.type, 'check', 'тип')

            stocks_in_vars = s.vars('stocks')
            stocks_in_vars = {s[0]: s[2] for s in stocks_in_vars}
            tap.eq(stocks_in_vars.get(stock1.stock_id), stock1.count,
                   'stock1 in vars, correct count')
            tap.eq(stocks_in_vars.get(stock2.stock_id), stock2.count,
                   'stock2 in vars, correct count')

            tap.eq(s.result_count, 0, 'результирующее число')

        tap.ok(await order.done('complete', user=user), 'ордер закрыт')

        await wait_order_status(order, ('complete', 'change_prepare'))

        order2 = await dataset.order(store_id=order.store_id)
        tap.ok(await stock1.do_put_exists(order2, 1, reserve=1),
               'положили ещё товара')

        await wait_order_status(order, ('complete', 'done'))

        stocks = await Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=store.store_id,
            product_id=product.product_id,
        )
        stocks = {s.stock_id: s.count for s in stocks}
        tap.eq_ok(stocks.get(stock1.stock_id), 11,
                  'остаток 1 стал на 1 больше')
        tap.eq_ok(stocks.get(stock2.stock_id), 9,
                  'остаток 2 не изменился')
        tap.eq(len(order.problems), 1, 'Одна проблема')
        problem = order.problems[0]
        tap.eq(problem.type, 'stock_changed', 'Тип проблемы правильный')
        tap.eq(problem.shelf_id, stock1.shelf_id, 'Полка правильная')
        tap.eq(problem.product_id, stock1.product_id, 'Продукт тот')

        child_id = order.vars('child.0', None)
        tap.ok(child_id, 'идентификатор дочернего заказа')

        child = await order.load(child_id)
        tap.ok(child, 'дочерний загружен')
        tap.eq(child.parent[0], order.order_id, 'parent')
        tap.eq(child.store_id, order.store_id, 'store_id')
        tap.eq(child.type, 'check', 'type')
        tap.eq(child.fstatus, ('reserving', 'begin'), 'full status')
        await wait_order_status(child, ('reserving', 'find_lost_and_found'))
        tap.eq(child.products, [product.product_id], 'продукт')
        tap.eq(child.shelves, [shelf.shelf_id], 'полка')
        tap.eq(child.vars('reserve', False), True, 'child reserve is True')
        tap.eq(
            child.attr['request_type'],
            order.attr['request_type'],
            'прокидываем request_type',
        )


async def test_more_required(tap, dataset,  wait_order_status):
    with tap.plan(47, 'Несколько продуктов в required'):
        product1 = await dataset.product()
        tap.ok(product1, 'товар создан')

        product2 = await dataset.product()
        tap.ok(product2, 'товар создан')

        product3 = await dataset.product()
        tap.ok(product3, 'товар создан')

        store   = await dataset.store()
        user    = await dataset.user(store=store)

        order_stock = await dataset.order(store=store)
        store_id = order_stock.store_id
        tap.eq(order_stock.store_id, store.store_id, 'ордер для стока создан')
        tap.ok(store_id, 'склад')

        shelf1 = await dataset.shelf(store_id=order_stock.store_id)
        tap.ok(shelf1, 'полка создана')
        shelf2 = await dataset.shelf(store_id=order_stock.store_id)
        tap.ok(shelf2, 'полка создана')
        shelf3 = await dataset.shelf(store_id=order_stock.store_id)
        tap.ok(shelf3, 'полка создана')

        lost = await dataset.shelf(store=store, type='lost')
        tap.eq(lost.store_id, store.store_id, 'полка создана')
        tap.eq(lost.type, 'lost', 'полка потерь')

        found = await dataset.shelf(
            store=store,
            type='found',
        )
        tap.eq(found.store_id, store.store_id, 'полка потерь')
        tap.eq(found.type, 'found', 'тип')

        stock1 = await dataset.stock(
            order=order_stock,
            product_id=product1.product_id,
            count=10,
            reserve=0,
            shelf=shelf1,
            valid='2022-01-02',
        )
        tap.ok(stock1, 'остаток создан')

        stock2 = await dataset.stock(
            order=order_stock,
            product_id=product2.product_id,
            count=5,
            reserve=0,
            shelf=shelf2,
            valid='2022-01-02',
        )
        tap.ok(stock2, 'остаток создан')

        stock3 = await dataset.stock(
            order=order_stock,
            product_id=product3.product_id,
            count=7,
            reserve=0,
            shelf=shelf3,
            valid='2022-01-02',
        )
        tap.ok(stock3, 'остаток создан')

        order = await dataset.order(
            type='check',
            status='reserving',
            estatus='begin',
            store_id=order_stock.store_id,
            required=[
                {
                    'shelf_id': shelf1.shelf_id,
                    'product_id': product1.product_id,
                },
                {
                    'shelf_id': shelf2.shelf_id,
                    'product_id': product2.product_id,
                },
                {
                    'shelf_id': shelf3.shelf_id,
                    'product_id': product3.product_id,
                }
            ],
        )
        tap.ok(order, 'ордер создан')
        tap.eq(order.store_id, store_id, 'на складе')
        await wait_order_status(order,  ('request', 'waiting'))
        await order.ack(user)
        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 3, 'саджесты по числу required')

        with next(sug for sug in suggests
                  if sug.product_id == product1.product_id) as s:
            tap.ok(await s.done(count=5), 'закрыли саджест на меньшее')
            tap.ok(await s.reload(), 'перегружен саджест')
            tap.eq(s.status, 'done', 'статус')
            tap.eq(s.type, 'check', 'тип')

        with next(sug for sug in suggests
                  if sug.product_id == product2.product_id) as s:
            tap.ok(await s.done(count=5), 'закрыли саджест на ровно')
            tap.ok(await s.reload(), 'перегружен саджест')
            tap.eq(s.status, 'done', 'статус')
            tap.eq(s.type, 'check', 'тип')

        with next(sug for sug in suggests
                  if sug.product_id == product3.product_id) as s:
            tap.ok(await s.done(count=10), 'закрыли саджест на больше')
            tap.ok(await s.reload(), 'перегружен саджест')
            tap.eq(s.status, 'done', 'статус')
            tap.eq(s.type, 'check', 'тип')

        tap.ok(await order.done('complete', user=user), 'ордер закрыт')
        await wait_order_status(order, ('complete', 'done'))

        await stock1.reload()
        tap.eq(stock1.count, 5, '1 продукт на стоке 1')
        tap.eq(stock1.reserve, 0, 'нет резерва на стоке 1')

        await stock2.reload()
        tap.eq(stock2.count, 5, '2 продукт на стоке 2')
        tap.eq(stock2.reserve, 0, 'нет резерва на стоке 2')

        await stock3.reload()
        tap.eq(stock3.count, 10, '3 продукт на стоке 3')

        logs = await StockLog.list(
            conditions=[
                ('order_id', order.order_id),
                ('type', 'found')
            ],
            by='look',
        )
        tap.eq(len(logs.list), 1, "Создан лог с типом found")
        tap.eq(logs.list[0].delta_count, 3, 'delta_count')
        found_logs = await StockLog.list(
            by='look',
            conditions=[
                ('order_id', order.order_id),
                ('type', 'put'),
                ('shelf_id', found.shelf_id),
            ],
        )
        tap.eq(len(found_logs.list), 1, 'Одно перемещение на found')
        tap.eq(found_logs.list[0].delta_count, 3, 'delta_count')

        # Проверяем полку потерь
        logs = await StockLog.list(
            conditions=[
                ('order_id', order.order_id),
                ('type', 'lost')
            ],
            by='look',
        )

        tap.eq(len(logs.list), 1, 'сток на полку потерь')
        tap.eq(logs.list[0].delta_count, -5, 'delta_count')

        lost_logs = await StockLog.list(
            by='look',
            conditions=[
                ('order_id', order.order_id),
                ('type', 'put'),
                ('shelf_id', lost.shelf_id)
            ],
        )
        tap.eq(len(lost_logs.list), 1, 'Одно перемещение на lost')
        tap.eq(lost_logs.list[0].delta_count, 5, 'delta_count')


async def test_recalculation_by_order_lnf(
        tap, dataset, wait_order_status, uuid):
    with tap.plan(
            22, 'Не меняется lost and found при пересчете по распоряжению'):
        store = await dataset.full_store(options={'exp_schrodinger': False})
        user = await dataset.user(store=store)

        shelf1 = await dataset.shelf(type='store', store=store)
        shelf2 = await dataset.shelf(type='store', store=store)
        shelf3 = await dataset.shelf(type='store', store=store)
        shelf_lost = await dataset.shelf(store=store, type='lost')
        shelf_found = await dataset.shelf(store=store, type='found')

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        await dataset.stock(
            product_id=product1.product_id,
            count=10,
            reserve=0,
            shelf=shelf1,
            valid='2022-01-02',
            lot=uuid(),
        )
        await dataset.stock(
            product_id=product2.product_id,
            count=10,
            reserve=0,
            shelf=shelf2,
            valid='2022-01-02',
            lot=uuid(),
        )
        await dataset.stock(
            product_id=product3.product_id,
            count=10,
            reserve=0,
            shelf=shelf3,
            valid='2022-01-02',
            lot=uuid(),
        )

        await dataset.shelf(store=store, type='lost')

        acceptance_parent = await dataset.order(
            type='acceptance',
            store=store,
        )
        check_product_on_shelf_1 = await dataset.order(
            type='check',
            store=store,
            status='complete',
            estatus='done',
            parent=[acceptance_parent.order_id],
        )
        check_product_on_shelf_2 = await dataset.order(
            type='check',
            products=[product1.product_id],
            required=[
                {
                    'product_id': product1.product_id,
                    'shelf_id': shelf1.shelf_id,
                },
                {
                    'product_id': product2.product_id,
                    'shelf_id': shelf2.shelf_id,
                },
                {
                    'product_id': product3.product_id,
                    'shelf_id': shelf3.shelf_id,
                }
            ],
            store=store,
            status='reserving',
            estatus='begin',
            # как правило, при создании check_product_on_shelf
            # содержится весь список родителей и их родителей
            parent=[
                check_product_on_shelf_1.order_id,
                acceptance_parent.order_id
            ]
        )
        await wait_order_status(check_product_on_shelf_2,
                                ('request', 'waiting'))
        await check_product_on_shelf_2.ack(user)
        await wait_order_status(check_product_on_shelf_2,
                                ('processing', 'waiting'))
        await check_product_on_shelf_2.reload()
        tap.eq(len(check_product_on_shelf_2.problems),
               0, 'Проблем нет')

        suggests = await Suggest.list_by_order(check_product_on_shelf_2)
        tap.eq(len(suggests), 3, 'саджесты по числу required')

        with next(sug for sug in suggests
                  if sug.product_id == product1.product_id) as s:
            tap.ok(await s.done(count=4), 'закрыли саджест на меньшее')
            tap.ok(await s.reload(), 'перегружен саджест')
            tap.eq(s.status, 'done', 'статус')
            tap.eq(s.type, 'check', 'тип')

        with next(sug for sug in suggests
                  if sug.product_id == product2.product_id) as s:
            tap.ok(await s.done(count=10), 'закрыли саджест на ровно')
            tap.ok(await s.reload(), 'перегружен саджест')
            tap.eq(s.status, 'done', 'статус')
            tap.eq(s.type, 'check', 'тип')

        with next(sug for sug in suggests
                  if sug.product_id == product3.product_id) as s:
            tap.ok(await s.done(count=13), 'закрыли саджест на больше')
            tap.ok(await s.reload(), 'перегружен саджест')

        tap.ok(
            await check_product_on_shelf_2.done('complete', user=user),
            'ордер закрыт'
        )
        await wait_order_status(check_product_on_shelf_2, ('complete', 'done'))

        # Проверяем полку находок
        logs_found = await StockLog.list(
            conditions=[
                ('order_id', check_product_on_shelf_2.order_id),
                ('type', 'found')
            ],
            by='look',
        )
        tap.eq(len(logs_found.list), 1, "Нашли товар на полке")

        logs_found_put = await StockLog.list(
            by='look',
            conditions=[
                ('order_id', check_product_on_shelf_2.order_id),
                ('shelf_id', shelf_found.shelf_id),
            ],
        )
        tap.eq(len(logs_found_put.list), 0, 'Нет перемещений на found')

        stocks_found = await Stock.list(
            by='full',
            conditions=[
                ('shelf_id', shelf_found.shelf_id),
            ],
            sort=(),
        )
        tap.eq(len(stocks_found.list), 0, "Нет стока с типом found")

        # Проверяем полку потерь
        logs_lost = await StockLog.list(
            conditions=[
                ('order_id', check_product_on_shelf_2.order_id),
                ('type', 'lost')
            ],
            by='look',
        )
        tap.eq(len(logs_lost.list), 1, 'Есть потеря в документе')

        logs_lost_put = await StockLog.list(
            by='look',
            conditions=[
                ('order_id', check_product_on_shelf_2.order_id),
                ('shelf_id', shelf_lost.shelf_id),
            ],
        )
        tap.eq(len(logs_lost_put.list), 0, 'Нет перемещений на lost')

        stocks_lost = await Stock.list(
            by='full',
            conditions=[
                ('shelf_id', shelf_lost.shelf_id),
            ],
            sort=(),
        )
        tap.eq(len(stocks_lost.list), 0, "Нет стока с типом lost")


async def test_create_check_final(tap, dataset, wait_order_status, uuid):
    with tap.plan(23, 'проверяем создание директорского чека'):
        ps = sorted(
            [await dataset.product() for _ in range(5)],
            key=lambda x: x.product_id,
        )
        store = await dataset.full_store()
        shelves = [await dataset.shelf(store=store) for _ in range(2)]
        user = await dataset.user(store=store)

        for p in ps[:3]:
            await dataset.stock(
                shelf=shelves[0], product=p, count=123, lot=uuid()
            )
        await dataset.stock(
            shelf=shelves[1], product=ps[-1], count=123, lot=uuid()
        )
        await dataset.stock(
            shelf=shelves[1], product=ps[-2], count=123, lot=uuid()
        )

        shelf1_id, shelf2_id = shelves[0].shelf_id, shelves[1].shelf_id
        order = await dataset.order(
            type='check',
            store=store,
            status='reserving',
            estatus='begin',
            shelves=[shelf1_id, shelf1_id, shelf1_id, shelf2_id, shelf2_id],
            products=[p.product_id for p in ps],
            acks=[user.user_id],
        )

        await wait_order_status(
            order, ('processing', 'waiting'), user_done=user,
        )

        suggests = sorted(
            await Suggest.list_by_order(order), key=lambda x: x.product_id
        )
        tap.eq(len(suggests), 5, '5 саджестов')
        tap.ok(await suggests[0].done(), 'первый скипаем')
        tap.ok(
            await dataset.stock(
                shelf=shelves[0], product=ps[1], count=321, lot=uuid()
            ),
            'второй с ошибкой',
        )
        tap.ok(await suggests[2].done(count=69), 'третий пересчитываем')
        tap.ok(
            await dataset.stock(
                shelf=shelves[1], product=ps[3], count=321, lot=uuid()
            ),
            'четвертый по приколу с ошибкой',
        )
        tap.ok(
            await suggests[4].done(count=69), 'пятый по приколу пересчитываем'
        )

        await wait_order_status(
            order, ('complete', 'done'), user_done=user,
        )

        children = (await order.list(
            by='full',
            conditions=('parent', '[1]=', order.order_id),
            sort=(),
        )).list
        tap.eq(len(children), 2, 'двое деток')

        child_check = [x for x in children if x.type == 'check'][0]
        child_check_final = [x for x in children if x.type == 'check_final'][0]

        await wait_order_status(
            child_check, ('reserving', 'find_lost_and_found')
        )
        await wait_order_status(
            child_check_final, ('reserving', 'find_lost_and_found')
        )

        tap.eq(
            set(child_check.products),
            {p.product_id for p in (ps[1], ps[3])},
            'products те'
        )
        tap.eq(
            set(child_check.shelves),
            {s.shelf_id for s in shelves},
            'shelves те',
        )
        tap.eq(
            set(child_check_final.products),
            {p.product_id for p in (ps[2], ps[4])},
            'products те'
        )
        tap.eq(
            set(child_check_final.shelves),
            {s.shelf_id for s in shelves},
            'shelves те',
        )

        await wait_order_status(child_check, ('request', 'waiting'))
        await wait_order_status(child_check_final, ('request', 'waiting'))
        tap.ok(await child_check.ack(user), 'назначили юзера')
        tap.ok(await child_check_final.ack(user), 'назначили юзера')

        await wait_order_status(
            child_check, ('complete', 'done'), user_done=user
        )
        await wait_order_status(
            child_check_final, ('complete', 'done'), user_done=user
        )

        children = (await order.list(
            by='full',
            conditions=('parent', '[1]=', child_check.order_id),
            sort=(),
        )).list
        tap.eq(len(children), 0, 'нету деток')
        children = (await order.list(
            by='full',
            conditions=('parent', '[1]=', child_check_final.order_id),
            sort=(),
        )).list
        tap.eq(len(children), 0, 'нету деток')
