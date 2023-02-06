async def test_consume_kitchen(tap, dataset, wait_order_status, now):
    with tap.plan(12, 'списываем компоненты до приготовления блюд'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, stocks, components, products = await dataset.coffee(
            shelves_meta=(
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
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
            order, ('complete', 'consume_kitchen'), user_done=user,
        )

        tap.ok(await order.business.order_changed(), 'тратим компоненты')

        tap.ok(await order.reload(), 'перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'lost_kitchen', 'lost_kitchen')
        tap.eq(order.target, 'complete', 'target: complete')

        await stocks['comp_coffee1'].reload()
        tap.eq(
            stocks['comp_coffee1'].count,
            10 * components['coffee1'].quants - (10 * 4 + 10 * 4),
            'кофе1 остаток уменьшился'
        )
        tap.eq(
            stocks['comp_coffee1'].reserve,
            0,
            'кофе1 нет резерва'
        )

        await stocks['comp_milk1'].reload()
        tap.eq(
            stocks['comp_milk1'].count,
            10 * components['milk1'].quants - (10 * 80 + 10 * 120),
            'молоко1 остаток уменьшился'
        )
        tap.eq(
            stocks['comp_milk1'].reserve,
            0,
            'молоко1 нет резерва'
        )

        await stocks['comp_glass1'].reload()
        tap.eq(
            stocks['comp_glass1'].count,
            100 - (10 + 10),
            'стакан1 остаток уменьшился'
        )
        tap.eq(
            stocks['comp_glass1'].reserve,
            0,
            'стакан1 нет резерва'
        )
