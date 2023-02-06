async def test_simple(tap, dataset, wait_order_status):
    with tap.plan(19, 'Все идет по плану по стеллажу'):
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
        tap.ok(
            await suggest.done(user=user),
            'Закрыли саджест'
        )
        tap.ok(
            await wait_order_status(order, ('processing', 'waiting')),
            'Дотолкали ордер снова'
        )
        suggests = await dataset.Suggest.list_by_order(
            order=order, status='request')
        tap.eq(len(suggests), 1, 'Саджест только один')
        suggest = suggests[0]
        tap.eq(suggest.type, 'put_cargo', 'Саджест положить груз')
        tap.ok(await suggest.done(user=user), 'Закрыли саджест')
        tap.ok(
            await order.done(target='complete', user=user),
            'Закрыли документ'
        )
        tap.ok(
            await wait_order_status(order, ('complete', 'done')),
            'Дотолкали ордер до конца'
        )
        tap.ok(await cargo.reload(), 'Перезабрали груз')
        tap.eq(cargo.rack_id, new_rack.rack_id, 'Груз теперь тут')
        tap.eq(
            cargo.order_id,
            None,
            'Нет заказа'
        )
        tap.ok(await new_rack.reload(), 'Перезабрали стеллаж')
        tap.eq(new_rack.count, 1, 'Теперь содержит 1')
        reserved_racks = await dataset.Rack.list_by_order(order=order)
        tap.eq(
            len(reserved_racks),
            0,
            'нет резервов в стеллажах'
        )
        children_orders = await order.get_descendants()
        tap.eq(len(children_orders), 0, 'нет дочерних документов')


async def test_spawn_child(tap, dataset, wait_order_status):
    # pylint: disable=too-many-locals
    with tap.plan(24, 'Создание дочернего документа'):
        store = await dataset.store(type='dc')
        user = await dataset.user(store_id=store.store_id)
        rack = await dataset.rack(store_id=store.store_id)
        cargo = await dataset.shelf(
            store_id=store.store_id,
            rack_id=rack.rack_id,
            type='cargo',
        )
        new_rack = await dataset.rack(store_id=store.store_id)
        another_rack = await dataset.rack(store_id=store.store_id)

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
        tap.eq(suggest.type, 'take_cargo', 'Саджест взять груз')
        tap.ok(await suggest.done(user=user), 'Закрыли саджест')
        tap.ok(
            await wait_order_status(order, ('processing', 'waiting')),
            'Дотолкали ордер снова'
        )
        suggests = await dataset.Suggest.list_by_order(
            order=order, status='request')
        tap.eq(len(suggests), 1, 'Саджест только один')
        suggest = suggests[0]
        tap.eq(suggest.type, 'put_cargo', 'Саджест положить груз')
        tap.ok(
            await suggest.done(user=user, status='error', reason={
                'code': 'LIKE_RACK',
                'rack_id': another_rack.rack_id
            }),
            'Закрыли саджест в ошибку'
        )
        tap.ok(
            await wait_order_status(order, ('processing', 'waiting')),
            'Дотолкали ордер снова'
        )
        suggests = await dataset.Suggest.list_by_order(
            order=order, status='request')
        tap.eq(len(suggests), 1, 'Саджест только один')
        new_suggest = suggests[0]
        tap.ok(await new_suggest.done(user=user), 'Закрыли саджест')
        tap.ok(
            await order.done(target='complete', user=user),
            'Закрыли документ'
        )
        tap.ok(
            await wait_order_status(order, ('complete', 'done')),
            'Дотолкали ордер до конца'
        )
        children_orders = await order.get_descendants()
        tap.eq(len(children_orders), 1, 'дочерний ордер 1')
        child = children_orders[0]

        tap.ok(await cargo.reload(), 'Перезабрали груз')
        tap.eq(cargo.rack_id, another_rack.rack_id, 'Груз теперь тут')
        tap.eq(
            cargo.vars.get('order_external_id', None),
            child.external_id,
            'Теперь дочерний документ'
        )
        tap.ok(await another_rack.reload(), 'Перезабрали стеллаж')
        tap.eq(another_rack.count, 1, 'Теперь содержит 1')
        reserved_racks = await dataset.Rack.list_by_order(order=order)
        tap.eq(
            len(reserved_racks),
            0,
            'нет резервов в стеллажах'
        )
