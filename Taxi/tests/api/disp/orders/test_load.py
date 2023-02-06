import pytest

from stall.model.order import ORDER_STATUS


@pytest.mark.parametrize('role', ['admin', 'store_admin'])
async def test_orders_list(tap, dataset, api, role):
    with tap.plan(10):
        store = await dataset.store()
        user = await dataset.user(role=role, store=store)

        orders = [
            await dataset.order(store=store, status=status)
            for status in ORDER_STATUS
        ]

        t = await api(user=user)

        await t.post_ok('api_disp_orders_load', json={
            'order_id': [orders[0].order_id, orders[1].order_id]
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order', 'Orders received')
        received_orders = sorted(
            order['order_id'] for order in t.res['json']['order'])
        expected_orders = sorted([orders[0].order_id, orders[1].order_id])
        tap.eq_ok(received_orders, expected_orders, 'Correct orders')

        await t.post_ok('api_disp_orders_load', json={
            'order_id': orders[0].order_id
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order', 'Order received')
        t.json_is('order.order_id', orders[0].order_id, 'Order received')


async def test_orders_load_weight(dataset, tap, api, uuid):
    with tap.plan(6):
        store = await dataset.store()
        user = await dataset.user(store=store)

        order = await dataset.order(
            store=store,
            required=[{
                'product_id': uuid(),
                'result_weight': 0,
                'weight': 100,
            }]
        )

        t = await api(user=user)

        await t.post_ok('api_disp_orders_load', json={
            'order_id': order.order_id
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('order', 'Ордер найден')
        t.json_is('order.order_id', order.order_id)
        t.json_is('order.required.0.product_id', order.required[0].product_id)
