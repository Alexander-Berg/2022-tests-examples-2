# pylint: disable=too-many-locals,too-many-statements,expression-not-assigned

from stall.model.suggest import Suggest


async def test_prepare_lost(tap, dataset, wait_order_status, now):
    with tap.plan(
            14,
            'товары испорченные в при сборки перекладываем в over_required',
    ):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, _, components, products = await dataset.coffee(
            shelves_meta=(
                ('store', 'store'),
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
            ),
            stocks_meta=(
                ('store', 'coffee1', 1),
                ('store', 'coffee2', 1),
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
                    'count': 1,
                },
                {
                    'product_id': products['cappuccino'].product_id,
                    'count': 1,
                },
                {
                    'product_id': components['coffee2'].product_id,
                    'count': 1,
                },
                {
                    'product_id': products['lungo'].product_id,
                    'count': 1,
                },
            ],
            vars={'editable': True},
        )

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()

        suggests = {
            s.product_id: s
            for s in await Suggest.list_by_order(
                order,
                status='request',
                types='shelf2box',
            )
        }

        tap.eq(len(suggests), 4, '4 саджеста на сборку')
        with tap.raises(
                Suggest.ErSuggestErrorDenided,
                'саджесты по обычным товарам в еррор закрывать нельзя',
        ):
            await suggests[components['coffee1'].product_id].done(
                'error', reason={'count': 1},
            )
        tap.ok(
            await suggests[components['coffee1'].product_id].done(
                'done', user=user,
            ),
            'закрыли саджест с обычным товаром',
        )
        tap.ok(
            await suggests[products['cappuccino'].product_id].done(
                'error', reason={'count': 1},
            ),
            'испортили 1 порцию кофе',
        )
        tap.ok(
            await suggests[components['coffee2'].product_id].done(
                'done', user=user,
            ),
            'положили в корзинку 1 обычный товар',
        )
        tap.ok(
            await suggests[products['lungo'].product_id].done(
                'done', user=user,
            ),
            'положили в корзинку 1 кофе',
        )

        await wait_order_status(order, ('processing', 'drop_errors'))

        await order.business.order_changed()
        await order.reload()

        over_required = {
            r['product_id']: r['count']
            for r in order.vars('over_required')
        }

        tap.eq(
            len(over_required), 1, '1 товар испортили и положили в оувер',
        )
        tap.eq(
            over_required[products['cappuccino'].product_id],
            1,
            '1 кофе',
        )

        suggests = await Suggest.list_by_order(order)

        tap.eq(len(suggests), 3, '3 саджеста осталось')
        tap.eq(suggests[0].status, 'done', 'первый исполнен')
        tap.eq(suggests[1].status, 'done', 'второй исполнен')
        tap.eq(suggests[2].status, 'done', 'второй исполнен')


async def test_prepare_lost_with_problems(
        tap, dataset, wait_order_status, now,
):
    with tap.plan(12, 'испрортили последние стаканчики для кофе'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, stocks, _, products = await dataset.coffee(
            shelves_meta=(
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
            ),
            stocks_meta=(
                ('comp', 'coffee1', 1),
                ('comp', 'milk1', 1),
                ('comp', 'glass1', 2),
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
                    'count': 2,
                },
            ],
            vars={'editable': True},
        )

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()

        suggests = {
            s.product_id: s
            for s in await Suggest.list_by_order(
                order,
                status='request',
                types='shelf2box',
            )
        }

        tap.eq(len(suggests), 1, '1 саджест на сборку')
        tap.ok(
            await suggests[products['cappuccino'].product_id].done(
                'error', reason={'count': 2},
            ),
            'сломали 2 кофе',
        )

        await wait_order_status(order, ('processing', 'drop_errors'))

        await order.business.order_changed()
        await order.reload()

        tap.eq(
            len(order.vars('over_required')), 1, 'кофе положили в оувер',
        )
        tap.eq(
            order.vars('over_required')[0]['count'],
            2,
            '2 порции кофе',
        )

        await wait_order_status(order, ('processing', 'suggests_complete'))

        await order.business.order_changed()
        await order.reload()

        tap.ok(
            order.problems,
            'было 2 стаканчика, 2 испортили, нужно править заказ',
        )
        tap.eq(order.problems[0].type, 'low', 'не хватает')
        tap.eq(order.problems[0].count, 0, '0 порций кофе')

        await stocks['comp_glass1'].reload()

        tap.eq(stocks['comp_glass1'].count, 2, 'количество стаканчиков')
        tap.eq(stocks['comp_glass1'].reserve, 2, 'резерв на стаканчики')
