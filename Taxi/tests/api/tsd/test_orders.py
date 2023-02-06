from datetime import timedelta

import pytest

@pytest.mark.parametrize('main_role', ['executer', 'admin'])
@pytest.mark.parametrize('role', ['executer', 'barcode_executer'])
async def test_orders_admin_as_role_empty(tap, api, dataset, role, main_role):
    with tap.plan(6, 'нет заказов'):

        user = await dataset.user(role=main_role, force_role=role)
        tap.ok(user, 'Юзер создан')
        tap.eq(user.force_role, role, 'форсирована роль')
        t = await api(user=user)

        await t.post_ok('api_tsd_orders', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('orders', [])

async def test_orders_no_owner(tap, api, dataset):
    with tap.plan(7, 'запрошен заказ другого склада'):
        t = await api(role='barcode_executer')

        order = await dataset.order(status='request')
        tap.ok(order, 'заказ создан')
        tap.eq(order.status, 'request', 'в статусе request')
        tap.ok(order.store_id, 'склад в нём')

        await t.post_ok('api_tsd_orders', json={'order_ids': [order.order_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('orders', [])

async def test_orders_request(tap, api, dataset):
    with tap.plan(18, 'Есть заказ request'):
        user = await dataset.user(role='executer',
                                  force_role='barcode_executer')
        tap.ok(user, 'пользователь создан')
        t = await api()
        t.set_user(user)

        order = await dataset.order(store_id=user.store_id, status='request')
        tap.ok(order, 'заказ создан')
        tap.eq(order.status, 'request', 'в статусе request')
        tap.ok(order.store_id, 'склад в нём')

        await t.post_ok('api_tsd_orders', json={'order_ids': [order.order_id]})
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')

        t.json_is('orders.0.order_id', order.order_id)
        t.json_is('orders.0.external_id', order.external_id)
        t.json_is('orders.0.parent', order.parent)
        t.json_is('orders.0.status', 'request')
        t.json_like('orders.0.created', r'^\d+$')
        t.json_like('orders.0.version', r'^\d+$')
        t.json_like('orders.0.revision', r'^\d+$')
        t.json_is('orders.0.users', order.users)
        t.json_is('orders.0.type', order.type)
        t.json_is('orders.0.required', order.required)
        t.json_is('orders.0.problems', order.problems)



async def test_orders_processing(tap, api, dataset):
    with tap.plan(10, 'Выбираем processing по order_ids'):
        user = await dataset.user(role='executer')
        t = await api()
        t.set_user(user)

        request = await dataset.order(store_id=user.store_id, status='request')
        tap.ok(request, 'ордер в статусе request создан')

        order = await dataset.order(
            store_id=user.store_id,
            status='processing',
            users=[user.user_id]
        )
        tap.ok(order, 'заказ создан')
        tap.eq(order.status, 'processing', 'в статусе processing')
        tap.ok(order.store_id, 'склад в нём')

        await t.post_ok('api_tsd_orders', json={'order_ids': [order.order_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('orders.0.order_id', order.order_id)
        t.json_is('orders.0.status', 'processing')
        t.json_hasnt('orders.1', 'Больше ордеров нет')

async def test_orders_other_users(tap, api, dataset):
    with tap.plan(8, 'Есть заказ request'):
        user = await dataset.user(role='executer')
        t = await api()
        t.set_user(user)

        user2 = await dataset.user(role='executer', store_id=user.store_id)
        tap.ok(user2, 'второй пользователь создан')

        order = await dataset.order(
            store_id=user.store_id,
            status='processing',
            users=[user2.user_id]
        )
        tap.ok(order, 'заказ создан')
        tap.eq(order.status, 'processing', 'в статусе processing')
        tap.ok(order.store_id, 'склад в нём')

        await t.post_ok('api_tsd_orders', json={'order_ids': [order.order_id]})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('orders', [], 'пусто')


async def test_courier(tap, api, dataset, uuid):
    with tap.plan(12, 'сортировка при наличии ордеров с данными о курьерах'):
        user = await dataset.user(role='executer')

        order = await dataset.order(status='request', store_id=user.store_id)
        tap.eq(order.store_id, user.store_id, 'ордер 1 создан')
        tap.ok(not order.courier, 'курьера нет')

        order2 = await dataset.order(
            status='request',
            store_id=user.store_id,
            courier={
                'name': 'Вася',
                'arrival_time': order.created + timedelta(days=10),
                'external_id': uuid(),
            }
        )
        tap.eq(order2.store_id, user.store_id, 'ордер 2 создан')
        tap.ok(order2.courier, 'курьер во втором есть')
        tap.ok(order2.courier.arrival_time > order.created,
               'время курьера больше времени создания')

        t = await api(user=user)
        await t.post_ok('api_tsd_orders', json={})
        t.status_is(200, diag=True)

        t.json_has('orders.0')
        t.json_is('orders.0.order_id',
                  order2.order_id,
                  'первый в списке с курьером')
        t.json_has('orders.1')
        t.json_is('orders.1.order_id', order.order_id)
        t.json_hasnt('orders.2')


async def test_all_option(tap, api, dataset, uuid):
    with tap.plan(10, 'Запрос за всеми ордерами'):
        user = await dataset.user(role='executer')

        order = await dataset.order(status='complete', store_id=user.store_id)
        t = await api(user=user)
        await t.post_ok('api_tsd_orders',
                        json={
                            'all': True,
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'empty order_ids')

        await t.post_ok('api_tsd_orders',
                        json={
                            'all': True,
                            'order_ids': [
                                order.order_id,
                                uuid(),
                            ]
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('orders.0')
        t.json_is('orders.0.order_id', order.order_id)
        t.json_hasnt('orders.1')

# pylint: disable=invalid-name
async def test_all_courier_wo_arrival_time(tap, api, dataset, uuid):
    with tap.plan(13, 'Ордера с курьерами без времени прибытия'):
        user = await dataset.user(role='executer')

        order = await dataset.order(
            status='complete',
            store_id=user.store_id,
            courier={
                'external_id': uuid(),
                'name': 'Вася',
            }
        )
        tap.ok(order, 'ордер создан')
        tap.ok(order.courier, 'курьер есть')
        tap.ok(not order.courier.arrival_time, 'времени прибытия нет')
        t = await api(user=user)
        await t.post_ok('api_tsd_orders',
                        json={
                            'all': True,
                        })
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')
        t.json_is('message', 'empty order_ids')

        await t.post_ok('api_tsd_orders',
                        json={
                            'all': True,
                            'order_ids': [
                                order.order_id,
                                uuid(),
                            ]
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('orders.0')
        t.json_is('orders.0.order_id', order.order_id)
        t.json_hasnt('orders.1')


@pytest.mark.parametrize('maybe_rover', [True, False, None])
async def test_maybe_rover(tap, api, dataset, maybe_rover):
    with tap:
        user = await dataset.user(role='executer')

        attr = {}
        if maybe_rover is not None:
            attr['maybe_rover'] = maybe_rover

        order = await dataset.order(
            status='request',
            store_id=user.store_id,
            attr=attr
        )
        tap.eq(order.store_id, user.store_id, 'ордер создан')

        t = await api(user=user)
        await t.post_ok('api_tsd_orders', json={})
        t.status_is(200, diag=True)

        t.json_has('orders.0')
        if maybe_rover is not None:
            t.json_is('orders.0.attr.maybe_rover', maybe_rover)
        else:
            t.json_hasnt('orders.0.attr.maybe_rovers')
