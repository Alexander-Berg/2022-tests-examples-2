import datetime
import itertools

import pytest

from stall.model.order import ORDER_STATUS


@pytest.mark.parametrize('role', ['admin', 'store_admin'])
async def test_simple(tap, dataset, api, role):
    with tap.plan(7):
        store = await dataset.store()
        admin = await dataset.user(role=role, store=store)
        shift = await dataset.courier_shift(store=store)

        product = await dataset.product()
        doc_dates = [
            datetime.date(2021, 10, 21),
            datetime.date(2021, 10, 7),
            datetime.date(2021, 9, 18),
        ]
        orders = [
            await dataset.order(
                store=store,
                status=status,
                doc_date=doc_date,
                required=[{'product_id': product.product_id, 'count': 0}],
                courier_shift=shift,
            )
            for status, doc_date in itertools.product(ORDER_STATUS, doc_dates)
        ]

        t = await api(user=admin)

        await t.post_ok('api_disp_orders_shift', json={
            'courier_shift_id': shift.courier_shift_id,
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('orders', 'Получили заказы')
        t.json_is('orders.0.required.0.product_id', product.product_id)
        t.json_is('orders.0.required.0.count', 0)

        received_orders = sorted(
            order['order_id'] for order in t.res['json']['orders']
        )
        expected_orders = sorted(order.order_id for order in orders)
        tap.eq_ok(received_orders, expected_orders, 'Заказы верны')


async def test_over_permits(tap, dataset, api):
    with tap.plan(4, 'Доступ только к своему заказу'):
        company1 = await dataset.company()
        company2 = await dataset.company()

        store1 = await dataset.store(company=company1)
        store2 = await dataset.store(company=company2)

        shift1 = await dataset.courier_shift(store=store1)
        shift2 = await dataset.courier_shift(store=store2)

        await dataset.order(store=store1, courier_shift=shift1)
        await dataset.order(store=store2, courier_shift=shift2)

        user = await dataset.user(role='store_admin', store=store2)

        t = await api(user=user)

        await t.post_ok(
            'api_disp_orders_shift',
            json={'courier_shift_id': shift1.courier_shift_id},
        )
        t.status_is(403, diag=True)

        await t.post_ok(
            'api_disp_orders_shift',
            json={'courier_shift_id': shift2.courier_shift_id},
        )
        t.status_is(200, diag=True)
