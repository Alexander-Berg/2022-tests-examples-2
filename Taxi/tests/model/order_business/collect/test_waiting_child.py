async def test_waiting_child(tap, dataset, wait_order_status):
    with tap.plan(34):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        stock = await dataset.stock(store=store, product=product, count=77)
        tap.eq(stock.store_id, store.store_id, 'остаток создан')
        tap.eq(stock.product_id, product.product_id, 'товар')
        tap.eq(stock.left, 77, 'свободно')

        order = await dataset.order(
            type='collect',
            required=[{'product_id': product.product_id, 'count': 27}],
            store=store,
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('processing', 'waiting_stocks'))
        tap.eq(
            await order.business.make_wave(),
            1,
            'создана волна из одного ордера'
        )
        await wait_order_status(order, ('processing', 'waiting_stocks'))
        await wait_order_status(order, ('processing', 'waiting_stocks'))

        move = await dataset.Order.list(
            by='full',
            conditions=(
                ('store_id', store.store_id),
                ('type', 'hand_move'),
                ('status', ('reserving', 'approving', 'processing'))
            ),
            sort=(),
        )
        tap.eq(len(move.list), 1, 'один ордер создан')
        with move.list[0] as moving:
            await wait_order_status(moving, ('request', 'waiting'))
            tap.ok(await moving.ack(user), 'ack')
            await wait_order_status(moving, ('processing', 'waiting'))
            suggests = await dataset.Suggest.list_by_order(moving)
            for s in suggests:
                await s.done(user=user)
            await moving.signal(
                {'type': 'next_stage'},
                user=user,
            )
            await wait_order_status(
                moving,
                ('complete', 'done'),
                user_done=user
            )

        await wait_order_status(order, ('complete', 'waiting_child_order'))
        await wait_order_status(order, ('complete', 'waiting_child_order'))

        shelf = await dataset.Shelf.load(order.vars('shelf'))
        tap.eq(shelf.store_id, store.store_id, 'назначенная полка выбрана')
        tap.eq(shelf.order_id, order.order_id, 'ордер назначения в ней есть')
        tap.ok(order.vars('child_order_id', None), 'дочерний ID ордера')

        child = await dataset.Order.load(order.vars('child_order_id'))
        tap.eq(child.store_id, store.store_id, 'дочерний ордер создан')
        tap.eq(child.type, 'shipment', 'отправка')
        tap.eq(len(child.required), 1, 'required')
        with child.required[0] as r:
            tap.eq(r.product_id, product.product_id, 'товар в required')
            tap.eq(r.count, 27, 'количество')
            tap.eq(r.price_type, 'collection', 'price_type')
            tap.eq(r.shelf_id, shelf.shelf_id, 'полка')

        await wait_order_status(child, ('request', 'waiting'))
        tap.ok(await child.ack(user), 'ack')
        await wait_order_status(child, ('complete', 'done'), user_done=user)

        await wait_order_status(order, ('complete', 'done'))
        tap.ok(await shelf.reload(), 'полка перегружена')
        tap.eq(shelf.order_id, None, 'назначение ордера убрано')
