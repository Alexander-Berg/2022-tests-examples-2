from stall.model.order_problem import OrderProblem


async def test_load_order(tap, api, dataset):
    with tap.plan(4, 'Loaded orders'):
        user = await dataset.user(role='admin')
        orders = [
            (
                await dataset.order(
                    store_id=user.store_id
                )
            )
            for _ in range(0, 5)
        ]

        orders_ids = [order.order_id for order in orders]
        t = await api(user=user)

        await t.post_ok(
            'api_tsd_order_load_order',
            json={
                'order_ids': orders_ids
            }
        )
        t.status_is(200, diag=True)
        t.json_has('orders', 'orders')
        orders = t.res['json']['orders']
        getted_ids = set(order['order_id'] for order in orders)
        tap.ok(set(orders_ids).issubset(getted_ids), 'founded')


async def test_load_error(tap, api, dataset):
    with tap.plan(4, 'No access'):
        user = await dataset.user(role='admin')

        order = await dataset.order()
        tap.ne(order.store_id, user.store_id, 'разные лавки')

        t = await api(user=user)

        await t.post_ok(
            'api_tsd_order_load_order',
            json={
                'order_ids': [order.order_id]
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_load_problems(tap, api, dataset):
    with tap.plan(5, 'Load order with problems'):
        user = await dataset.user(role='admin')
        product = await dataset.product()
        order = await dataset.order(
            store_id=user.store_id,
            problems=[
                OrderProblem({
                    'type': 'product_not_found',
                    'product_id': product.product_id,
                }),
            ]
        )
        t = await api(user=user)

        await t.post_ok(
            'api_tsd_order_load_order',
            json={'order_ids': [order.order_id]},
        )
        t.status_is(200, diag=True)
        t.json_has('orders', 'orders')
        t.json_is('orders.0.problems.0.product_id', product.product_id)
        t.json_is('orders.0.problems.0.type', 'product_not_found')
