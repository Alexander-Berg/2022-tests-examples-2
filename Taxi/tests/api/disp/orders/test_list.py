import datetime
import itertools

import pytest

from stall.model.order import ORDER_STATUS


@pytest.mark.parametrize('role', ['admin', 'store_admin'])
async def test_orders_list(tap, dataset, api, role):
    with tap.plan(7):
        store = await dataset.store()
        admin = await dataset.user(role=role, store=store)
        product = await dataset.product()

        doc_dates = [datetime.date(2020, 4, 1),
                     datetime.date(2020, 3, 5),
                     datetime.date(2020, 2, 11)]
        orders = [
            await dataset.order(
                store=store,
                status=status,
                doc_date=doc_date,
                required=[{'product_id': product.product_id, 'count': 0}],
            )
            for status, doc_date in itertools.product(ORDER_STATUS, doc_dates)
        ]
        in_work = (
            'reserving',
            'approving',
            'request',
            'processing'
        )
        orders_in_work = [order for order in orders if order.status in in_work]

        t = await api(user=admin)

        await t.post_ok('api_disp_orders_list', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('orders', 'Orders received')
        t.json_is('orders.0.required.0.product_id', product.product_id)
        t.json_is('orders.0.required.0.count', 0)
        received_orders = sorted(
            order['order_id'] for order in t.res['json']['orders'])
        expected_orders = sorted(order.order_id for order in orders_in_work)
        tap.eq_ok(received_orders, expected_orders, 'Correct orders')


async def test_over_permits(tap, dataset, api):
    with tap.plan(4, 'Доступ только к своему заказу'):
        company1 = await dataset.company()
        company2 = await dataset.company()

        store1 = await dataset.store(company=company1)
        store2 = await dataset.store(company=company2)

        order1 = await dataset.order(store=store1)
        order2 = await dataset.order(store=store2)

        user = await dataset.user(role='admin', store=store2)

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_load',
            json={'order_id': order1.order_id},
        )
        t.status_is(403, diag=True)

        await t.post_ok(
            'api_disp_orders_load',
            json={'order_id': order2.order_id},
        )
        t.status_is(200, diag=True)
