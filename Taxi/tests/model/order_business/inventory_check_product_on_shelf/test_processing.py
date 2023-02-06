import pytest

from stall.model.stock import Stock
from stall.model.stock_log import StockLog


# pylint: disable=too-many-locals
@pytest.mark.parametrize(
    'variant',
    [
        {
            'desc': 'Нет стоков',
            'stocks': [],
            'count': None,
            'done': 10,
            'valid': None,
            'count_stocks': 1,
        },
        {
            'desc': 'Нет стоков и на выходе нет товаров',
            'stocks': [],
            'count': 28,
            'done': 0,
            'valid': None,
            'count_stocks': 0,
        },

        {
            'desc': 'Один сток, увеличиваем склад',
            'stocks': [12],
            'count': 11,
            'done': 121,
            'valid': None,
            'count_stocks': 1,
        },
        {
            'desc': 'Пара стоков, увеличиваем склад',
            'stocks': [12, 17],
            'count': 11,
            'done': 100,
            'valid': '2022-01-01',
            'count_stocks': 2,
        },
        {
            'desc': 'Один сток, уменьшаем',
            'stocks': [122],
            'count': 122,
            'done': 100,
            'valid': None,
            'count_stocks': 1,
        },

        {
            'desc': 'Один сток столько же',
            'stocks': [122],
            'count': 122,
            'done': 122,
            'valid': None,
            'count_stocks': 1,
        },

        {
            'desc': 'три стока, меньше каждого',
            'stocks': [12, 15, 11],
            'count': 122,
            'done': 10,
            'valid': None,
            'count_stocks': 3,
        },
        {
            'desc': 'полка оказалась пустой после пересчета',
            'stocks': [312],
            'count': None,
            'done': None,
            'valid': None,
            'count_stocks': 1,
        },
    ]
)
# pylint: disable=too-many-statements
async def test_suggests(tap, dataset, wait_order_status, variant, uuid):
    with tap.plan(27, variant['desc']):
        store = await dataset.store(estatus='inventory')
        tap.ok(store, 'склад сгенерирован')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        product = await dataset.product()
        tap.ok(product, 'товар сгенерирован')

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка сгенерирована')

        tap.ok(await dataset.shelf(
            store=store,
            type='lost',
        ), 'полка lost')

        tap.ok(await dataset.shelf(
            store=store,
            type='found',
        ), 'полка found')

        with tap.subtest(None, 'Генерим стоки') as taps:
            for count in variant['stocks']:
                stock = await dataset.stock(
                    product_id=product.product_id,
                    count=count,
                    lot=uuid(),
                    store=store,
                    shelf=shelf,
                )
                taps.eq(stock.store_id, store.store_id, 'сгенерирован сток')
                taps.eq(stock.shelf_id, shelf.shelf_id, 'на полке')

        order = await dataset.order(
            store=store,
            type='inventory_check_product_on_shelf',
            required=[
                {
                    'shelf_id': shelf.shelf_id,
                    'product_id': product.product_id,
                    'count': variant['count'],
                }
            ],
            status='reserving',
            acks=[user.user_id],
        )
        tap.eq(order.store_id, store.store_id, 'ордер сгенерирован')
        tap.eq(order.fstatus, ('reserving', 'begin'), 'fstatus')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')

        with suggests[0] as s:
            tap.eq(s.type, 'check', 'проверка')
            tap.eq(s.order_id, order.order_id, 'order_id')
            tap.eq(s.store_id, store.store_id, 'store_id')
            tap.eq(s.product_id, product.product_id, 'product_id')

            tap.ok(s.conditions.all, 'conditions.all')
            tap.ok(s.conditions.editable, 'conditions.editable')
            tap.ok(not s.conditions.need_valid, 'conditions.need_valid')
            tap.eq(s.count, variant['count'], 'count из required')

            tap.ok(await s.done(count=variant['done'], valid=variant['valid']),
                   'Завершили саджест')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await Stock.list_by_product(
            product_id=product.product_id,
            store_id=order.store_id,
            shelf_id=shelf.shelf_id,
        )
        variant['done'] = variant['done'] or 0
        tap.eq(sum(s.count for s in stocks),
               variant['done'],
               'количество на складе')
        tap.eq(sum(s.reserve for s in stocks),
               0,
               'не зарезервировано')
        tap.eq(len(stocks),
               variant['count_stocks'],
               'количество остатков')

        # Проверяем полку находок
        if variant['done'] > sum(variant['stocks']):
            stocks = await Stock.list_by_product(
                product_id=product.product_id,
                store_id=store.store_id,
                shelf_type='found',
            )
            tap.eq(len(stocks), 1, "Длина")
            tap.eq(sum(s.count for s in stocks),
                   variant['done'] - sum(variant['stocks']),
                   'На полке находок')

            logs = await StockLog.list(
                conditions=[
                    ('order_id', order.order_id),
                    ('type', 'found')],
                by='look',
            )
            tap.eq(len(logs.list), 1, "Создан лог с типом found")
        elif variant['done'] < sum(variant['stocks']):
            # Проверяем полку потерь
            stocks = await Stock.list_by_product(
                product_id=product.product_id,
                store_id=store.store_id,
                shelf_type='lost',
            )

            tap.eq(sum(s.count for s in stocks),
                   sum(variant['stocks']) - variant['done'],
                   'На полке потерь')
            tap.eq(sum(s.reserve for s in stocks), 0, 'нет резерва')

            logs = await StockLog.list(
                conditions=[
                    ('order_id', order.order_id),
                    ('type', 'lost')],
                by='look',
            )
            tap.ne(len(logs.list), 0, "Создан лог с типом lost")
        elif variant['done'] == sum(variant['stocks']):
            tap.passed('')
            tap.passed('')
            tap.passed('')


async def test_weight_lost_and_found(tap, dataset, wait_order_status):
    with tap.plan(
        46,
        'Две весовые группы одного весового продукта '
        'можно перенести на полки lost и found'
    ):
        store = await dataset.store(estatus='inventory')
        tap.ok(store, 'склад сгенерирован')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь')

        store = await dataset.store(estatus='inventory')
        tap.eq(store.estatus, 'inventory', 'склад создан')

        children_weights = [
            [0, 10],
            [10, 20],
            [20, 30],
            [30, 40],
        ]

        _, *products = await dataset.weight_products(children=children_weights)
        tap.eq_ok(len(products), 4, '4 детей создано')

        shelves = [await dataset.shelf(store=store) for _ in range(4)]

        lost_shelf = await dataset.shelf(store=store, type='lost')
        found_shelf = await dataset.shelf(store=store, type='found')
        stocks_to_generate = [
            [products[0], shelves[0], 5],
            [products[1], shelves[1], 7],
            [products[2], shelves[2], 11],
            [products[3], shelves[3], 13],
        ]
        used = {}
        for product, shelf, count in stocks_to_generate:
            await dataset.stock(product=product, shelf=shelf,
                                store=store, count=count)
            used[(product.product_id, shelf.shelf_id)] = count

        stocks = {
            (s.product_id, s.shelf_id): s.count
            for s in await dataset.Stock.list(
                by='full',
                conditions=('store_id', store.store_id),
                sort=(),
            )
            if s.count
        }
        tap.eq_ok(stocks, used, 'стоки сгенерированы')

        found_on_shelf = [3, 3, 15, 15]
        for shelf, product, found_cnt in zip(shelves, products, found_on_shelf):
            order = await dataset.order(
                store=store,
                type='inventory_check_product_on_shelf',
                required=[
                    {
                        'shelf_id': shelf.shelf_id,
                        'product_id': product.product_id,
                        'count': stocks[(product.product_id, shelf.shelf_id)],
                    }
                ],
                status='reserving',
                acks=[user.user_id],
            )
            tap.eq(order.store_id, store.store_id, 'ордер сгенерирован')
            tap.eq(order.fstatus, ('reserving', 'begin'), 'fstatus')

            await wait_order_status(order, ('processing', 'waiting'))

            suggests = await dataset.Suggest.list_by_order(order)
            tap.eq(len(suggests), 1, 'один саджест сгенерирован')

            with suggests[0] as s:
                tap.eq(s.type, 'check', 'проверка')
                tap.eq(s.order_id, order.order_id, 'order_id')
                tap.eq(s.store_id, store.store_id, 'store_id')
                tap.eq(s.product_id, product.product_id, 'product_id')

                tap.ok(await s.done(count=found_cnt), 'Завершили саджест')

            await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = {
            (s.product_id, s.shelf_id): s.count
            for s in await dataset.Stock.list(
                by='full',
                conditions=('store_id', store.store_id),
                sort=(),
            )
            if s.count
        }

        lost_stocks = {
            (products[0].product_id, shelves[0].shelf_id): 3,
            (products[0].product_id, lost_shelf.shelf_id): 2,
            (products[1].product_id, shelves[1].shelf_id): 3,
            (products[1].product_id, lost_shelf.shelf_id): 4,
            (products[2].product_id, shelves[2].shelf_id): 15,
            (products[2].product_id, found_shelf.shelf_id): 4,
            (products[3].product_id, shelves[3].shelf_id): 15,
            (products[3].product_id, found_shelf.shelf_id): 2,
        }
        tap.eq_ok(stocks, lost_stocks,
                  'Две весовые группы успешно перенесены на полку lost'
                  'Две весовые группы успешно перенесены на полку found')
