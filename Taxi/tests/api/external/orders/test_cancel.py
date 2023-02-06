import pytest


async def test_cancel_notfound(tap, dataset, uuid, api):
    with tap.plan(5):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        await t.post_ok('api_external_orders_status',
                        json={
                            'store_id': store.store_id,
                            'external_id': uuid(),
                            'status': 'cancel'})
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')
        t.json_is('details.message', 'Order not found')


@pytest.mark.parametrize('order_status', ['complete', 'failed'])
async def test_cancel_complete(tap, dataset, api, order_status):
    with tap.plan(6):
        t = await api(role='token:web.external.tokens.0')

        order = await dataset.order(status=order_status, type='writeoff')
        tap.ok(order, 'заказ создан')
        tap.eq(order.status, order_status, 'статус')

        await t.post_ok('api_external_orders_status',
                        json={
                            'store_id': order.store_id,
                            'external_id': order.external_id,
                            'status': 'cancel'})
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'Order has already done')


@pytest.mark.parametrize('order_status',
                         ['reserving', 'approving', 'request'])
async def test_cancel(tap, dataset, api, order_status):
    with tap.plan(14):
        t = await api(role='token:web.external.tokens.0')

        order = await dataset.order(status=order_status, estatus='status1')
        tap.ok(order, 'заказ создан')
        tap.eq(order.status, order_status, 'статус')
        tap.eq(order.estatus, 'status1', 'неизвестный подстатус')

        await t.post_ok('api_external_orders_status',
                        json={
                            'store_id': order.store_id,
                            'external_id': order.external_id,
                            'status': 'cancel'})
        t.status_is(200, diag=True)
        t.json_is('order.order_id', order.order_id)
        t.json_is('order.store_id', order.store_id, 'резервируется')
        t.json_is('order.external_id',
                  order.external_id,
                  'external_id в ответе')
        t.json_is('order.status', order_status, 'заказ остался в обработке')

        lorder = await order.load(order.order_id)

        tap.ok(lorder, 'заказ загружен')
        tap.eq(lorder.status, order_status, 'статус')
        tap.eq(lorder.target, 'canceled', 'цель')
        tap.eq(lorder.revision, order.revision + 1, 'ревизия++')
        tap.eq(lorder.estatus, 'status1', 'сабстатус не менялся')
