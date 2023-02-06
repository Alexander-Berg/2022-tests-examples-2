import pytest


@pytest.mark.parametrize('order_status', ['reserving', 'request', 'approving'])
async def test_cancel(tap, order_status, dataset):
    with tap.plan(8, 'Отмена заказа'):

        product = await dataset.product()
        store = await dataset.store()
        order = await dataset.order(
            store=store,
            type='order',
            status=order_status,
            target='canceled',
            required = [
                {
                    'product_id': product.product_id,
                    'count': 1
                },
            ],
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, order_status, order_status)
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'canceled', 'target: canceled')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'canceled', 'target: canceled')


@pytest.mark.parametrize('order_status', ['processing', 'complete', 'failed'])
async def test_skip_cancel(tap, order_status, dataset):
    with tap.plan(6, 'Отмена заказа'):

        product = await dataset.product()
        store = await dataset.store()
        order = await dataset.order(
            store=store,
            type='order',
            status=order_status,
            target='canceled',
            required = [
                {
                    'product_id': product.product_id,
                    'count': 1
                },
            ],
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, order_status, order_status)
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'canceled', 'target: canceled')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.ne(order.status, 'canceled', order.status)
