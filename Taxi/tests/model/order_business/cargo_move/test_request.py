async def test_request_noack(tap, dataset, wait_order_status):
    with tap.plan(6, 'Нет ack'):
        store = await dataset.store(type='dc')
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
            ]
        )
        tap.ok(
            await wait_order_status(order, ('request', 'waiting')),
            'Дотолкали ордер до request,waiting'
        )
        tap.ok(
            await order.business.order_changed() is None,
            'Не было движений'
        )
        tap.ok(await order.reload(), 'перегрузили')
        tap.eq(order.status, 'request', 'статус переключен')
        tap.eq(order.estatus, 'waiting', 'сабстатус переключен')


async def test_request_ack(tap, dataset, wait_order_status):
    with tap.plan(2, 'Есть ack'):
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
