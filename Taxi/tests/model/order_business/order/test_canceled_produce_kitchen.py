from stall.model.stock import Stock


async def test_simple(tap, dataset, wait_order_status, now):
    with tap.plan(12, 'производим кофе, чтобы корректно списать'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, _, _, products = await dataset.coffee(
            shelves_meta=(
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
                ('trash', 'trash'),
                ('lost', 'lost'),
            ),
            stocks_meta=(
                ('comp', 'coffee1', 10),
                ('comp', 'milk1', 10),
                ('comp', 'glass1', 100),
            ),
            store=store,
        )

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            acks=[user.user_id],
            approved=now(),
            required=[
                {
                    'product_id': products['cappuccino'].product_id,
                    'count': 10,
                },
                {
                    'product_id': products['latte'].product_id,
                    'count': 10,
                },
            ],
        )

        await wait_order_status(
            order, ('processing', 'waiting'), user_done=user,
        )

        tap.ok(await order.cancel(), 'отменяем')

        await wait_order_status(
            order, ('canceled', 'produce_kitchen'), user_done=user,
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'trash_kitchen', 'trash_kitchen')
        tap.eq(order.target, 'canceled', 'target: canceled')

        stocks_on_demand = {
            s.product_id: s
            for s in await Stock.list_by_order(
                order, shelf_type='kitchen_on_demand',
            )
        }
        tap.eq(len(stocks_on_demand), 2, 'приготовили 2 типа кофе')
        tap.eq(
            stocks_on_demand[products['cappuccino'].product_id].count,
            10,
            '10 капучино',
        )
        tap.eq(
            stocks_on_demand[products['cappuccino'].product_id].reserve,
            10,
            'все капучино в резерве',
        )
        tap.eq(
            stocks_on_demand[products['latte'].product_id].count,
            10,
            '10 латте',
        )
        tap.eq(
            stocks_on_demand[products['latte'].product_id].reserve,
            10,
            'все латте в резерве',
        )
