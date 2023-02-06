async def test_simple(tap, dataset, wait_order_status):
    with tap.plan(13, 'все зарезервировали с первой попытки'):
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
            status='reserving',
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

        await wait_order_status(order, ('reserving', 'reserve_kitchen'))

        await order.business.order_changed()
        await order.business.order_changed()
        await order.reload()

        tap.eq(order.status, 'reserving', 'reserving')
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


async def test_low_product(tap, dataset, wait_order_status):
    with tap.plan(14, 'не хватает товара с обычной полки'):
        store = await dataset.store()
        _, stocks, components, products = await dataset.coffee(
            shelves_meta=(
                ('store', 'store'),
                ('comp', 'kitchen_components'),
            ),
            stocks_meta=(
                ('store', 'coffee1', 1),
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
            required=[
                {
                    'product_id': components['coffee1'].product_id,
                    'count': 10,
                },
                {
                    'product_id': products['cappuccino'].product_id,
                    'count': 1,
                },
            ],
        )

        await wait_order_status(order, ('reserving', 'reserve_kitchen'))

        await order.business.order_changed()
        await order.reload()

        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'begin', 'begin')

        tap.eq(len(order.problems), 1, 'есть проблема с обычным товаром')
        tap.eq(
            order.problems[0].product_id,
            stocks['store_coffee1'].product_id,
            'не хватает кофе1',
        )
        tap.eq(order.problems[0].count, 9, 'количество установлено')

        await stocks['store_coffee1'].reload()
        tap.eq(stocks['store_coffee1'].count, 1, 'кофе1 остаток')
        tap.eq(stocks['store_coffee1'].reserve, 1, 'кофе1 резерв')

        await stocks['comp_coffee1'].reload()
        tap.eq(
            stocks['comp_coffee1'].count,
            1 * components['coffee1'].quants,
            'кофе1 остаток'
        )
        tap.eq(
            stocks['comp_coffee1'].reserve,
            1 * 4,
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
            1 * 80,
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
            1 * 1,
            'стакан1 резерв'
        )


async def test_low_components(tap, dataset, wait_order_status):
    with tap.plan(14, 'не хватает одного из компонент'):
        store = await dataset.store()
        _, stocks, components, products = await dataset.coffee(
            shelves_meta=(
                ('store', 'store'),
                ('comp', 'kitchen_components'),
            ),
            stocks_meta=(
                ('store', 'coffee1', 1),
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
            required=[
                {
                    'product_id': components['coffee1'].product_id,
                    'count': 1,
                },
                {
                    'product_id': products['cappuccino'].product_id,
                    'count': 10,
                },
            ],
        )

        await wait_order_status(order, ('reserving', 'reserve_kitchen'))

        await order.business.order_changed()
        await order.reload()

        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'begin', 'begin')

        tap.eq(len(order.problems), 1, 'есть проблема с компонентами')
        tap.eq(
            order.problems[0].product_id,
            products['cappuccino'].product_id,
            'не хватает стаканчиков на столько порций',
        )
        tap.eq(order.problems[0].count, 0, 'здесь всегда 0 пишем')

        await stocks['store_coffee1'].reload()
        tap.eq(stocks['store_coffee1'].count, 1, 'обычный кофе1 остаток')
        tap.eq(stocks['store_coffee1'].reserve, 1, 'обычный кофе1 резерв')

        await stocks['comp_coffee1'].reload()
        tap.eq(
            stocks['comp_coffee1'].count,
            1 * components['coffee1'].quants,
            'кофе1 остаток'
        )
        tap.eq(
            stocks['comp_coffee1'].reserve,
            3 * 4,
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
            3 * 80,
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
            3 * 1,
            'стакан1 резерв'
        )


async def test_lock_components(tap, dataset, wait_order_status):
    with tap.plan(12, 'не хватило на два типа кофе'):
        store = await dataset.store()
        _, stocks, components, products = await dataset.coffee(
            shelves_meta=(
                ('comp', 'kitchen_components'),
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
            required=[
                {
                    'product_id': products['cappuccino'].product_id,
                    'count': 10,
                },
                {
                    'product_id': products['latte'].product_id,
                    'count': 1,
                },
            ],
        )

        await wait_order_status(order, ('reserving', 'reserve_kitchen'))

        await order.business.order_changed()
        await order.reload()

        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'begin', 'begin')

        tap.eq(len(order.problems), 2, 'есть проблемы')
        tap.eq(
            order.problems[0].product_id,
            products['cappuccino'].product_id,
            'не хватает стаканчиков на 10 столько порций',
        )
        tap.eq(
            order.problems[1].product_id,
            products['latte'].product_id,
            'здесь тоже не хватает',
        )

        await stocks['comp_coffee1'].reload()
        tap.eq(
            stocks['comp_coffee1'].count,
            1 * components['coffee1'].quants,
            'кофе1 остаток'
        )
        tap.eq(
            stocks['comp_coffee1'].reserve,
            3 * 4,
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
            3 * 80,
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
            3 * 1,
            'стакан1 резерв'
        )


async def test_crash(tap, dataset, wait_order_status):
    with tap.plan(13, 'молоток во время резервирования'):
        store = await dataset.store()
        _, stocks, components, products = await dataset.coffee(
            shelves_meta=(
                ('comp', 'kitchen_components'),
            ),
            stocks_meta=(
                ('comp', 'coffee1', 1),
                ('comp', 'milk1', 2),
                ('comp', 'glass1', 5),
            ),
            store=store,
        )

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            required=[
                {
                    'product_id': products['cappuccino'].product_id,
                    'count': 2,
                },
                {
                    'product_id': products['latte'].product_id,
                    'count': 2,
                },
            ],
        )

        tap.ok(
            await stocks['comp_coffee1'].do_reserve(order, 2 * 4),
            'зарезервировали кофе1 для двух порций капучино',
        )
        tap.ok(
            await stocks['comp_milk1'].do_reserve(order, 2 * 80),
            'зарезервировали молоко1 для двух порций капучино и упал молоток',
        )

        await wait_order_status(order, ('reserving', 'reserve_kitchen'))

        await order.business.order_changed()
        await order.business.order_changed()
        await order.reload()

        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(
            order.estatus,
            'calculate_order_weight',
            'calculate_order_weight'
        )
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'не слышали о проблемах')

        await stocks['comp_coffee1'].reload()
        tap.eq(
            stocks['comp_coffee1'].count,
            1 * components['coffee1'].quants,
            'кофе1 остаток'
        )
        tap.eq(
            stocks['comp_coffee1'].reserve,
            2 * 4 + 2 * 4,
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
            2 * 80 + 2 * 120,
            'молоко1 резерв'
        )

        await stocks['comp_glass1'].reload()
        tap.eq(
            stocks['comp_glass1'].count,
            5 * components['glass1'].quants,
            'стакан1 остаток'
        )
        tap.eq(
            stocks['comp_glass1'].reserve,
            2 + 2,
            'стакан1 резерв'
        )
