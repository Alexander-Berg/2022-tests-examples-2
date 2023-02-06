async def test_delivery_status(tap, dataset, uuid):
    with tap.plan(8, 'Проверка сопоставления внешнего статуса заказа'):

        with await dataset.order(
                status='approving',
        ) as order:
            tap.eq(order.external_delivery_status(), 'unassigned', 'unassigned')

        with await dataset.order(
                status='approving',
                courier_id=uuid(),
        ) as order:
            tap.eq(order.external_delivery_status(), 'assigned', 'assigned')

        with await dataset.order(
                status='delivery',
                estatus='enqueued',
                courier_id=uuid(),
        ) as order:
            tap.eq(order.external_delivery_status(), 'enqueued', 'enqueued')

        with await dataset.order(
                status='delivery',
                estatus='en_route',
                courier_id=uuid(),
        ) as order:
            tap.eq(order.external_delivery_status(), 'en_route', 'en_route')

        with await dataset.order(
                status='delivery',
                estatus='wait_client',
                courier_id=uuid(),
        ) as order:
            tap.eq(order.external_delivery_status(),
                   'wait_client', 'wait_client')

        with await dataset.order(
                status='complete',
                estatus='done',
                courier_id=uuid(),
        ) as order:
            tap.eq(order.external_delivery_status(), 'delivered', 'delivered')

        with await dataset.order(
                status='canceled',
                estatus='done',
                courier_id=uuid(),
        ) as order:
            tap.eq(order.external_delivery_status(), 'canceled', 'canceled')

        with await dataset.order(
                status='failed',
                estatus='done',
                courier_id=uuid(),
        ) as order:
            tap.eq(order.external_delivery_status(), 'canceled', 'canceled')
