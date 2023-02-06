# pylint: disable=wrong-import-order

import itertools

import pytest

import datetime as dt
from stall.model.order import ORDER_STATUS, ORDER_TYPE


@pytest.mark.parametrize('role', ['admin', 'store_admin'])
async def test_orders_no_store_id(tap, dataset, api, role):
    with tap.plan(9, f'у {role} без установленного склада нет доступа'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        admin = await dataset.user(role=role, store_id=None)
        tap.ok(admin, 'админ создан')
        tap.eq(admin.role, role, f'роль {role}')
        tap.eq(admin.store_id, None, 'вне склада')

        t = await api(user=admin)

        await t.post_ok('api_disp_orders_history', json={})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Access denied', 'сообщение об ошибке')
        t.json_like('details.message', r'over: my_store$', 'сообщение')


@pytest.mark.parametrize('role', ['admin', 'store_admin'])
async def test_orders_empty(tap, dataset, api, role):
    with tap.plan(8, f'нет заказов диспетчерской для роли {role}'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        admin = await dataset.user(role=role, store=store)
        tap.ok(admin, 'админ создан')
        tap.eq(admin.role, role, f'роль {role}')
        tap.eq(admin.store_id, store.store_id, 'на складе')

        t = await api(user=admin)

        await t.post_ok('api_disp_orders_history', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('orders', [], 'список заказов пуст')


@pytest.mark.parametrize('role', ['admin', 'store_admin'])
async def test_orders_nonempty(tap, dataset, api, role):
    with tap.plan(34, f'список заказов диспетчерской для роли {role}'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        orders = [
            await dataset.order(store=store, status=status)
            for status in ORDER_STATUS
        ]
        tap.ok(orders, 'Заказы созданы')
        orders.sort(key=lambda x: x.order_id)

        admin = await dataset.user(role=role, store=store)
        tap.ok(admin, 'админ создан')
        tap.eq(admin.role, role, f'роль {role}')
        tap.eq(admin.store_id, store.store_id, 'на складе')

        t = await api(user=admin)

        await t.post_ok('api_disp_orders_history', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('orders', 'Orders received')
        received_orders = sorted(t.res['json']['orders'],
                                 key=lambda x: x['order_id'])
        tap.eq_ok(len(orders), len(received_orders), 'Quantity of orders')
        for order, received in zip(orders, received_orders):
            tap.eq_ok(order.order_id, received['order_id'], 'ID')
            tap.eq_ok(order.status, received['status'], 'status')
            tap.eq_ok(order.store_id, received['store_id'], 'store_id')


@pytest.mark.parametrize('role', ['admin', 'store_admin'])
async def test_orders_history(tap, dataset, api, role, uuid):
    with tap.plan(1 + len(ORDER_STATUS) * 5 + len(ORDER_TYPE) * 5):
        store = await dataset.store()
        admin = await dataset.user(role=role, store=store)

        doc_dates = [dt.date(2020, 4, 1),
                     dt.date(2020, 3, 5),
                     dt.date(2020, 2, 11)]
        orders = [
            await dataset.order(store=store, status=status,
                                type=order_type,
                                attr={'doc_date': doc_date.strftime('%F'),
                                      'doc_number': uuid()})
            for status, order_type, doc_date in itertools.product(ORDER_STATUS,
                                                                  ORDER_TYPE,
                                                                  doc_dates)
        ]
        tap.ok(orders, 'Заказы созданы')

        t = await api(user=admin)

        for status in ORDER_STATUS:
            await t.post_ok('api_disp_orders_history', json={'status': status})
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('orders', 'Orders received')
            received_orders = sorted(
                order['order_id'] for order in t.res['json']['orders'])
            expected_orders = sorted(
                order.order_id for order in orders if order.status == status)
            tap.eq_ok(received_orders, expected_orders, 'Correct orders')

        for order_type in ORDER_TYPE:
            await t.post_ok('api_disp_orders_history',
                            json={'type': order_type})
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('orders', 'Orders received')
            received_orders = sorted(
                order['order_id'] for order in t.res['json']['orders'])
            expected_orders = sorted(
                order.order_id for order in orders if order.type == order_type)
            tap.eq_ok(received_orders, expected_orders, 'Correct orders')


@pytest.mark.parametrize('role', ['admin', 'store_admin'])
async def test_orders_history_doc_date(
    tap, dataset, api, uuid, role, time2time,
):
    with tap.plan(16):
        store = await dataset.store()
        admin = await dataset.user(role=role, store=store)

        doc_dates = [dt.date(2020, 4, 1),
                     dt.date(2020, 3, 5),
                     dt.date(2020, 2, 11)]
        orders = [
            await dataset.order(store=store, status=status,
                                type=order_type,
                                attr={'doc_date': doc_date.strftime('%F'),
                                      'doc_number': uuid()})
            for status, order_type, doc_date in itertools.product(ORDER_STATUS,
                                                                  ORDER_TYPE,
                                                                  doc_dates)
        ]
        tap.ok(orders, 'Заказы созданы')

        t = await api(user=admin)

        await t.post_ok('api_disp_orders_history',
                        json={'type': 'order',
                              'doc_date': {'from': '2020-03-05'}})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('orders', 'Orders received')
        received_orders = sorted(
            order['order_id'] for order in t.res['json']['orders'])
        expected_orders = sorted(
            order.order_id
            for order in orders
            if time2time(order.attr['doc_date']).date() >= dt.date(
                2020, 3, 5) and order.type == 'order'
        )
        tap.eq_ok(received_orders, expected_orders, 'Correct orders')

        await t.post_ok('api_disp_orders_history',
                        json={'status': 'request',
                              'doc_date': {'to': '2020-03-05'}})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('orders', 'Orders received')
        received_orders = sorted(
            order['order_id'] for order in t.res['json']['orders'])
        expected_orders = sorted(
            order.order_id
            for order in orders
            if time2time(order.attr['doc_date']).date() <= dt.date(
                2020, 3, 5) and order.status == 'request'
        )
        tap.eq_ok(received_orders, expected_orders, 'Correct orders')

        await t.post_ok('api_disp_orders_history',
                        json={'type': 'acceptance',
                              'doc_date': {'from': '2020-02-12',
                                           'to': '2020-04-01'}})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('orders', 'Orders received')
        received_orders = sorted(
            order['order_id'] for order in t.res['json']['orders'])
        expected_orders = sorted(
            order.order_id for order in orders if
            dt.date(2020, 2, 12) <= time2time(order.attr['doc_date']).date()
            <= dt.date(2020, 4, 1)
            and order.type == 'acceptance'
        )
        tap.eq_ok(received_orders, expected_orders, 'Correct orders')


async def test_orders_history_doc_number(tap, dataset, api, uuid):
    with tap.plan(14, 'Тесты поиска по номеру ордера'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')
        user = await dataset.user(store=store)
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(attr={'doc_number': uuid()}, store=store)
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        t = await api(user=user)

        await t.post_ok('api_disp_orders_history',
                        json={'type': 'order',
                              'doc_number': uuid()})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('orders', 'Список получен')
        t.json_hasnt('orders.0', 'Он пуст')

        await t.post_ok('api_disp_orders_history',
                        json={'type': 'order',
                              'doc_number': order.attr['doc_number']})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('orders', 'Список получен')
        t.json_hasnt('orders.1', 'Он не пуст')
        t.json_is('orders.0.order_id', order.order_id, 'содержит ордер')
