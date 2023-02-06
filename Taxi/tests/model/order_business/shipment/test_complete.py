# pylint: disable=unused-variable


async def test_done(tap, dataset, now, wait_order_status):
    with tap.plan(11, 'Заказ обработан'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()
        user  = await dataset.user(store=store)

        shelf1 = await dataset.shelf(store=store, type='store')
        shelf2 = await dataset.shelf(store=store, type='markdown')

        stock1 = await dataset.stock(
            product=product1, store=store, shelf=shelf1, count=110)
        stock2 = await dataset.stock(
            product=product2, store=store, shelf=shelf2, count=220)

        order = await dataset.order(
            store=store,
            type = 'shipment',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 100,
                },
                {
                    'product_id': product2.product_id,
                    'count': 200,
                    'price_type': 'markdown',
                },
                {
                    'product_id': product3.product_id,
                    'count': 300,
                },
            ],
        )
        tap.ok(order, 'Заказ создан')

        await wait_order_status(order, ('complete', 'done'), user_done=user)

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'done', 'done')

        tap.eq(len(order.problems), 1, 'Проблемы были, но не повлияли')
        tap.eq(order.problems[0].product_id, product3.product_id, 'product_id')

        with await stock1.reload() as stock:
            tap.eq(stock.count, 110-100, 'count')
            tap.eq(stock.reserve, 0, 'reserve')

        with await stock2.reload() as stock:
            tap.eq(stock.count, 220-200, 'count')
            tap.eq(stock.reserve, 0, 'reserve')
