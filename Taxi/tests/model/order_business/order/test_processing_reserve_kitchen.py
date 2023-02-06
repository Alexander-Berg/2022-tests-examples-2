async def test_reserve_kitchen(tap, dataset, wait_order_status):
    with tap.plan(13, 'все зарезервировали'):
        store = await dataset.store()
        _, stocks, components, products = await dataset.coffee(
            shelves_meta=(
                ('store', 'store'),
                ('comp', 'kitchen_components'),
            ),
            stocks_meta=(
                ('store', 'coffee1', 10),
                ('comp', 'coffee1', 1),
                ('comp', 'milk1', 2),
                ('comp', 'glass1', 3),
            ),
            store=store,
        )

        order = await dataset.order(
            store=store,
            type='order',
            status='processing',
            required=[
                {
                    'product_id': components['coffee1'].product_id,
                    'count': 10,
                },
                {
                    'product_id': products['cappuccino'].product_id,
                    'count': 1,
                },
                {
                    'product_id': products['latte'].product_id,
                    'count': 2,
                },
            ],
        )

        await wait_order_status(order, ('processing', 'reserve_kitchen'))

        await order.business.order_changed()
        await order.business.order_changed()
        await order.reload()

        tap.eq(order.status, 'processing', 'processing')
        tap.eq(
            order.estatus,
            'calculate_order_weight',
            'calculate_order_weight',
        )
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'нет проблем')

        await stocks['store_coffee1'].reload()
        tap.eq(stocks['store_coffee1'].count, 10, 'кофе1 остаток')
        tap.eq(stocks['store_coffee1'].reserve, 10, 'кофе1 резерв')

        await stocks['comp_coffee1'].reload()
        tap.eq(
            stocks['comp_coffee1'].count,
            1 * components['coffee1'].quants,
            'кофе1 остаток'
        )
        tap.eq(
            stocks['comp_coffee1'].reserve,
            1 * 4 + 2 * 4,
            'кофе1 резерв'
        )

        await stocks['comp_milk1'].reload()
        tap.eq(
            stocks['comp_milk1'].count,
            2 * components['milk1'].quants,
            'молоко1 остаток'
        )
        tap.eq(
            stocks['comp_milk1'].reserve,
            1 * 80 + 2 * 120,
            'молоко1 резерв'
        )

        await stocks['comp_glass1'].reload()
        tap.eq(
            stocks['comp_glass1'].count,
            3 * components['glass1'].quants,
            'стакан1 остаток'
        )
        tap.eq(
            stocks['comp_glass1'].reserve,
            1 * 1 + 2 * 1,
            'стакан1 резерв'
        )


async def test_failed(tap, dataset, wait_order_status, uuid):
    with tap.plan(4, 'ошибка резервирования'):
        order = await dataset.order(
            type='order',
            status='processing',
            required=[
                {
                    'product_id': uuid(),
                    'count': 1
                },
            ],
        )

        await wait_order_status(order, ('processing', 'reserve_kitchen'))

        await order.business.order_changed()
        await order.reload()

        tap.eq(order.status, 'failed', 'processing')
        tap.eq(order.estatus, 'begin', 'suggests_error')

        tap.eq(len(order.problems), 1, 'Проблемы')
