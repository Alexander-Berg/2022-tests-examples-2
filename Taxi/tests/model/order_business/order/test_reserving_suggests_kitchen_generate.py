from stall.model.suggest import Suggest


async def test_simple(tap, dataset, wait_order_status):
    with tap.plan(10, 'саджесты для кофе'):
        store = await dataset.store()
        shelves, _, _, products = await dataset.coffee(
            shelves_meta=(
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
            ),
            stocks_meta=(
                ('comp', 'coffee1', 1),
                ('comp', 'milk1', 2),
                ('comp', 'glass1', 3),
            ),
            store=store,
        )

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            required=[
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

        await wait_order_status(
            order, ('reserving', 'suggests_kitchen_generate'),
        )

        await order.business.order_changed()
        await order.reload()

        tap.eq(order.status, 'approving', 'approving')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'нет проблем')

        suggests = {
            (s.shelf_id, s.product_id): s
            for s in await Suggest.list_by_order(order)
        }
        tap.eq(len(suggests), 2, 'два саджеста')

        s1 = suggests[
            shelves['on_demand'].shelf_id, products['cappuccino'].product_id
        ]
        tap.eq(s1.count, 1, 'count')
        tap.ok('kitchen' in s1.conditions.tags, 'tags')

        s2 = suggests[
            shelves['on_demand'].shelf_id, products['latte'].product_id
        ]
        tap.eq(s2.count, 2, 'count')
        tap.ok('kitchen' in s2.conditions.tags, 'tags')


async def test_problems(tap, dataset, wait_order_status):
    with tap.plan(6, 'нет саджестов при наличии проблем'):
        store = await dataset.store()
        _, _, _, products = await dataset.coffee(
            shelves_meta=(
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
            ),
            stocks_meta=(
                ('comp', 'coffee1', 1),
                ('comp', 'milk1', 2),
            ),
            store=store,
        )

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            required=[
                {
                    'product_id': products['cappuccino'].product_id,
                    'count': 1,
                },
            ],
            vars={'editable': True},
        )

        await wait_order_status(
            order, ('reserving', 'suggests_kitchen_generate'),
        )

        await order.business.order_changed()
        await order.reload()

        tap.eq(order.status, 'approving', 'approving')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 1, 'есть проблема')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 0, 'не генерим саджесты')
