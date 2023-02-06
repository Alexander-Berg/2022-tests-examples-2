# pylint: disable=unused-variable


async def test_begin(tap, dataset, now, wait_order_status):
    with tap.plan(7, 'Сборка заказа'):

        store = await dataset.store()
        user  = await dataset.user(store=store)
        shelf = await dataset.shelf(store=store, type='store', order=1)
        trash = await dataset.shelf(store=store, type='trash', order=100)

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
        )

        await wait_order_status(order, ('processing', 'begin'))
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'products_find', 'products_find')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')
