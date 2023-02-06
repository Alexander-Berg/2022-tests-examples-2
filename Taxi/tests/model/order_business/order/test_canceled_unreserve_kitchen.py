from stall.model.suggest import Suggest


async def test_all_done(tap, dataset, wait_order_status, now):
    with tap.plan(12, 'все приготовленное кофе идет в потери'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, _, _, products = await dataset.coffee(
            shelves_meta=(
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
                ('trash', 'trash'),
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
            order, ('canceled', 'unreserve_kitchen'), user_done=user,
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'перезабрали заказ')

        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'consume_kitchen', 'consume_kitchen')
        tap.eq(order.target, 'canceled', 'canceled')

        tap.eq(
            len(order.vars('over_required', [])),
            0,
            'в перерасходе пусто',
        )
        tap.eq(
            order.components.total(products['cappuccino'].product_id),
            10,
            'резерв для капучино держим',
        )
        tap.eq(
            order.components.total(products['latte'].product_id),
            10,
            'резерв для латте держим',
        )


async def test_one_done(tap, dataset, wait_order_status, now):
    with tap.plan(
            13, 'одну позицию полностью в потери, вторую разрезервируем',
    ):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, _, _, products = await dataset.coffee(
            shelves_meta=(
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
                ('trash', 'trash'),
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
                order, status='request', shelf_types='kitchen_on_demand',
            )
        }
        tap.eq(len(suggests), 2, 'есть два саджеста')

        tap.ok(
            await suggests[products['cappuccino'].product_id].done('done'),
            'капучино успели сделать',
        )
        tap.ok(
            await suggests[products['latte'].product_id].rm(),
            'латте не успели сделать',
        )

        tap.ok(await order.cancel(), 'отменяем')

        await wait_order_status(
            order, ('canceled', 'unreserve_kitchen'), user_done=user,
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'consume_kitchen', 'consume_kitchen')
        tap.eq(order.target, 'canceled', 'canceled')

        tap.eq(
            len(order.vars('over_required', [])),
            0,
            'в перерасход ничего не кладем',
        )
        tap.eq(
            order.components.total(products['cappuccino'].product_id),
            10,
            'резерв для капучино держим, чтобы списать',
        )
        tap.eq(
            order.components.total(products['latte'].product_id),
            0,
            'резерв для латте не держим',
        )


async def test_one_error(tap, dataset, wait_order_status, now):
    with tap.plan(18, '1 кофе разлили'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, _, _, products = await dataset.coffee(
            shelves_meta=(
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
                ('trash', 'trash'),
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
                order, status='request', shelf_types='kitchen_on_demand',
            )
        }
        tap.eq(len(suggests), 2, 'есть два саджеста')

        tap.ok(
            await suggests[products['cappuccino'].product_id].done('done'),
            'капучино успели сделать',
        )
        tap.ok(
            await suggests[products['latte'].product_id].done(
                'error', reason={'count': 1},
            ),
            '1 латте упал на пол =(',
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = {
            s.product_id: s
            for s in await Suggest.list_by_order(
                order, status='request', shelf_types='kitchen_on_demand',
            )
        }
        tap.eq(len(suggests), 1, 'появился еще один саджест')
        tap.eq(
            suggests[products['latte'].product_id].count,
            10,
            '10 порций латте',
        )

        tap.ok(
            await suggests[products['latte'].product_id].done('done'),
            'сделали все латте',
        )

        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(await order.cancel(), 'отменяем')

        await wait_order_status(
            order, ('canceled', 'unreserve_kitchen'), user_done=user,
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'consume_kitchen', 'consume_kitchen')
        tap.eq(order.target, 'canceled', 'canceled')

        over_required = {
            r['product_id']: r['count']
            for r in order.vars('over_required')
        }

        tap.eq(
            over_required[products['latte'].product_id],
            1,
            'в перерасходе 1 порция латте',
        )

        tap.eq(
            order.components.total(products['cappuccino'].product_id),
            10,
            'резерв для капучино держим, чтобы списать',
        )
        tap.eq(
            order.components.total(products['latte'].product_id),
            10,
            'резерв для латте также держим',
        )


async def test_zero_done(tap, dataset, wait_order_status, now):
    with tap.plan(11, 'не успели сделать кофе вообще'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, _, _, products = await dataset.coffee(
            shelves_meta=(
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
                ('trash', 'trash'),
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

        await wait_order_status(order, ('canceled', 'unreserve_kitchen'),)

        await order.business.order_changed()

        tap.ok(await order.reload(), 'перезабрали заказ')
        tap.eq(order.status, 'canceled', 'canceled')
        tap.eq(order.estatus, 'consume_kitchen', 'consume_kitchen')
        tap.eq(order.target, 'canceled', 'target: canceled')

        tap.eq(
            len(order.vars('over_required', [])),
            0,
            'в перерасходе пусто',
        )
        tap.eq(
            order.components.total(products['cappuccino'].product_id),
            0,
            'резерв для капучино не держим',
        )
        tap.eq(
            order.components.total(products['latte'].product_id),
            0,
            'резерв для латте не держим',
        )
