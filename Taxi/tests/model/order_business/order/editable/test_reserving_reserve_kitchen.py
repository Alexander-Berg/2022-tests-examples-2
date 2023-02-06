async def test_add(tap, dataset, wait_order_status, now):
    with tap.plan(14, 'хитро добавляем количество порций'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, stocks, components, products = await dataset.coffee(
            shelves_meta=(
                ('comp1', 'kitchen_components'),
                ('comp2', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
            ),
            stocks_meta=(
                ('comp1', 'coffee1', 1),
                ('comp1', 'milk1', 1),
                ('comp1', 'glass1', 1),
                ('comp2', 'glass2', 2),
            ),
            store=store,
        )

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
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
            vars={'editable': True},
        )

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()

        tap.eq(len(order.problems), 1, 'есть проблема')
        tap.eq(
            order.problems[0].product_id,
            products['latte'].product_id,
            'не хватает стаканов для латте',
        )

        # NOTE: все три стакана зарезервированы:
        # 2 для капучино и один 1 латте
        # после редактирования убираем капучино совсем,
        # НО увеличиваем латте до 3 порций

        order.vars['required'] = [
            {
                'product_id': products['latte'].product_id,
                'count': 2,
            },
            {
                'product_id': products['latte'].product_id,
                'count': 1,
            },
        ]
        tap.ok(await order.save(), 'уменьшаем количество')

        await wait_order_status(order, ('processing', 'suggests_complete'))

        await order.business.order_changed()
        await order.reload()

        tap.eq(len(order.problems), 0, 'нет проблем')

        await stocks['comp1_coffee1'].reload()
        tap.eq(
            stocks['comp1_coffee1'].count,
            1 * components['coffee1'].quants,
            'кофе1 остаток'
        )
        tap.eq(
            stocks['comp1_coffee1'].reserve,
            3 * 4,
            'кофе1 резерв'
        )

        await stocks['comp1_milk1'].reload()
        tap.eq(
            stocks['comp1_milk1'].count,
            1 * components['milk1'].quants,
            'молоко1 остаток'
        )
        tap.eq(
            stocks['comp1_milk1'].reserve,
            3 * 120,
            'молоко1 резерв'
        )

        await stocks['comp1_glass1'].reload()
        tap.eq(
            stocks['comp1_glass1'].count,
            1 * components['glass1'].quants,
            'стакан1 остаток'
        )
        tap.eq(
            stocks['comp1_glass1'].reserve,
            1 * 1,
            'стакан1 резерв'
        )

        await stocks['comp2_glass2'].reload()
        tap.eq(
            stocks['comp2_glass2'].count,
            2 * components['glass2'].quants,
            'стакан2 остаток'
        )
        tap.eq(
            stocks['comp2_glass2'].reserve,
            2 * 1,
            'стакан2 резерв'
        )


async def test_rm(tap, dataset, wait_order_status, now):
    with tap.plan(11, 'убавляем количество порций'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, stocks, components, products = await dataset.coffee(
            shelves_meta=(
                ('store', 'store'),
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
            ),
            stocks_meta=(
                ('store', 'coffee1', 10),
                ('comp', 'coffee1', 1),
                ('comp', 'milk1', 1),
                ('comp', 'glass1', 3),
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
                    'product_id': components['coffee1'].product_id,
                    'count': 1,
                },
                {
                    'product_id': products['cappuccino'].product_id,
                    'count': 2,
                },
            ],
            vars={'editable': True},
        )

        await wait_order_status(order, ('processing', 'suggests_complete'))

        await order.business.order_changed()
        await order.reload()

        tap.eq(len(order.problems), 0, 'нет проблем')

        order.vars['required'] = [
            {
                'product_id': components['coffee1'].product_id,
                'count': 2,
            },
            {
                'product_id': products['cappuccino'].product_id,
                'count': 1,
            },
        ]
        tap.ok(await order.save(), 'редактируем заказ')

        await wait_order_status(order, ('processing', 'suggests_complete'))

        await order.business.order_changed()
        await order.reload()

        tap.eq(len(order.problems), 0, 'нет проблем')

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
            1 * components['milk1'].quants,
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


async def test_rm_all(tap, dataset, wait_order_status, now):
    with tap.plan(11, 'полностью убираем кухню их заказа'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, stocks, components, products = await dataset.coffee(
            shelves_meta=(
                ('store', 'store'),
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
            ),
            stocks_meta=(
                ('store', 'coffee1', 10),
                ('comp', 'coffee1', 1),
                ('comp', 'milk1', 1),
                ('comp', 'glass1', 3),
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
                    'product_id': components['coffee1'].product_id,
                    'count': 1,
                },
                {
                    'product_id': products['cappuccino'].product_id,
                    'count': 1,
                },
            ],
            vars={'editable': True},
        )

        await wait_order_status(order, ('processing', 'suggests_complete'))

        await order.business.order_changed()
        await order.reload()

        tap.eq(len(order.problems), 0, 'нет проблем')

        order.vars['required'] = [
            {
                'product_id': components['coffee1'].product_id,
                'count': 1,
            },
        ]
        tap.ok(await order.save(), 'редактируем заказ')

        await wait_order_status(order, ('processing', 'suggests_complete'))

        await order.business.order_changed()
        await order.reload()

        tap.eq(len(order.problems), 0, 'нет проблем')

        await stocks['comp_coffee1'].reload()
        tap.eq(
            stocks['comp_coffee1'].count,
            1 * components['coffee1'].quants,
            'кофе1 остаток'
        )
        tap.eq(
            stocks['comp_coffee1'].reserve,
            0,
            'кофе1 резерв'
        )

        await stocks['comp_milk1'].reload()
        tap.eq(
            stocks['comp_milk1'].count,
            1 * components['milk1'].quants,
            'молоко1 остаток'
        )
        tap.eq(
            stocks['comp_milk1'].reserve,
            0,
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
            0,
            'стакан1 резерв'
        )


async def test_over_required(tap, dataset, now, wait_order_status):
    with tap.plan(20, 'корректо резервируем в с перерасходом'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, stocks, components, products = await dataset.coffee(
            shelves_meta=(
                ('store', 'store'),
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
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
            acks=[user.user_id],
            approved=now(),
            required=[
                {
                    'product_id': components['coffee1'].product_id,
                    'price_type': 'store',
                    'count': 1,
                },
                {
                    'product_id': products['cappuccino'].product_id,
                    'count': 1,
                    'price_type': 'store',
                },
                {
                    'product_id': products['latte'].product_id,
                    'count': 1,
                    'price_type': 'store',
                },
            ],
        )

        await wait_order_status(order, ('processing', 'begin'))

        tap.eq(
            len(order.vars('over_required', [])),
            0,
            'в перерасходе ничего нет',
        )
        tap.eq(
            order.components.total(products['cappuccino'].product_id),
            1,
            '1 капучино',
        )
        tap.eq(
            order.components.total(products['latte'].product_id),
            1,
            '1 латте',
        )

        await stocks['store_coffee1'].reload()
        tap.eq(stocks['store_coffee1'].count, 10, 'кофе1 остаток')
        tap.eq(stocks['store_coffee1'].reserve, 1, 'кофе1 резерв')

        await stocks['comp_coffee1'].reload()
        tap.eq(
            stocks['comp_coffee1'].count,
            1 * components['coffee1'].quants,
            'кофе1 остаток'
        )
        tap.eq(
            stocks['comp_coffee1'].reserve,
            1 * 4 + 1 * 4,
            'кофе1 резерв',
        )

        await stocks['comp_milk1'].reload()
        tap.eq(
            stocks['comp_milk1'].count,
            2 * components['milk1'].quants,
            'молоко1 остаток',
        )
        tap.eq(
            stocks['comp_milk1'].reserve,
            1 * 80 + 1 * 120,
            'молоко1 резерв',
        )

        await stocks['comp_glass1'].reload()
        tap.eq(
            stocks['comp_glass1'].count,
            3 * components['glass1'].quants,
            'стакан1 остаток',
        )
        tap.eq(
            stocks['comp_glass1'].reserve,
            1 + 1,
            'стакан1 резерв',
        )

        order.vars['over_required'] = [
            {
                'product_id': products['cappuccino'].product_id,
                'price_type': 'store',
                'count': 1,
            }
        ]

        tap.ok(await order.save(), 'уронили капучно')

        await wait_order_status(
            order, ('processing', 'waiting'), user_done=user,
        )

        await order.business.order_changed()
        await order.reload()

        tap.eq(len(order.vars('over_required')), 1, 'в перерасходе капучино')
        tap.eq(
            order.components.total(products['cappuccino'].product_id),
            2,
            '2 капучино',
        )
        tap.eq(
            order.components.total(products['latte'].product_id),
            1,
            '1 латте',
        )

        await stocks['comp_coffee1'].reload()
        tap.eq(
            stocks['comp_coffee1'].reserve,
            2 * 4 + 1 * 4,
            'кофе1 резерв увеличился',
        )

        await stocks['comp_milk1'].reload()
        tap.eq(
            stocks['comp_milk1'].reserve,
            2 * 80 + 1 * 120,
            'молоко1 резерв увеличился',
        )

        await stocks['comp_glass1'].reload()
        tap.eq(
            stocks['comp_glass1'].reserve,
            2 + 1,
            'стакан1 резерв увеличился',
        )
