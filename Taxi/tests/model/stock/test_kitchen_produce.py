from stall.model.stock import Stock


# pylint: disable=too-many-statements
async def test_kitchen_produce(tap, dataset):
    with tap.plan(35, 'при производстве кухни пишем в лог потраченные ПФ'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='kitchen_on_demand')

        comp1 = await dataset.product(quants=1)
        comp2 = await dataset.product(quants=2)
        comp3 = await dataset.product(quants=3)

        product1 = await dataset.product(
            components=[
                [
                    {'product_id': comp1.product_id, 'count': 1},
                ],
                [
                    {'product_id': comp2.product_id, 'count': 2},
                    {'product_id': comp3.product_id, 'count': 3},
                ],
            ],
        )
        product2 = await dataset.product(
            components=[
                [
                    {'product_id': comp1.product_id, 'count': 1},
                ],
                [
                    {'product_id': comp3.product_id, 'count': 3},
                ],
            ],
        )

        order = await dataset.order(store_id=store.store_id)

        order.components.add(
            product1.product_id,
            [
                {'product_id': comp1.product_id, 'count': 1},
                {'product_id': comp2.product_id, 'count': 2},
            ]
        )
        order.components.add(
            product2.product_id,
            [
                {'product_id': comp1.product_id, 'count': 1},
                {'product_id': comp3.product_id, 'count': 3},
            ]
        )
        await order.save()

        tap.eq(
            order.components.total(product1.product_id),
            1,
            'порции для первого продукта',
        )
        tap.eq(
            order.components.total(product2.product_id),
            1,
            'порции для второго продукта',
        )

        with await Stock.do_kitchen_produce(
                order, shelf, product1, 1,
        ) as stock:
            tap.eq(stock.product_id, product1.product_id, 'корректный товар')
            tap.eq(stock.count, 1, 'остаток')
            tap.eq(stock.reserve, 1, 'резерв')

            logs1 = (await stock.list_log()).list
            tap.eq(len(logs1), 1, 'одна запись')

            with logs1[0] as log:
                tap.eq(log.recount, None, 'основная запись')
                tap.eq(log.type, 'kitchen_produce', 'type')
                tap.eq(log.product_id, product1.product_id, 'product_id')
                tap.eq(log.count, 1, 'остаток')
                tap.eq(log.reserve, 1, 'резерв')
                tap.eq(log.delta_count, 1, 'delta_count')
                tap.eq(log.delta_reserve, 1, 'delta_reserve')
                tap.eq(
                    log.vars['components'],
                    [
                        [
                            {
                                'product_id': comp1.product_id,
                                'count': 1,
                                'quants': 1,
                                'portions': 1,
                            },
                        ],
                        [
                            {
                                'product_id': comp2.product_id,
                                'count': 2,
                                'quants': 2,
                                'portions': 1,
                            },
                        ]
                    ],
                    'components',
                )

        order.components.add(
            product1.product_id,
            [
                {'product_id': comp1.product_id, 'count': 1},
                {'product_id': comp2.product_id, 'count': 2},
            ]
        )
        await order.save()

        tap.eq(
            order.components.total(product1.product_id),
            2,
            'больше порций для первого продукта',
        )

        with await Stock.do_kitchen_produce(
                order, shelf, product1, 2,
        ) as stock:
            tap.eq(stock.product_id, product1.product_id, 'корректный товар')
            tap.eq(stock.count, 2, 'остаток')
            tap.eq(stock.reserve, 2, 'резерв')

            logs2 = (await stock.list_log()).list
            tap.eq(len(logs2), 3, 'записей прибавилось')

            with logs2[-1] as log:
                tap.eq(log.recount, None, 'основная запись')
                tap.eq(log.type, 'kitchen_produce', 'type')
                tap.eq(log.product_id, product1.product_id, 'product_id')
                tap.eq(log.count, 2, 'count')
                tap.eq(log.reserve, 2, 'reserve')
                tap.eq(log.delta_count, 2, 'delta_count')
                tap.eq(log.delta_reserve, 2, 'delta_reserve')
                tap.eq(
                    log.vars['components'],
                    [
                        [
                            {
                                'product_id': comp1.product_id,
                                'count': 1,
                                'quants': 1,
                                'portions': 2,
                            },
                        ],
                        [
                            {
                                'product_id': comp2.product_id,
                                'count': 2,
                                'quants': 2,
                                'portions': 2,
                            },
                        ]
                    ],
                    'components',
                )

            with logs2[-2] as log:
                tap.eq(log.recount, logs1[-1].log_id, 'предыдущий лог')
                tap.eq(log.type, 'kitchen_produce', 'type')
                tap.eq(log.product_id, product1.product_id, 'product_id')
                tap.eq(log.count, 0, 'count')
                tap.eq(log.reserve, 0, 'reserve')
                tap.eq(log.delta_count, -1, 'delta_count')
                tap.eq(log.delta_reserve, -1, 'delta_reserve')
                tap.eq(
                    log.vars['components'],
                    [
                        [
                            {
                                'product_id': comp1.product_id,
                                'count': 1,
                                'quants': 1,
                                'portions': 1,
                            },
                        ],
                        [
                            {
                                'product_id': comp2.product_id,
                                'count': 2,
                                'quants': 2,
                                'portions': 1,
                            },
                        ]
                    ],
                    'components',
                )


async def test_bad_shelf(tap, dataset):
    with tap.plan(1, 'проверфяем корректность полки'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='store')

        comp1 = await dataset.product()
        comp2 = await dataset.product()

        product = await dataset.product(
            components=[
                [
                    {'product_id': comp1.product_id, 'count': 1},
                ],
                [
                    {'product_id': comp2.product_id, 'count': 2},
                ],
            ],
        )

        order = await dataset.order(store_id=store.store_id)

        with tap.raises(AssertionError, 'полка не для кухни'):
            await Stock.do_kitchen_produce(order, shelf, product, 1)


async def test_bad_product(tap, dataset):
    with tap.plan(1, 'проверфяем что товар с рецептом'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='kitchen_components')

        product = await dataset.product()

        order = await dataset.order(store_id=store.store_id)

        with tap.raises(AssertionError, 'товар не блюдо'):
            await Stock.do_kitchen_produce(order, shelf, product, 1)

