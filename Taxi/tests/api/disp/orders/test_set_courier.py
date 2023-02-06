# pylint: disable=too-many-locals


async def test_assign(tap, dataset, api, now):
    with tap.plan(18, 'Назначение курьера на заказ'):
        store = await dataset.store()

        user    = await dataset.user(store=store)
        courier = await dataset.user(store=store, role='courier')
        other   = await dataset.user(store=store, role='courier')

        order   = await dataset.order(
            store=store,
            type='order',
            dispatch_type='grocery',
        )
        old_version = order.version

        order1   = await dataset.order(
            store=store,
            type='order',
            dispatch_type='grocery',
        )
        order2   = await dataset.order(
            store=store,
            type='order',
            dispatch_type='grocery',
            courier_id=other.user_id,
        )
        order3   = await dataset.order(
            store=store,
            type='order',
            dispatch_type='grocery',
            courier_id=courier.user_id,
            courier_pri=0,
            delivery_promise=now(),
            en_route_timer=11,
            wait_client_timer=22,
        )

        order4   = await dataset.order(
            store=store,
            type='order',
            dispatch_type='grocery',
            courier_id=courier.user_id,
            status='complete',
        )
        order5   = await dataset.order(
            store=store,
            type='order',
            dispatch_type='external',
            courier_id=courier.user_id,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_set_courier',
            json={
                'mode': 'assign',
                'order_id': order.order_id,
                'courier_id': courier.user_id,
                'delivery_promise': now(),
                'en_route_timer': 10,
                'wait_client_timer': 20,

            })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await order.reload() as order:
            tap.eq(order.courier_id, courier.user_id, 'Курьер назначен')
            tap.eq(order.courier_pri, 0, 'courier_pri')
            tap.ok(order.delivery_promise, 'delivery_promise')
            tap.eq(order.en_route_timer, 10, 'en_route_timer')
            tap.eq(order.wait_client_timer, 20, 'wait_client_timer')
            tap.eq(order.version, old_version + 1, 'Версия увеличилась')

        with await order1.reload() as order:
            tap.eq(order.courier_id, None, 'Заказ не менялся')

        with await order2.reload() as order:
            tap.eq(order.courier_id, other.user_id, 'Заказ не менялся')

        with await order3.reload() as order:
            tap.eq(order.courier_id, None, 'курьер сброшен')
            tap.eq(order.courier_pri, None, 'courier_pri')
            tap.eq(order.delivery_promise, None, 'delivery_promise')
            tap.eq(order.en_route_timer, None, 'en_route_timer')
            tap.eq(order.wait_client_timer, None, 'wait_client_timer')

        with await order4.reload() as order:
            tap.eq(order.courier_id, courier.user_id, 'Заказ уже закрыт')

        with await order5.reload() as order:
            tap.eq(order.courier_id, courier.user_id, 'Заказ не диспатчится')


async def test_append(tap, dataset, api, now):
    with tap.plan(14, 'Добавление заказа курьеру'):
        store = await dataset.store()

        user    = await dataset.user(store=store)
        courier = await dataset.user(store=store, role='courier')

        order   = await dataset.order(
            store=store,
            type='order',
            dispatch_type='grocery',
        )
        old_version = order.version

        order1   = await dataset.order(
            store=store,
            type='order',
            dispatch_type='grocery',
            courier_id=courier.user_id,
            courier_pri=0,
            delivery_promise=now(),
            en_route_timer=11,
            wait_client_timer=22,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_set_courier',
            json={
                'mode': 'append',
                'order_id': order.order_id,
                'courier_id': courier.user_id,
                'delivery_promise': now(),
                'en_route_timer': 10,
                'wait_client_timer': 20,

            })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await order.reload() as order:
            tap.eq(order.courier_id, courier.user_id, 'Курьер назначен')
            tap.eq(order.courier_pri, 1, 'courier_pri')
            tap.ok(order.delivery_promise, 'delivery_promise')
            tap.eq(order.en_route_timer, 10, 'en_route_timer')
            tap.eq(order.wait_client_timer, 20, 'wait_client_timer')
            tap.eq(order.version, old_version + 1, 'Версия увеличилась')

        with await order1.reload() as order:
            tap.eq(order.courier_id, courier.user_id, 'Заказ не менялся')
            tap.eq(order.courier_pri, 0, 'courier_pri')
            tap.ok(order.delivery_promise, 'delivery_promise')
            tap.eq(order.en_route_timer, 11, 'en_route_timer')
            tap.eq(order.wait_client_timer, 22, 'wait_client_timer')


async def test_append_first(tap, dataset, api, now):
    with tap.plan(8, 'Добавление заказа курьеру без заказов'):
        store = await dataset.store()

        user    = await dataset.user(store=store)
        courier = await dataset.user(store=store, role='courier')

        order   = await dataset.order(
            store=store,
            type='order',
            dispatch_type='grocery',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_set_courier',
            json={
                'mode': 'append',
                'order_id': order.order_id,
                'courier_id': courier.user_id,
                'delivery_promise': now(),
                'en_route_timer': 10,
                'wait_client_timer': 20,

            })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await order.reload() as order:
            tap.eq(order.courier_id, courier.user_id, 'Курьер назначен')
            tap.eq(order.courier_pri, 0, 'courier_pri')
            tap.ok(order.delivery_promise, 'delivery_promise')
            tap.eq(order.en_route_timer, 10, 'en_route_timer')
            tap.eq(order.wait_client_timer, 20, 'wait_client_timer')


async def test_remove(tap, dataset, api, now):
    with tap.plan(12, 'Снятие курьера с заказа'):
        store = await dataset.store()

        user    = await dataset.user(store=store)
        courier = await dataset.user(store=store, role='courier')

        order   = await dataset.order(
            store=store,
            type='order',
            dispatch_type='grocery',
            courier_id=courier.user_id,
            courier_pri=0,
            delivery_promise=now(),
            en_route_timer=11,
            wait_client_timer=22,
        )
        old_version = order.version

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_set_courier',
            json={
                'mode': 'remove',
                'order_id': order.order_id,
                'courier_id': courier.user_id,
            })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        with await order.reload() as order:
            tap.eq(order.courier_id, None, 'Курьер снят')
            tap.eq(order.courier_pri, None, 'courier_pri')
            tap.eq(order.delivery_promise, None, 'delivery_promise')
            tap.eq(order.en_route_timer, None, 'en_route_timer')
            tap.eq(order.wait_client_timer, None, 'wait_client_timer')
            tap.eq(order.version, old_version + 1, 'Версия увеличилась')

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_set_courier',
            json={
                'mode': 'remove',
                'order_id': order.order_id,
                'courier_id': courier.user_id,
            })
        t.status_is(410, diag=True)
        t.json_is('message', 'Already gone')
