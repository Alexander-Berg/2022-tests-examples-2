# pylint: disable=too-many-statements
from stall.model.shelf import Shelf
from stall.model.suggest import Suggest


# pylint: disable=expression-not-assigned
async def test_trash(tap, dataset, wait_order_status):
    with tap.plan(74, 'Списание'):
        store = await dataset.full_store(options={'exp_chicken_run': True})
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        parent, *products = await dataset.weight_products(
            children=[[0, 100], [100, 200], [200, 300], ]
        )
        tap.ok(products, 'товар создан')

        shelves = [await dataset.shelf(store=store) for s in range(5)]
        tap.eq(len(shelves), 5, 'несколько полок создано')
        # TODO 2 продукта и закрыть последний н 0
        order = await dataset.order(
            store=store,
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': parent.product_id,
                    'count': 15,
                    'weight': 100
                }
            ],
        )
        tap.ok(order, 'ордер создан')
        await wait_order_status(
            order,
            ('request', 'waiting'),
            tap=tap
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            tap=tap
        )

        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест')

        with suggests[0] as s:
            tap.eq(s.product_id, parent.product_id, 'product_id')
            tap.eq(s.type, 'shelf2box', 'type')

            loaded_shelf = await Shelf.load(s.shelf_id)
            tap.eq(loaded_shelf.type, 'incoming', 'с полки incoming')
            tap.eq(s.store_id, store.store_id, 'store_id')
            tap.eq(s.order_id, order.order_id, 'order_id')
            tap.eq(s.count, 15, 'count')
            tap.eq(s.weight, None, 'weight')

            tap.eq(s.conditions.all, True, 'all')
            tap.eq(s.conditions.need_weight, True, 'need_weight')
            tap.eq(
                s.conditions.weight_aggregate,
                True,
                'weight_aggregate'
            )
            tap.ok(await s.done(count=10, weight=10), 'закрыли count=10')

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            tap=tap
        )
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест b2s')
        with suggests[0] as s:
            tap.eq(s.type, 'box2shelf', 'type')
            loaded_shelf = await Shelf.load(s.shelf_id)
            tap.eq(loaded_shelf.type, 'store', 'на полку store')

            tap.eq(s.product_id, products[0].product_id, 'product_id')
            tap.eq(s.count, 10, 'count')
            tap.eq(s.weight, 10, 'weight')

            tap.ok(await s.done(count=10, weight=10), 'закрыли count=10')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(
            await order.signal({'type': 'sale_stowage'}),
            'сигнал sale_stowage'
        )
        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(
            order.signals[order.vars['signo']].type,
            'sale_stowage',
            'сигнал sale_stowage'
        )
        tap.ok(
            order.signals[order.vars['signo']].done is not None,
            'сигнал sale_stowage закрыт'
        )

        tap.eq(order.vars('stage'), 'trash', 'stage')

        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request'
        )
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')

        with suggests[0] as s:
            loaded_shelf = await Shelf.load(s.shelf_id)
            tap.eq(loaded_shelf.type, 'incoming', 'с полки incoming')
            tap.eq(s.product_id, parent.product_id, 'product_id')
            tap.eq(s.type, 'shelf2box', 'type')
            tap.eq(s.store_id, store.store_id, 'store_id')
            tap.eq(s.order_id, order.order_id, 'order_id')
            tap.eq(s.vars['stage'], 'trash', 'саджест на треш')

            tap.eq(s.count, 5, 'count')
            tap.eq(s.weight, None, 'weight')

            tap.eq(s.conditions.all, True, 'all')
            tap.eq(s.conditions.need_weight, True, 'need_weight')
            tap.eq(
                s.conditions.weight_aggregate,
                True,
                'weight_aggregate'
            )
            with tap.raises(
                    Suggest.ErSuggestErrorDenided,
                    'саджесты b2s в еррор закрывать нельзя',
            ):
                await s.done(
                    'error',
                    reason={
                        'code': 'LIKE_SHELF',
                        'shelf_id': shelves[0].shelf_id,
                    },
                )
            tap.ok(await s.done(count=5, weight=5), 'закрыт в 5')

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            tap=tap
        )
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест')
        # проверки значение
        with suggests[0] as s:
            tap.eq(s.type, 'box2shelf', 'type')
            loaded_shelf = await Shelf.load(s.shelf_id)
            tap.eq(loaded_shelf.type, 'trash', 'на полку trash')

            tap.eq(s.vars['stage'], 'trash', 'stage')
            tap.eq(s.product_id, products[0].product_id, 'product_id')
            tap.eq(s.count, 5, 'count')
            tap.eq(s.weight, 5, 'weight')

            tap.ok(await s.done(count=5, weight=5), 'закрыли count=5')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request'
        )
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')
        with suggests[0] as s:
            loaded_shelf = await Shelf.load(s.shelf_id)
            tap.eq(loaded_shelf.type, 'incoming', 'с полки incoming')

            await s.done(count=0, weight=0)

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=(('store_id', store.store_id),),
            sort=(),
        )
        tap.eq(len(stocks.list), 2, 'Остатки')
        with next(sl for sl in stocks if sl.shelf_type == 'trash') as s:
            tap.eq(len(s.vars['reasons']), 1, 'Записана причина')
            tap.eq(
                s.vars['reasons'][0][order.order_id]['reason_code'],
                'TRASH_DECAYED',
                'Код записан'
            )
            tap.eq(s.shelf_type, 'trash', 'остаток на списании')
            tap.eq(s.count, 5, 'количество')
            tap.eq(s.vars['weight'], 5, 'weight')
            tap.eq(s.product_id, products[0].product_id, 'товар')

        with next(sl for sl in stocks if sl.shelf_type == 'store') as s:
            tap.eq(s.shelf_type, 'store', 'остаток на списании')
            tap.eq(s.count, 10, 'количество')
            tap.eq(s.vars['weight'], 10, 'weight')
            tap.eq(s.product_id, products[0].product_id, 'товар')

        await order.reload()
        tap.eq(len(order.required), 1, 'один required')
        tap.eq(order.required[0]['result_count'],
               15,
               'result_count в required')
        tap.eq(order.required[0]['result_weight'],
               15,
               'result_weight в required')


async def test_trash_more_signal(tap, dataset, wait_order_status):
    with tap.plan(67, 'Списание'):
        store = await dataset.full_store(
            options={'exp_chicken_run': True}
        )
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        parent, *products = await dataset.weight_products(
            children=[[0, 100], [100, 200], [200, 300], ]
        )
        tap.ok(products, 'товар создан')

        shelves = [await dataset.shelf(store=store) for s in range(5)]
        tap.eq(len(shelves), 5, 'несколько полок создано')
        order = await dataset.order(
            store=store,
            type='weight_stowage',
            acks=[user.user_id],
            required=[
                {
                    'product_id': parent.product_id,
                    'count': 15,
                    'weight': 100
                }
            ],
        )
        tap.ok(order, 'ордер создан')
        await wait_order_status(
            order,
            ('request', 'waiting'),
            tap=tap
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            tap=tap
        )

        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест')

        with suggests[0] as s:
            tap.eq(s.product_id, parent.product_id, 'product_id')
            tap.eq(s.type, 'shelf2box', 'type')
            tap.eq(s.store_id, store.store_id, 'store_id')
            tap.eq(s.order_id, order.order_id, 'order_id')
            tap.eq(s.count, 15, 'count')
            tap.eq(s.weight, None, 'weight')

            tap.eq(s.conditions.all, True, 'all')
            tap.eq(s.conditions.need_weight, True, 'need_weight')
            tap.eq(
                s.conditions.weight_aggregate,
                True,
                'weight_aggregate'
            )
            tap.ok(await s.done(count=10, weight=10), 'закрыли count=10')

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            tap=tap
        )
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест b2s')
        with suggests[0] as s:
            tap.eq(s.type, 'box2shelf', 'type')
            tap.eq(s.product_id, products[0].product_id, 'product_id')
            tap.eq(s.count, 10, 'count')
            tap.eq(s.weight, 10, 'weight')

            tap.ok(await s.done(count=10, weight=10), 'закрыли count=10')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(
            await order.signal({'type': 'sale_stowage'}),
            'сигнал sale_stowage'
        )
        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(order.vars('stage'), 'trash', 'stage')

        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request'
        )
        with suggests[0] as s:
            tap.eq(s.product_id, parent.product_id, 'product_id')
            tap.eq(s.type, 'shelf2box', 'type')
            tap.eq(s.store_id, store.store_id, 'store_id')
            tap.eq(s.order_id, order.order_id, 'order_id')
            tap.eq(s.count, 5, 'count')
            tap.eq(s.weight, None, 'weight')
            await s.done(count=0, weight=0)

        tap.ok(await order.signal(
            {
                'type': 'more_product',
                'data': {
                    'product_id': parent.product_id,
                    'count': 5,
                    'weight': 5
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
            status='request'
        )
        tap.eq(len(suggests), 1, 'саджест сгенерирован')
        with suggests[0] as s:
            loaded_shelf = await Shelf.load(s.shelf_id)
            tap.eq(loaded_shelf.type, 'incoming', 'с полки incoming')

            tap.eq(s.vars['stage'], 'trash', 'stage')
            await s.done(count=5, weight=5)

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            tap=tap
        )
        suggests = await dataset.Suggest.list_by_order(order, status='request')
        tap.eq(len(suggests), 1, 'один саджест')
        # проверки значение
        with suggests[0] as s:
            tap.eq(s.vars['stage'], 'trash', 'stage')
            tap.eq(s.type, 'box2shelf', 'type')
            tap.eq(s.product_id, products[0].product_id, 'product_id')
            tap.eq(s.count, 5, 'count')
            tap.eq(s.weight, 5, 'weight')

            tap.ok(await s.done(count=5, weight=5), 'закрыли count=5')

        await wait_order_status(order, ('processing', 'waiting'))
        suggests = await dataset.Suggest.list_by_order(
            order,
            status='request'
        )
        tap.eq(len(suggests), 1, 'один саджест сгенерирован')
        with suggests[0] as s:
            await s.done(count=0, weight=0)

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        stocks = await dataset.Stock.list(
            by='full',
            conditions=(('store_id', store.store_id),),
            sort=(),
        )

        tap.eq(len(stocks.list), 2, 'Остатки')

        with next(sl for sl in stocks if sl.shelf_type == 'trash') as s:
            tap.eq(len(s.vars['reasons']), 1, 'Записана причина')
            tap.eq(
                s.vars['reasons'][0][order.order_id]['reason_code'],
                'TRASH_DECAYED',
                'Код записан'
            )
            tap.eq(s.shelf_type, 'trash', 'остаток на списании')
            tap.eq(s.count, 5, 'количество')
            tap.eq(s.vars['weight'], 5, 'weight')
            tap.eq(s.product_id, products[0].product_id, 'товар')

        with next(sl for sl in stocks if sl.shelf_type == 'store') as s:
            tap.eq(s.shelf_type, 'store', 'остаток на списании')
            tap.eq(s.count, 10, 'количество')
            tap.eq(s.vars['weight'], 10, 'weight')
            tap.eq(s.product_id, products[0].product_id, 'товар')

        await order.reload()
        tap.eq(len(order.required), 1, 'один required')
        tap.eq(order.required[0]['result_count'],
               15,
               'result_count в required')
        tap.eq(order.required[0]['result_weight'],
               15,
               'result_weight в required')
