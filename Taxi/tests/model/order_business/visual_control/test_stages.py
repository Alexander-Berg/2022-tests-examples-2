async def test_flow(tap, dataset, wait_order_status):
    with tap.plan(25, 'сначала делаем фейсконтроль, потом перекладку на треш'):
        banana = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )
        apple = await dataset.product(
            vars={'imported': {'visual_control': True}},
        )

        store = await dataset.store()

        trash = await dataset.shelf(type='trash', store=store)
        tap.eq(trash.store_id, store.store_id, 'создали полку списания')

        shelf1 = await dataset.shelf(store=store)
        tap.eq(shelf1.store_id, store.store_id, 'создали полку 1')

        shelf2 = await dataset.shelf(store=store)
        tap.eq(shelf2.store_id, store.store_id, 'создали полку 2')

        stocks_banana = await dataset.stock(
            product=banana, shelf=shelf1, count=3,
        )
        stocks_apple = await dataset.stock(
            product=apple, shelf=shelf2, count=5,
        )

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'создали пользователя')

        order = await dataset.order(
            store=store,
            type='visual_control',
            status='processing',
            estatus='begin',
            acks=[user.user_id],
            required=[
                {
                    'product_id': banana.product_id,
                    'shelf_id': shelf1.shelf_id,
                },
                {
                    'product_id': apple.product_id,
                    'shelf_id': shelf2.shelf_id,
                },
            ],
        )

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'visual_control', 'этап фейсконтроля')

        suggests = {
            (s.product_id, s.shelf_id): s
            for s in await dataset.Suggest.list_by_order(
                order, types='shelf2box', status='request',
            )
        }
        tap.eq(len(suggests), 2, '2 саджеста на проверку')

        await suggests[(banana.product_id, shelf1.shelf_id)].done(count=3)
        await suggests[(apple.product_id, shelf2.shelf_id)].done(count=5)

        # параллельный ордер за бананами
        order2 = await dataset.order(
            store=store,
            acks=[user.user_id],
            required=[
                {'product_id': banana.product_id, 'count': 3},
            ]
        )
        await wait_order_status(order2, ('approving', 'waiting'))

        # перетряхиваем ордер фейсконтроля
        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()
        tap.eq(order.vars('stage'), 'visual_control', 'этап фейсконтроля')
        tap.eq(order.vars('suggests_write_off'), False, 'нет саджестов на треш')

        suggests = {
            (s.product_id, s.shelf_id): s
            for s in await dataset.Suggest.list_by_order(
                order, types='shelf2box', status='done',
            )
        }
        tap.eq(len(suggests), 2, '2 саджеста на проверку закрыты')
        tap.eq(
            suggests[(banana.product_id, shelf1.shelf_id)].vars('reserves'),
            {stocks_banana.stock_id: 0},
            'нет резерва на бананы по фейсконтролю',
        )
        tap.eq(
            suggests[(apple.product_id, shelf2.shelf_id)].vars('reserves'),
            {stocks_apple.stock_id: 5},
            'есть резерв по яблокам по фейсконтролю',
        )

        suggests = {
            (s.product_id, s.shelf_id): s
            for s in await dataset.Suggest.list_by_order(
                order, types='box2shelf', status='request',
            )
        }
        tap.eq(len(suggests), 1, '1 саджест на возврат товаров на полку')
        tap.eq(
            suggests[(banana.product_id, shelf1.shelf_id)].vars('stage'),
            'visual_control',
            'все еще фейсконтроль',
        )
        tap.eq(
            suggests[(banana.product_id, shelf1.shelf_id)].count,
            3,
            'все бананы верните назад',
        )

        await suggests[(banana.product_id, shelf1.shelf_id)].done(count=3)

        tap.ok(
            await order.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        await order.reload()
        tap.eq(order.vars('suggests_write_off'),
               True,
               'Cаджесты на треш сгенерированы'
               )
        tap.eq(order.vars('stage'), 'trash', 'этап раскладки на треш')

        suggests = {
            (s.product_id, s.shelf_id): s
            for s in await dataset.Suggest.list_by_order(
                order, types='box2shelf', status='request',
            )
        }
        tap.eq(len(suggests), 1, '1 саджест на треш')
        tap.eq(
            suggests[(apple.product_id, trash.shelf_id)].count,
            5,
            'все яблоки',
        )
        tap.eq(
            suggests[(apple.product_id, trash.shelf_id)].vars('stage'),
            'trash',
            'треш',
        )
        tap.eq(
            suggests[(apple.product_id, trash.shelf_id)].vars('reserves'),
            {stocks_apple.stock_id: 5},
            'яблочные стоки',
        )
