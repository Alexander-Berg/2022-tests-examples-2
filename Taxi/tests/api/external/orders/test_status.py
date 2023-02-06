import pytest

from stall.model.order import Order


async def test_status_not_found(tap, dataset, uuid, api):
    with tap.plan(5):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        await t.post_ok('api_external_orders_status', json={
            'store_id': store.store_id,
            'external_id': uuid(),
            'status': 'cancel'
        })
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')
        t.json_is('details.message', 'Order not found')


@pytest.mark.parametrize('status', ['cancel', 'confirm'])
async def test_status(tap, dataset, api, status):
    with tap.plan(8):
        t = await api(role='token:web.external.tokens.0')

        product = await dataset.product()
        order = await dataset.order(
            status='approving',
            required=[{'product_id': product.product_id, 'count': 2}]
        )
        tap.ok(order, 'заказ создан')
        tap.ok(order.approved is None, 'Заказ не одобрен')

        await t.post_ok('api_external_orders_status', json={
            'store_id': order.store_id,
            'external_id': order.external_id,
            'status': status
        })
        t.status_is(200, diag=True)
        t.json_is('order.order_id', order.order_id)
        t.json_is('order.store_id', order.store_id, 'лавка')
        t.json_is('order.external_id',
                  order.external_id,
                  'external_id в ответе')
        if status == 'cancel':
            tap.eq_ok(
                (await Order.load(order.order_id)).target,
                'canceled',
                'Обновилен target'
            )
        elif status == 'confirm':
            tap.ok(
                (await Order.load(order.order_id)).approved,
                'Одобрен'
            )


async def test_conflict(tap, dataset, api):
    with tap.plan(5):
        t = await api(role='token:web.external.tokens.0')

        product = await dataset.product()
        order = await dataset.order(
            status='canceled',
            required=[{'product_id': product.product_id, 'count': 2}]
        )
        tap.ok(order, 'заказ создан')
        tap.ok(order.approved is None, 'Заказ не одобрен')

        await t.post_ok('api_external_orders_status', json={
            'store_id': order.store_id,
            'external_id': order.external_id,
            'status': 'cancel'
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


async def test_cancel_already_canceled(tap, dataset, api):
    with tap.plan(5):
        t = await api(role='token:web.external.tokens.0')

        product = await dataset.product()
        order = await dataset.order(
            status='failed',
            target='canceled',
            required=[{'product_id': product.product_id, 'count': 2}]
        )
        tap.ok(order, 'заказ создан')
        tap.ok(order.approved is None, 'Заказ не одобрен')

        await t.post_ok('api_external_orders_status', json={
            'store_id': order.store_id,
            'external_id': order.external_id,
            'status': 'cancel'
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')


async def test_cancel_order_complete(tap, dataset, api):
    with tap.plan(13, 'отмена после complete'):
        t = await api(role='token:web.external.tokens.0')

        product = await dataset.product()
        order = await dataset.order(
            status='complete',
            target='complete',
            required=[{'product_id': product.product_id, 'count': 2}]
        )
        tap.ok(order, 'заказ создан')
        tap.ok(order.approved is None, 'Заказ не одобрен')
        tap.ne(order.target, 'canceled', 'target != canceled')

        for i in (1, 2):
            await t.post_ok('api_external_orders_status', json={
                'store_id': order.store_id,
                'external_id': order.external_id,
                'status': 'cancel',
                'desc': f'попытка отменить {i}',
            })
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            tap.ok(await order.reload(), 'перезаргружен')
            tap.eq(order.target, 'canceled', 'target поменялся')


@pytest.mark.parametrize(
    'status', ['request', 'processing', 'complete', 'canceled', 'failed'],
)
async def test_confirm_fail(tap, dataset, api, status):
    with tap.plan(
            7,
            'Подтверждение в не подходящем статусе отклоняется'
            ' без записи в лог'
    ):
        t = await api(role='token:web.external.tokens.0')

        product = await dataset.product()
        order = await dataset.order(
            status=status,
            required=[{'product_id': product.product_id, 'count': 2}],
        )
        tap.ok(order, 'заказ создан')
        tap.ok(not order.approved, 'Заказ не одобрен')

        logs = await dataset.OrderLog.list_by_order(order)
        tap.eq(
            len([x for x in logs if x.source == 'approve']), 0,
            'Подтверждения нет'
        )

        tap.note('Подтверждаем')
        await t.post_ok(
            'api_external_orders_status',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,
                'status': 'confirm',
            }
        )
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')

        logs = await dataset.OrderLog.list_by_order(order)
        tap.eq(
            len([x for x in logs if x.source == 'approve']), 0,
            'Повтора нет'
        )


@pytest.mark.parametrize(
    'status', ['reserving', 'approving'],
)
async def test_double_confirm(tap, dataset, api, status):
    with tap.plan(11, 'Спам аппрувов. Выполняется только первый раз.'):
        t = await api(role='token:web.external.tokens.0')

        product = await dataset.product()
        order = await dataset.order(
            status=status,
            required=[{'product_id': product.product_id, 'count': 2}],
        )
        tap.ok(order, 'заказ создан')
        tap.ok(not order.approved, 'Заказ не одобрен')

        logs = await dataset.OrderLog.list_by_order(order)
        tap.eq(
            len([x for x in logs if x.source == 'approve']), 0,
            'Подтверждения нет'
        )

        tap.note('Подтверждаем')
        await t.post_ok(
            'api_external_orders_status',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,
                'status': 'confirm',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        logs = await dataset.OrderLog.list_by_order(order)
        tap.eq(
            len([x for x in logs if x.source == 'approve']), 1,
            'Подтверждение в логе'
        )

        tap.note('Поврторно подтверждаем')
        await t.post_ok(
            'api_external_orders_status',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,
                'status': 'confirm',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        logs = await dataset.OrderLog.list_by_order(order)
        tap.eq(
            len([x for x in logs if x.source == 'approve']), 1,
            'Повтора нет'
        )


@pytest.mark.parametrize(
    'status', ['request', 'processing', 'complete', 'canceled', 'failed'],
)
async def test_double_confirm_fail(tap, dataset, api, now, status):
    with tap.plan(
            7,
            'Повторение аппрувов в процессе выполенния'
            'отдаст текущий результат'
    ):
        t = await api(role='token:web.external.tokens.0')

        product = await dataset.product()
        order = await dataset.order(
            status=status,
            approved=now(),
            required=[{'product_id': product.product_id, 'count': 2}],
        )
        tap.ok(order, 'заказ создан')
        tap.ok(order.approved, 'Заказ уже одобрен')

        logs = await dataset.OrderLog.list_by_order(order)
        tap.eq(
            len([x for x in logs if x.source == 'approve']), 0,
            'Подтверждения нет'
        )

        tap.note('Повторно подтверждаем')
        await t.post_ok(
            'api_external_orders_status',
            json={
                'store_id': order.store_id,
                'external_id': order.external_id,
                'status': 'confirm',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        logs = await dataset.OrderLog.list_by_order(order)
        tap.eq(
            len([x for x in logs if x.source == 'approve']), 0,
            'Повтора нет'
        )
