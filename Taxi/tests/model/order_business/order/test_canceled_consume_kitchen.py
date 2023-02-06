from stall.model.suggest import Suggest


async def test_all_done(tap, dataset, wait_order_status, now):
    with tap.plan(15, 'успели сделать все кофе'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, stocks, components, products = await dataset.coffee(
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

        suggests = await Suggest.list_by_order(order, tags=['kitchen'])
        tap.eq(len(suggests), 2, 'есть два саджеста')
        tap.ok(
            [await s.done() for s in suggests], 'закрыли все саджесты',
        )

        tap.ok(await order.cancel(), 'отменяем')

        await wait_order_status(
            order, ('canceled', 'consume_kitchen'), user_done=user,
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'lost_kitchen', 'lost_kitchen')
        tap.eq(order.target, 'canceled', 'target: canceled')

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


async def test_one_done(tap, dataset, wait_order_status, now):
    with tap.plan(14, 'успели сделать 1 позицию'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, stocks, components, products = await dataset.coffee(
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

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = {
            s.product_id: s
            for s in await Suggest.list_by_order(
                order, status='request', tags=['kitchen'],
            )
        }
        tap.eq(len(suggests), 2, 'есть два саджеста')
        await suggests[products['cappuccino'].product_id].rm()

        tap.ok(await order.cancel(), 'отменяем')

        await wait_order_status(
            order, ('canceled', 'consume_kitchen'), user_done=user,
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'lost_kitchen', 'lost_kitchen')
        tap.eq(order.target, 'canceled', 'target: canceled')

        await stocks['comp_coffee1'].reload()
        tap.eq(
            stocks['comp_coffee1'].count,
            10 * components['coffee1'].quants - 10 * 4,
            'кофе1 остаток уменьшился на одну позицию'
        )
        tap.eq(
            stocks['comp_coffee1'].reserve,
            0,
            'кофе1 нет резерва'
        )

        await stocks['comp_milk1'].reload()
        tap.eq(
            stocks['comp_milk1'].count,
            10 * components['milk1'].quants - 10 * 120,
            'молоко1 остаток уменьшился на одну позицию'
        )
        tap.eq(
            stocks['comp_milk1'].reserve,
            0,
            'молоко1 нет резерва'
        )

        await stocks['comp_glass1'].reload()
        tap.eq(
            stocks['comp_glass1'].count,
            100 - 10,
            'стакан1 остаток уменьшился на одну позицию'
        )
        tap.eq(
            stocks['comp_glass1'].reserve,
            0,
            'стакан1 нет резерва'
        )


async def test_zero_done(tap, dataset, wait_order_status, now):
    with tap.plan(14, 'не успели сделать кофе вообще'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, stocks, components, products = await dataset.coffee(
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

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(
            order, status='request', tags=['kitchen'],
        )
        tap.eq(len(suggests), 2, 'есть два саджеста')

        tap.ok(await order.cancel(), 'отменяем')

        await wait_order_status(order, ('canceled', 'consume_kitchen'),)

        await order.business.order_changed()

        tap.ok(await order.reload(), 'перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'lost_kitchen', 'lost_kitchen')
        tap.eq(order.target, 'canceled', 'target: canceled')

        await stocks['comp_coffee1'].reload()
        tap.eq(
            stocks['comp_coffee1'].count,
            10 * components['coffee1'].quants,
            'кофе1 на месте',
        )
        tap.eq(
            stocks['comp_coffee1'].reserve,
            0,
            'кофе1 нет резерва',
        )

        await stocks['comp_milk1'].reload()
        tap.eq(
            stocks['comp_milk1'].count,
            10 * components['milk1'].quants,
            'молоко1 на месте'
        )
        tap.eq(
            stocks['comp_milk1'].reserve,
            0,
            'молоко1 нет резерва',
        )

        await stocks['comp_glass1'].reload()
        tap.eq(
            stocks['comp_glass1'].count,
            100,
            'стакан1 на месте'
        )
        tap.eq(
            stocks['comp_glass1'].reserve,
            0,
            'стакан1 нет резерва'
        )
