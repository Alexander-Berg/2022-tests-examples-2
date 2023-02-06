async def test_simple(tap, dataset, wait_order_status):
    with tap.plan(10, 'Отмена до взятия'):
        store = await dataset.store(type='dc')
        user = await dataset.user(store_id=store.store_id)
        rack = await dataset.rack(store_id=store.store_id)
        cargo = await dataset.shelf(
            store_id=store.store_id,
            rack_id=rack.rack_id,
            type='cargo',
        )
        new_rack = await dataset.rack(store_id=store.store_id)

        order = await dataset.order(
            store=store,
            type='cargo_move',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'shelf_id': cargo.shelf_id,
                    'dst_rack_id': new_rack.rack_id,
                }
            ],
            acks=[user.user_id]
        )
        tap.ok(
            await wait_order_status(order, ('processing', 'waiting')),
            'Дотолкали ордер до processing'
        )
        suggests = await dataset.Suggest.list_by_order(
            order=order, status='request')
        tap.eq(len(suggests), 1, 'Саджест только один')
        tap.ok(
            await order.cancel(user=user),
            'Отменили заказ'
        )
        tap.ok(
            await wait_order_status(order, ('canceled', 'done')),
            'Дотолкали ордер canceled'
        )
        tap.ok(await cargo.reload(), 'Перезабрали груз')
        tap.eq(cargo.rack_id, rack.rack_id, 'Груз в старом месте')
        tap.eq(
            cargo.order_id,
            None,
            'Нет заказа'
        )
        reserved_racks = await dataset.Rack.list_by_order(order=order)
        tap.eq(
            len(reserved_racks),
            0,
            'нет резервов в стеллажах'
        )


async def test_after_take(tap, dataset, wait_order_status):
    with tap.plan(20, 'Отмена после взятия'):
        store = await dataset.store(type='dc')
        user = await dataset.user(store_id=store.store_id)
        rack = await dataset.rack(store_id=store.store_id)
        cargo = await dataset.shelf(
            store_id=store.store_id,
            rack_id=rack.rack_id,
            type='cargo',
        )
        new_rack = await dataset.rack(store_id=store.store_id)

        order = await dataset.order(
            store=store,
            type='cargo_move',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'shelf_id': cargo.shelf_id,
                    'dst_rack_id': new_rack.rack_id,
                }
            ],
            acks=[user.user_id]
        )
        tap.ok(
            await wait_order_status(order, ('processing', 'waiting')),
            'Дотолкали ордер до processing'
        )
        suggests = await dataset.Suggest.list_by_order(
            order=order, status='request')
        tap.eq(len(suggests), 1, 'Саджест только один')
        suggest = suggests[0]
        tap.ok(await suggest.done(user=user), 'Закрыли саджест взятия')
        tap.ok(
            await order.cancel(user=user),
            'Отменили заказ'
        )
        tap.ok(
            await wait_order_status(order, ('processing', 'waiting')),
            'Дотолкали ордер'
        )
        tap.ok(
            await wait_order_status(order, ('processing', 'waiting')),
            'Дотолкали ордер c генерацией'
        )
        suggests = await dataset.Suggest.list_by_order(
            order=order, status='request')
        tap.eq(len(suggests), 1, 'Саджест только один')
        suggest = suggests[0]
        tap.eq(suggest.type, 'put_cargo', 'Саджест на возврат')
        tap.eq(suggest.shelf_id, cargo.shelf_id, 'Груз тот')
        tap.eq(suggest.rack_id, rack.rack_id, 'Вернуть обратно')
        tap.ok(await suggest.done(user=user), 'Закрыли саджест взятия')
        tap.ok(
            await wait_order_status(order, ('canceled', 'done')),
            'Дотолкали ордер canceled'
        )
        tap.ok(await cargo.reload(), 'Перезабрали груз')
        tap.eq(cargo.rack_id, rack.rack_id, 'Груз в старом месте')
        tap.eq(
            cargo.order_id,
            None,
            'Нет заказа'
        )
        reserved_racks = await dataset.Rack.list_by_order(order=order)
        tap.eq(
            len(reserved_racks),
            0,
            'нет резервов в стеллажах'
        )
