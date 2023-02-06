async def test_children(tap, dataset, api):
    with tap.plan(10, 'получение дочерних заказов'):
        user = await dataset.user(role='admin')
        tap.ok(user.store_id, 'админ сгенерирован')
        t = await api(user=user)

        order = await dataset.order(store_id=user.store_id)
        tap.ok(order, 'заказ сгенерирован')

        order_child_1 = await dataset.order(store_id=user.store_id,
                                            parent=[order.order_id])
        order_child_2 = await dataset.order(store_id=user.store_id,
                                            parent=[order.order_id])

        tap.ok(order, 'дочерние заказы сгенерированы')

        await t.post_ok('api_tsd_order_children',
                        json={
                            'order_id': order.order_id,
                            'cursor': None,
                            'limit': 10,
                        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('order_ids')
        tap.eq(len(t.res['json']['order_ids']), 2, 'Длина корректна')
        tap.ok(order_child_1.order_id in t.res['json']['order_ids'],
               'Первый чайлд получен')
        tap.ok(order_child_2.order_id in t.res['json']['order_ids'],
               'Второй чайлд получен')


async def test_children_zero(tap, dataset, api):
    with tap.plan(7, 'получение дочерних заказов'
                     ' когда 0 дочерних'):
        user = await dataset.user(role='admin')
        tap.ok(user.store_id, 'админ сгенерирован')
        t = await api(user=user)

        order = await dataset.order(store_id=user.store_id)
        tap.ok(order, 'заказ сгенерирован')

        await t.post_ok('api_tsd_order_children',
                        json={
                            'order_id': order.order_id,
                            'cursor': None,
                            'limit': 10,
                        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('order_ids')
        tap.eq(len(t.res['json']['order_ids']), 0, 'Длина корректна')


async def test_children_no_order(tap, dataset, api, uuid):
    with tap.plan(3, 'получение дочерних заказов'
                     ' по ошибочному айишнику'):
        user = await dataset.user(role='admin')
        tap.ok(user.store_id, 'админ сгенерирован')
        t = await api(user=user)

        await t.post_ok('api_tsd_order_children',
                        json={
                            'order_id': uuid(),
                            'cursor': None,
                            'limit': 10,
                        })

        t.status_is(403, diag=True)


async def test_children_wrong_role(tap, dataset, api):
    with tap.plan(5, 'получение дочерних заказов'
                     ' для неподходящей роли'):
        user = await dataset.user(role='courier')
        tap.ok(user.store_id, 'админ сгенерирован')
        t = await api(user=user)

        order = await dataset.order(store_id=user.store_id)
        tap.ok(order, 'заказ сгенерирован')

        tap.ok(order, 'дочерние заказы сгенерирован')

        await t.post_ok('api_tsd_order_children',
                        json={
                            'order_id': order.order_id,
                            'cursor': None,
                            'limit': 10,
                        })

        t.status_is(403, diag=True)
