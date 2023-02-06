async def test_incomplete(tap, api, dataset):
    with tap.plan(15):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order_approving = await dataset.order(
            store=store,
            status='approving',
            eda_status='CALL_CENTER_CONFIRMED'
        )

        tap.eq(order_approving.store_id, store.store_id, 'Ордер создан')

        order = await dataset.order(
            store=store,
            status='complete',
            eda_status='ARRIVED_TO_CUSTOMER'
        )
        tap.eq(order.store_id, store.store_id, 'Ордер создан')

        order_request = await dataset.order(
            store=store,
            status='request',
            eda_status='PICKUP'
        )
        tap.ok(order_request, 'Ордер создан')

        order_failed = await dataset.order(
            store=store,
            status='failed',
            eda_status='UNCONFIRMED',
        )
        tap.ok(order_failed, 'Создан failed ордер')

        order_canceled = await dataset.order(
            store=store,
            status='canceled',
            eda_status='UNKNOWN',
        )
        tap.ok(order_canceled, 'Создан canceled ордер')

        order_reserving_null = await dataset.order(
            store=store,
            status='reserving',
            eda_status=None,
        )
        tap.ok(order_reserving_null, 'Создан reserving ордер с null')

        order_complete = await dataset.order(
            store=store,
            status='complete',
            eda_status='DELIVERED'
        )
        tap.eq(order_complete.store_id, store.store_id, 'Ордер создан')

        order_null = await dataset.order(
            store=store,
            status='complete',
            eda_status=None
        )
        tap.eq(order_null.store_id, store.store_id, 'Ордер создан')

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_incomplete',
            json={
                'limit': 10,
            }
        )

        expected_orders = [
            order_approving,
            order_request,
            order,
            order_reserving_null
        ]
        t.status_is(200, diag=True)
        t.json_has('cursor')

        tap.eq(
            len(t.res['json']['orders']),
            len(expected_orders),
            'Количетсво ордеров правильное'
        )
        tap.eq(
            {order['order_id'] for order in t.res['json']['orders']},
            {order.order_id for order in expected_orders},
            'Правильные id ордеров'
        )


async def test_incomplete_cursor(tap, api, dataset):
    with tap.plan(16, 'Работа incomplete ручки с курсором'):
        store = await dataset.store()
        tap.ok(store, 'Склад создан')

        user = await dataset.user(store=store)
        tap.ok(user, 'Пользователь создан')

        order_one = await dataset.order(
            store=store,
            status='approving',
            eda_status='CALL_CENTER_CONFIRMED'
        )
        tap.ok(order_one, 'Первый ордер создан')

        order_two = await dataset.order(
            store=store,
            status='request',
            eda_status='UNKNOWN'
        )
        tap.ok(order_two, 'Второй ордер создан')

        order_three = await dataset.order(
            store=store,
            status='complete',
            eda_status='ARRIVED_TO_CUSTOMER'
        )
        tap.ok(order_two, 'Третий ордер создан')

        order_failed = await dataset.order(
            store=store,
            status='failed',
            eda_status='UNCONFIRMED',
        )
        tap.ok(order_failed, 'Создан failed ордер')

        recieved_ids = []

        t = await api(user=user)
        await t.post_ok(
            'api_disp_orders_incomplete',
            json={
                'limit': 2,
            }
        )
        t.status_is(200, diag=True)
        t.json_isnt('cursor', None)
        cursor_str = t.res['json']['cursor']
        t.json_has('orders.0')
        recieved_ids.extend(
            order['order_id']
            for order in t.res['json']['orders']
        )

        await t.post_ok(
            'api_disp_orders_incomplete',
            json={
                'cursor': cursor_str,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('cursor', None)
        t.json_has('orders.0')
        recieved_ids.extend(
            order['order_id']
            for order in t.res['json']['orders']
        )
        expected_orders = [order_one, order_two, order_three]

        tap.eq(
            len(recieved_ids),
            len(expected_orders),
            'Правильное совокупное количество оредров'
        )

        tap.eq(
            set(recieved_ids),
            {order.order_id for order in expected_orders},
            'Получены правильные ордера'
        )
