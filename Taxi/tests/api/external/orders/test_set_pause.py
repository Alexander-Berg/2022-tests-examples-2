from stall.model.order_log import OrderLog


async def test_set_pause(tap, dataset, api, now):
    with tap.plan(14, 'ставим заказ на паузу'):
        t = await api(role='token:web.external.tokens.0')

        user = await dataset.user()
        order = await dataset.order(
            store_id=user.store_id,
            type='order',
            status='processing',
            required=[],
        )

        await t.post_ok(
            'api_external_orders_set_pause',
            json={
                'external_id': order.external_id,
                'store_id': user.store_id,
                'duration': 30,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('order_id', order.order_id)
        t.json_is('external_id', order.external_id)
        t.json_is('store_id', order.store_id)
        t.json_has('paused_until')

        await order.reload()
        tap.ok(
            29 <= (order.paused_until - now()).seconds <= 30,
            'выставили паузу',
        )
        tap.eq(order.vars('total_pause'), 30, 'записали продолжительность')

        await t.post_ok(
            'api_external_orders_set_pause',
            json={
                'external_id': order.external_id,
                'store_id': user.store_id,
                'duration': 0,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await order.reload()
        tap.ok(
            (now() - order.paused_until).seconds < 1,
            'сняли с паузы',
        )

        olog = await OrderLog.list(
            by='full',
            conditions=[
                ('order_id', order.order_id),
                ('source', 'set_pause'),
            ],
        )
        tap.eq(len(olog.list), 2, 'обе паузы в логе')


async def test_bad_status(tap, dataset,  api):
    with tap.plan(3, 'в статусе, когда пауза не имеет смысла'):
        t = await api(role='token:web.external.tokens.0')

        user = await dataset.user()
        order = await dataset.order(
            store_id=user.store_id,
            type='order',
            status='complete',
            required=[],
        )

        await t.post_ok(
            'api_external_orders_set_pause',
            json={
                'external_id': order.external_id,
                'store_id': user.store_id,
                'duration': 30,
            },
        )

        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')


async def test_not_paused(tap, dataset,  api):
    with tap.plan(3, 'снимаем с паузы заказ не на паузе'):
        t = await api(role='token:web.external.tokens.0')

        user = await dataset.user()
        order = await dataset.order(
            store_id=user.store_id,
            type='order',
            status='processing',
            required=[],
        )

        await t.post_ok(
            'api_external_orders_set_pause',
            json={
                'external_id': order.external_id,
                'store_id': user.store_id,
                'duration': 0,
            },
        )

        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')


async def test_not_found(tap, uuid, api):
    with tap.plan(3, 'заказ не найден'):
        t = await api(role='token:web.external.tokens.0')

        await t.post_ok(
            'api_external_orders_set_pause',
            json={
                'external_id': uuid(),
                'store_id': uuid(),
                'duration': 30,
            },
        )

        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')
