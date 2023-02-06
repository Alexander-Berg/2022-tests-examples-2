import pytest

@pytest.mark.parametrize('order_status', ['request'])
async def test_ack(tap, api, dataset, order_status):
    with tap.plan(10, 'Нормальный ack'):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user, 'пользователь создан')
        tap.ok(user.store_id, 'склад есть')
        tap.eq(user.force_role, 'barcode_executer', 'форсированная роль')
        tap.eq(user.role, 'executer', 'роль')

        t = await api()
        t.set_user(user)


        order = await dataset.order(
            store_id=user.store_id,
            status=order_status,
        )

        tap.ok(order, 'заказ создан')
        tap.eq(order.status, order_status, f'статус {order_status}')

        await t.post_ok('api_tsd_order_ack', json={'order_id': order.order_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('message', 'ack was sent')



@pytest.mark.parametrize(
    'order_status',
    ['reserving', 'approving', 'processing'])
async def test_ack_wrong_status(tap, api, dataset, order_status):
    with tap.plan(10, 'Нормальный ack'):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user, 'пользователь создан')
        tap.ok(user.store_id, 'склад есть')
        tap.eq(user.force_role, 'barcode_executer', 'форсированная роль')
        tap.eq(user.role, 'executer', 'роль')

        t = await api()
        t.set_user(user)


        order = await dataset.order(
            store_id=user.store_id,
            status=order_status,
        )

        tap.ok(order, 'заказ создан')
        tap.eq(order.status, order_status, f'статус {order_status}')

        await t.post_ok('api_tsd_order_ack', json={'order_id': order.order_id})
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_GONE')
        t.json_is('message', 'Order has gone')


@pytest.mark.parametrize(
    'order_status',
    ['complete', 'failed', 'canceled'])
async def test_ack_access_denied(tap, api, dataset, order_status):
    with tap.plan(10, 'Нормальный ack'):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user, 'пользователь создан')
        tap.ok(user.store_id, 'склад есть')
        tap.eq(user.force_role, 'barcode_executer', 'форсированная роль')
        tap.eq(user.role, 'executer', 'роль')

        t = await api()
        t.set_user(user)

        order = await dataset.order(
            store_id=user.store_id,
            status=order_status,
        )

        tap.ok(order, 'заказ создан')
        tap.eq(order.status, order_status, f'статус {order_status}')

        await t.post_ok('api_tsd_order_ack', json={'order_id': order.order_id})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Access denied')


@pytest.mark.parametrize('order_status', ['request'])
async def test_ack_repeat(tap, api, dataset, order_status):
    with tap.plan(14, 'повторы ack'):
        user = await dataset.user(role='barcode_executer')
        tap.ok(user, 'пользователь создан')
        tap.ok(user.store_id, 'склад есть')
        tap.eq(user.force_role, 'barcode_executer', 'форсированная роль')
        tap.eq(user.role, 'executer', 'роль')

        t = await api()
        t.set_user(user)


        order = await dataset.order(
            store_id=user.store_id,
            status=order_status,
        )

        tap.ok(order, 'заказ создан')
        tap.eq(order.status, order_status, f'статус {order_status}')

        for i in range(1, 3):
            await t.post_ok('api_tsd_order_ack',
                            json={'order_id': order.order_id},
                            desc=f'Запрос {i}')
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('message', 'ack was sent')



@pytest.mark.parametrize('mode',
                         ['processing', 'inventory_begin', 'inventory_finish'])
async def test_store_mode_processing(tap, dataset, api, mode):
    with tap.plan(6, 'в processing нельзя брать инвентаризацию'):
        store = await dataset.store(estatus=mode)
        tap.eq((store.status, store.estatus), ('active', mode), 'склад')

        user = await dataset.user(store=store, role='barcode_executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(store=store,
                                    type='inventory',
                                    status='request')
        tap.eq(order.store_id, store.store_id, 'заказ создан')
        tap.eq(order.type, 'inventory', 'инвентаризация')


        t = await api(user=user)
        await t.post_ok('api_tsd_order_ack',
                        json={'order_id': order.order_id})
        t.status_is(423, diag=True)


@pytest.mark.parametrize('mode',
                         ['inventory', 'inventory_begin', 'inventory_finish'])
async def test_store_mode_inventory(tap, dataset, api, mode):
    with tap.plan(6, 'в processing нельзя брать инвентаризацию'):
        store = await dataset.store(estatus=mode)
        tap.eq((store.status, store.estatus), ('active', mode), 'склад')

        user = await dataset.user(store=store, role='barcode_executer')
        tap.eq(user.store_id, store.store_id, 'пользователь создан')

        order = await dataset.order(store=store,
                                    type='order',
                                    status='request')
        tap.eq(order.store_id, store.store_id, 'заказ создан')
        tap.eq(order.type, 'order', 'обычный заказ')


        t = await api(user=user)
        await t.post_ok('api_tsd_order_ack',
                        json={'order_id': order.order_id})
        t.status_is(423, diag=True)


async def test_study(tap, dataset, api):
    with tap.plan(23, 'взятие учебных заказов'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store,
                                  role='barcode_executer',
                                  study=True)
        tap.eq(
            (user.store_id, user.study),
            (store.store_id, True),
            'Ученик создан'
        )

        order1 = await dataset.order(store=store,
                                     type='order',
                                     status='request')
        tap.eq(order1.store_id, store.store_id, 'заказ создан')
        tap.eq(order1.type, 'order', 'обычный заказ')

        t = await api(user=user)
        await t.post_ok('api_tsd_order_ack',
                        json={'order_id': order1.order_id})
        t.status_is(403, diag=True)
        t.json_is('message', 'user.study can not ack the order')
        tap.ok(await order1.reload(), 'перегружен')
        tap.eq(order1.acks, [], 'не зафиксирован ack')


        order = await dataset.order(store=store,
                                    type='order',
                                    status='request',
                                    study=True)
        tap.eq(order.store_id, store.store_id, 'заказ создан')
        tap.eq(order.type, 'order', 'обычный заказ')
        tap.eq(order.study, True, 'учебный заказ')

        await t.post_ok('api_tsd_order_ack',
                        json={'order_id': order.order_id})
        t.status_is(200, diag=True)
        t.json_is('message', 'ack was sent')
        tap.ok(await order.reload(), 'перегружен')
        tap.eq(order.acks, [user.user_id], 'зафиксирован ack')


        user.study = False
        tap.ok(await user.save(), 'больше не ученик')
        await t.post_ok('api_tsd_order_ack',
                        json={'order_id': order1.order_id})
        t.status_is(200, diag=True)
        t.json_is('message', 'ack was sent')
        tap.ok(await order1.reload(), 'перегружен')
        tap.eq(order1.acks, [user.user_id], 'зафиксирован ack')
