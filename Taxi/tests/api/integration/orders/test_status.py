import pytest

from stall.model.order import Order


async def test_status_not_found(tap, dataset, uuid, api):
    with tap.plan(5):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        await t.post_ok('api_integration_orders_status', json={
            'store_id': store.store_id,
            'external_id': uuid(),
            'status': 'cancel'
        })
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')
        t.json_is('details.message', 'Order not found')


@pytest.mark.parametrize('status', ['cancel', 'approve'])
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

        await t.post_ok('api_integration_orders_status', json={
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
        elif status == 'approve':
            tap.ok(
                (await Order.load(order.order_id)).approved,
                'Одобрен'
            )


async def test_status_company(tap, dataset, api):
    with tap.plan(8, 'Установка статуса по ключу компании'):
        company = await dataset.company()
        store   = await dataset.store(company=company)

        t = await api(token=company.token)

        order = await dataset.order(store=store, status='approving')

        await t.post_ok('api_integration_orders_status', json={
            'store_id': order.store_id,
            'external_id': order.external_id,
            'status': 'approve',
        })
        t.status_is(200, diag=True)
        t.json_is('order.order_id', order.order_id)
        t.json_is('order.company_id', order.company_id)
        t.json_is('order.store_id', order.store_id)
        t.json_is('order.external_id', order.external_id)
        t.json_is('order.status', 'approving')
        tap.ok(
            (await Order.load(order.order_id)).approved,
            'Одобрен'
        )


async def test_status_company_not_owner(tap, dataset, api):
    with tap.plan(3, 'Установка статуса по ключу компании в чужом складе'):
        company1 = await dataset.company()
        company2 = await dataset.company()
        store   = await dataset.store(company=company1)

        t = await api(token=company2.token)

        order = await dataset.order(store=store, status='approving')

        await t.post_ok('api_integration_orders_status', json={
            'store_id': order.store_id,
            'external_id': order.external_id,
            'status': 'approve',
        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_conflict(tap, dataset, api):
    with tap.plan(4):
        t = await api(role='token:web.external.tokens.0')

        product = await dataset.product()
        order = await dataset.order(
            status='canceled',
            required=[{'product_id': product.product_id, 'count': 2}]
        )
        tap.ok(order, 'заказ создан')
        tap.ok(order.approved is None, 'Заказ не одобрен')

        await t.post_ok('api_integration_orders_status', json={
            'store_id': order.store_id,
            'external_id': order.external_id,
            'status': 'cancel'
        })
        t.status_is(200, diag=True)
