# pylint: disable=too-many-statements,too-many-locals
from stall.model.shelf import Shelf


async def test_weight_more_product(tap, dataset, wait_order_status):
    with tap.plan(39, 'Тесты more_product'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        child_weights = [
            [0, 10],
            [10, 20],
            [20, 30]
        ]

        parent, *products = await dataset.weight_products(
            children=child_weights
        )
        tap.eq(len([parent]+products), 4, '3 детей + родитель')

        parent_2, *products_2 = await dataset.weight_products()
        tap.eq(len([parent_2]+products_2), 4, '3 детей+ родитель другой группы')

        shelves = [await dataset.shelf(store=store) for s in range(5)]
        tap.eq(len(shelves), 5, 'несколько полок создано')

        order = await dataset.order(
            store=store,
            type='weight_stowage',
            status='processing',
            estatus='waiting',
            acks=[user.user_id],
            required=[
                {
                    'product_id': parent.product_id,
                    'weight': 5000,
                    'count': 4,
                }
            ],
            vars={
                'stage': 'stowage',
                'signo': -1,
                'suggest_mode': 'processing',
            }
        )
        tap.ok(order, 'Ордер раскладки создан')
        # создадим реквестный саджест
        shelves = await Shelf.list_by_store(
            store_id=order.store_id,
            type='incoming',
            db={'mode': 'slave'},
        )
        tap.ne(len(shelves), 0, 'есть полка приемки')
        suggest = await dataset.suggest(
            type='shelf2box',
            product_id=parent.product_id,
            store_id=order.store_id,
            order=order,
            shelf_id=shelves[0].shelf_id,
            count=4,
            weight=None,
            conditions={
                'error': False,
                'all': True,
                'need_weight': True,
                'weight_aggregate': True,
            },

            vars={
                'mode': 'product',
                'children': [],
                'stage': 'stowage',
            }
        )

        tap.ok(suggest, 'Саджест создан')

        tap.note('Саджест не обновился так как продукт не из required')
        tap.ok(await order.signal(
            {
                'type': 'more_product',
                'data': {
                    'product_id': parent_2.product_id,
                    'count': 1,
                    'weight': 1,
                }
            }), 'сигнал more_product')

        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(
            order.signals[order.vars['signo']].type,
            'more_product',
            'сигнал more_product'
        )
        tap.ok(
            order.signals[order.vars['signo']].done is not None,
            'сигнал more_product закрыт'
        )
        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['shelf2box'],
            status='request',
        )
        tap.eq(len(suggests), 1, 'Саджестов не создалось')
        with suggests[0] as s:
            tap.eq(s.weight, None, 'Вес не изменился')
            tap.eq(s.count, 4, 'Число не изменилось')
            tap.eq(s.product_id,
                   parent.product_id,
                   'Родитель не изменился'
                   )

        tap.note('Саджест не изменился,'
                 'так как прислали more_product с правильным родителем')
        tap.ok(await order.signal(
            {
                'type': 'more_product',
                'data': {
                    'product_id': parent.product_id,
                    'count': 4,
                    'weight': 4,
                }
            }), 'сигнал more_product')

        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(
            order.signals[order.vars['signo']].type,
            'more_product',
            'сигнал more_product'
        )
        tap.ok(
            order.signals[order.vars['signo']].done is not None,
            'сигнал more_product закрыт'
        )
        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['shelf2box'],
            status='request',
        )
        tap.eq(len(suggests), 1, 'Саджестов не создалось')
        with suggests[0] as s:
            tap.eq(s.weight, None, 'Вес изменился')
            tap.eq(s.count, 4, 'Число изменилось')
            tap.eq(s.product_id,
                   parent.product_id,
                   'Родитель не изменился'
                   )
            tap.ok(await s.done(count=4, weight=15), 'закрыли count=4')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests_b2s = await dataset.Suggest.list_by_order(
            order,
            types=['box2shelf'],
            status='request',
        )
        tap.eq(len(suggests_b2s), 1, 'Саджестов положи на полку')

        with suggests_b2s[0] as s:
            tap.eq(s.product_id, products[1].product_id, 'Правильный продукт')
            tap.eq(s.weight, 15, 'Вес 15')
            tap.eq(s.count, 4, 'Число 4')
            tap.ok(await s.done(count=4, weight=15), 'закрыли count=4')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(
            order,
            types=['shelf2box'],
            status='request',
        )
        tap.eq(len(suggests), 1, 'Саджестов взять с полки')

        with suggests[0] as s:
            await s.done(count=0, weight=0)

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=(('store_id', store.store_id),),
            sort=(),
        )

        tap.eq(len(stocks.list), 1, 'Остатки')
        with [s for s in stocks
              if s.product_id == products[1].product_id][0] as s:
            tap.eq(s.shelf_type, 'store', 'остаток на полке')
            tap.eq(s.count, 4, 'количество')
            tap.eq(s.vars['weight'], 15, 'weight')
            tap.eq(s.reserve, 0, 'нет резерва')


async def test_weight_more_product_same(
        tap, dataset, wait_order_status,):
    with tap.plan(20, 'Тесты more_product c разными вариациями'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        child_weights = [
            [0, 10],
            [10, 20],
            [20, 30]
        ]

        parent, *products = await dataset.weight_products(
            children=child_weights
        )
        tap.eq(len([parent] + products), 3 + 1, '3 детей и родитель')

        parent_2, *products_2 = await dataset.weight_products()
        tap.eq(len([parent_2]+products_2),
               3 + 1,
               '3 детей и родитель другой группы')

        shelves = [await dataset.shelf(store=store) for s in range(5)]
        tap.eq(len(shelves), 5, 'несколько полок создано')

        order = await dataset.order(
            store=store,
            type='weight_stowage',
            status='processing',
            estatus='waiting',
            acks=[user.user_id],
            required=[
                {
                    'product_id': parent.product_id,
                    'weight': 5000,
                    'count': 8
                }
            ],
            vars={
                'stage': 'stowage',
                'signo': -1,
                'suggest_mode': 'processing',
            }
        )
        tap.ok(order, 'Ордер раскладки создан')
        # создадим реквестный саджест
        shelves = await Shelf.list_by_store(
            store_id=order.store_id,
            type='incoming',
            db={'mode': 'slave'},
        )
        tap.ne(len(shelves), 0, 'есть полка приемки')
        suggest = await dataset.suggest(
            type='shelf2box',
            product_id=parent.product_id,
            store_id=order.store_id,
            order=order,
            shelf_id=shelves[0].shelf_id,
            count=8,
            weight=None,
            conditions={
                'error': False,
                'all': True,
                'need_weight': True,
                'weight_aggregate': True,
            },

            vars={
                'mode': 'product',
                'children': [],
                'stage': 'stowage',
            }
        )

        tap.ok(suggest, 'Саджест создан')
        for i in range(0, 2):
            with tap.subtest(15, 'несколько more_product') as taps:
                taps.ok(await order.signal(
                    {
                        'type': 'more_product',
                        'data': {
                            'product_id': parent.product_id,
                            'count': 4,
                            'weight': 4,
                        }
                    }), 'сигнал more_product')

                await wait_order_status(order, ('processing', 'waiting'),
                                        tap=taps)
                tap.eq(
                    order.signals[order.vars['signo']].type,
                    'more_product',
                    'сигнал more_product'
                )
                tap.ok(
                    order.signals[order.vars['signo']].done is not None,
                    'сигнал more_product закрыт'
                )
                suggests = await dataset.Suggest.list_by_order(
                    order,
                    types=['shelf2box'],
                    status='request',
                )
                taps.eq(len(suggests), 1, 'Саджестов не создалось')
                with suggests[0] as s:
                    taps.eq(s.weight, None, 'Вес изменился')
                    taps.eq(s.count, 8 - i*4, 'Число изменилось')
                    taps.eq(s.product_id,
                            parent.product_id,
                            'Родитель не изменился'
                            )
                    taps.ok(await s.done(count=4, weight=15), 'закрыли count=4')

                await wait_order_status(order, ('processing', 'waiting'),
                                        tap=taps)
                suggests_b2s = await dataset.Suggest.list_by_order(
                    order,
                    types=['box2shelf'],
                    status='request',
                )
                taps.eq(len(suggests_b2s), 1, 'Саджестов положи на полку')

                with suggests_b2s[0] as s:
                    taps.eq(s.product_id, products[1].product_id,
                            'Правильный продукт')
                    taps.eq(s.weight, 15, 'Вес 15')
                    taps.eq(s.count, 4, 'Число 4')
                    taps.ok(await s.done(count=4, weight=15), 'закрыли count=4')

                await wait_order_status(order, ('processing', 'waiting'),
                                        tap=taps)
                suggests = await dataset.Suggest.list_by_order(
                    order,
                    types=['shelf2box'],
                    status='request',
                )
                taps.eq(len(suggests), 1, 'Саджестов взять с полки')

        with suggests[0] as s:
            await s.done(count=0, weight=0)

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=(('store_id', store.store_id),),
            sort=(),
        )

        tap.eq(len(stocks.list), 1, 'Остатки')
        with [s for s in stocks
              if s.product_id == products[1].product_id][0] as s:
            tap.eq(s.shelf_type, 'store', 'остаток на полке')
            tap.eq(s.count, 8, 'количество')
            tap.eq(s.vars['weight'], 30, 'weight')
            tap.eq(s.reserve, 0, 'нет резерва')
