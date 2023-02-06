from stall.model.order import ORDER_STATUS


async def test_one(tap, dataset, api):
    with tap.plan(6, 'Загрузка одного ордера'):
        store = await dataset.store()
        user = await dataset.user(role='executer', store=store)
        order = await dataset.order(store=store)

        tap.note('По своему стору можно получать ордера')
        with user.role as role:
            role.add_permit('orders_load', True)
            t = await api(user=user)
            await t.post_ok(
                'api_admin_orders_load',
                json={
                    'order_id': [order.order_id]
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('orders', 'Order received')
            t.json_is('orders.0.order_id', order.order_id, 'Order received')
            t.json_hasnt('orders.1.order_id', 'Всё загрузили')


async def test_fields(tap, dataset, api):
    with tap.plan(6, 'Загружаем ограниченный набор полей'):
        order = await dataset.order()
        t = await api(role='admin')
        await t.post_ok(
            'api_admin_orders_load',
            json={
                'order_id': [order.order_id]
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('orders', 'Order received')
        t.json_has('orders.0', 'Order received')

        received_fields = set(t.res['json']['orders'][0].keys())
        expected_fields = set([
            'order_id',
            'company_id',
            'store_id',
            'external_id',
            'status',
            'type',
            'created',
            'updated',
            'attr',
        ])
        tap.eq(
            received_fields,
            expected_fields,
            f'Лишние поля: {received_fields - expected_fields} '
            f'Недостающие поля: {expected_fields - received_fields}'
        )


async def test_orders_list(tap, dataset, api):
    with tap.plan(5, 'Проверим загрузку списка ордеров'):
        store = await dataset.store()
        user = await dataset.user(role='executer', store=store)
        orders = [
            await dataset.order(store=store, status=status)
            for status in ORDER_STATUS
        ]

        with user.role as role:
            role.add_permit('orders_load', True)

            expected_orders = sorted([orders[0].order_id, orders[1].order_id])

            t = await api(user=user)
            await t.post_ok(
                'api_admin_orders_load',
                json={
                    'order_id': expected_orders
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('orders', 'Orders received')

            received_orders = sorted(
                order['order_id'] for order in t.res['json']['orders']
            )

            tap.eq_ok(received_orders, expected_orders, 'Correct orders')


async def test_permits_other_store(tap, dataset, api):
    with tap.plan(9, 'По другому стору можно загрузить, если out_of_store'):
        cluster = await dataset.cluster()
        company = await dataset.company()
        my_store = await dataset.store(company=company, cluster=cluster)
        other_store = await dataset.store(company=company, cluster=cluster)
        other_store_order = await dataset.order(store=other_store)
        user = await dataset.user(role='executer', store=my_store)

        t = await api(user=user)
        with user.role as role:
            role.add_permit('orders_load', True)
            await t.post_ok(
                'api_admin_orders_load',
                json={
                    'order_id': [other_store_order.order_id]
                }
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

            tap.note('Добавим пермит out_of_store')
            role.add_permit('out_of_store', True)
            await t.post_ok(
                'api_admin_orders_load',
                json={
                    'order_id': [other_store_order.order_id]
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('orders', 'Order received')
            t.json_is(
                'orders.0.order_id',
                other_store_order.order_id,
                'Order received'
            )
            t.json_hasnt('orders.1.order_id', 'Всё загрузили')


async def test_permits_stores_allow(tap, dataset, api):
    # pylint: disable=too-many-locals
    with tap.plan(
            2,
            'Права по out_of_store, можно ограничить через stores_allow'
    ):
        cluster = await dataset.cluster()
        company = await dataset.company()
        my_store = await dataset.store(company=company, cluster=cluster)
        allow_store = await dataset.store(company=company, cluster=cluster)
        other_store = await dataset.store(company=company, cluster=cluster)
        other_store_order = await dataset.order(store=other_store)
        allow_store_order = await dataset.order(store=allow_store)
        user = await dataset.user(role='executer', store=my_store)

        t = await api(user=user)
        with user.role as role:
            role.add_permit('orders_load', True)
            role.add_permit('out_of_store', True)

            all_orders = sorted([
                other_store_order.order_id, allow_store_order.order_id,
            ])
            with tap.subtest(5, 'Без stores_allow доступ везде') as taps:
                t.tap = taps
                await t.post_ok(
                    'api_admin_orders_load',
                    json={
                        'order_id': all_orders
                    }
                )
                t.status_is(200, diag=True)
                t.json_is('code', 'OK')
                t.json_has('orders', 'Order received')

                received_orders = sorted(
                    order['order_id'] for order in t.res['json']['orders']
                )
                taps.eq_ok(received_orders, all_orders, 'Correct orders')

            tap.note('Ограничим доступные сторы')
            user.stores_allow = [my_store.store_id, allow_store.store_id]
            await user.save()

            with tap.subtest(9, 'stores_allow ограничивает доступ') as taps:
                t.tap = taps
                await t.post_ok(
                    'api_admin_orders_load',
                    json={
                        'order_id': all_orders
                    }
                )
                t.status_is(403, diag=True)
                t.json_is('code', 'ER_ACCESS')

                taps.note('Запросим только доки по разрешенным сторам')
                await t.post_ok(
                    'api_admin_orders_load',
                    json={
                        'order_id': [allow_store_order.order_id]
                    }
                )
                t.status_is(200, diag=True)
                t.json_is('code', 'OK')
                t.json_has('orders', 'Order received')
                t.json_is(
                    'orders.0.order_id',
                    allow_store_order.order_id,
                    'Order received'
                )
                t.json_hasnt('orders.1.order_id', 'Всё загрузили')


async def test_permits_other_company(tap, dataset, api):
    with tap.plan(
            9,
            'По стору в другой компании можно грузить, если out_of_company'
    ):
        company = await dataset.company()
        other_company = await dataset.company()
        my_store = await dataset.store(company=company)
        other_company_store = await dataset.store(company=other_company)

        other_company_order = await dataset.order(store=other_company_store)

        user = await dataset.user(role='executer', store=my_store)
        t = await api(user=user)
        with user.role as role:
            role.add_permit('orders_load', True)
            role.add_permit('out_of_store', True)
            await t.post_ok(
                'api_admin_orders_load',
                json={
                    'order_id': [other_company_order.order_id]
                }
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

            tap.note('Добавим пермит out_of_company')
            role.add_permit('out_of_company', True)
            await t.post_ok(
                'api_admin_orders_load',
                json={
                    'order_id': [other_company_order.order_id]
                }
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('orders', 'Order received')
            t.json_is(
                'orders.0.order_id',
                other_company_order.order_id,
                'Order received'
            )
            t.json_hasnt('orders.1.order_id', 'Всё загрузили')
