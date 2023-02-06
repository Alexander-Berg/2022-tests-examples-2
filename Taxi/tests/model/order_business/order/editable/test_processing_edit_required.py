import pytest

from stall.model.suggest import Suggest


@pytest.mark.parametrize('done', [True, False])
async def test_add_some(tap, dataset, wait_order_status, now, done):
    with tap.plan(9, 'увеличиваем количество порций по кухне'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, _, components, products = await dataset.coffee(
            shelves_meta=(
                ('store', 'store'),
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
            ),
            stocks_meta=(
                ('store', 'coffee1', 10),
                ('comp', 'coffee1', 10),
                ('comp', 'milk1', 10),
                ('comp', 'glass1', 10),
            ),
            store=store,
        )

        required_v1 = [
            {
                'product_id': components['coffee1'].product_id,
                'count': 1,
            },
            {
                'product_id': products['latte'].product_id,
                'count': 1,
            },
        ]

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            acks=[user.user_id],
            approved=now(),
            required=required_v1,
            vars={'editable': True},
        )

        await wait_order_status(order, ('processing', 'waiting'))

        await order.business.order_changed()
        await order.reload()

        tap.eq(order.vars('total_order_weight', 0), 537, 'Вес исходный')
        tap.eq(order.required, required_v1, 'требования в порядке')

        suggests = await Suggest.list_by_order(order, tags=['kitchen'])
        tap.eq(len(suggests), 1, 'есть один саджест по кухне')
        tap.eq(suggests[0].status, 'request', 'саджест не исполнен')

        if done:
            await suggests[0].done(user=user)

        required_v2 = [
            {
                'product_id': components['coffee1'].product_id,
                'count': 2,
            },
            {
                'product_id': products['latte'].product_id,
                'count': 2,
            },
        ]

        order.vars['required'] = required_v2
        tap.ok(await order.save(), 'отредактировали заказ')

        await wait_order_status(order, ('processing', 'waiting'))

        await order.business.order_changed()
        await order.reload()

        tap.eq(order.vars('total_order_weight', 0), 1074, 'Вес обновленный')
        tap.eq(order.required, required_v2, 'требования изменились')


@pytest.mark.parametrize('done', [True, False])
async def test_add_new(tap, dataset, wait_order_status, now, done):
    with tap.plan(9, 'добавляем новую позицию по кухне'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, _, components, products = await dataset.coffee(
            shelves_meta=(
                ('store', 'store'),
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
            ),
            stocks_meta=(
                ('store', 'coffee1', 10),
                ('comp', 'coffee1', 10),
                ('comp', 'milk1', 10),
                ('comp', 'glass1', 10),
            ),
            store=store,
        )

        required_v1 = [
            {
                'product_id': components['coffee1'].product_id,
                'count': 1,
            },
            {
                'product_id': products['latte'].product_id,
                'count': 1,
            },
        ]

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            acks=[user.user_id],
            approved=now(),
            required=required_v1,
            vars={'editable': True},
        )

        await wait_order_status(order, ('processing', 'waiting'))

        await order.business.order_changed()
        await order.reload()

        tap.eq(order.vars('total_order_weight', 0), 537, 'Вес базовый')
        tap.eq(order.required, required_v1, 'требования в порядке')

        suggests = await Suggest.list_by_order(order, tags=['kitchen'])
        tap.eq(len(suggests), 1, 'есть один саджест по кухне')
        tap.eq(suggests[0].status, 'request', 'саджест не исполнен')

        if done:
            await suggests[0].done(user=user)

        required_v2 = [
            {
                'product_id': components['coffee1'].product_id,
                'count': 2,
            },
            {
                'product_id': products['latte'].product_id,
                'count': 2,
            },
            {
                'product_id': products['cappuccino'].product_id,
                'count': 2,
            },
        ]

        order.vars['required'] = required_v2
        tap.ok(await order.save(), 'отредактировали заказ')

        await wait_order_status(order, ('processing', 'waiting'))

        await order.business.order_changed()
        await order.reload()

        tap.eq(order.vars('total_order_weight', 0), 1298, 'Вес обновленный')
        tap.eq(order.required, required_v2, 'требования изменились')


# pylint: disable=too-many-locals
@pytest.mark.parametrize('done', [True, False])
async def test_rm_some(tap, dataset, wait_order_status, now, done):
    with tap.plan(9, 'убавляем количество порций по кухне'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, _, components, products = await dataset.coffee(
            shelves_meta=(
                ('store', 'store'),
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
            ),
            stocks_meta=(
                ('store', 'coffee1', 10),
                ('comp', 'coffee1', 10),
                ('comp', 'milk1', 10),
                ('comp', 'glass1', 10),
            ),
            store=store,
        )

        required_v1 = [
            {
                'product_id': components['coffee1'].product_id,
                'count': 2,
            },
            {
                'product_id': products['latte'].product_id,
                'count': 2,
            },
            {
                'product_id': products['cappuccino'].product_id,
                'count': 2,
            },
        ]

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            acks=[user.user_id],
            approved=now(),
            required=required_v1,
            vars={'editable': True},
        )

        await wait_order_status(order, ('processing', 'waiting'))

        await order.business.order_changed()
        await order.reload()

        tap.eq(order.required, required_v1, 'требования в порядке')

        suggests = {
            s.product_id: s
            for s in await Suggest.list_by_order(order, tags=['kitchen'])
        }
        tap.eq(len(suggests), 2, 'есть  саджесты по кухне')
        tap.eq(
            suggests[products['latte'].product_id].status,
            'request',
            'саджест по латте не исполнен',
        )

        if done:
            await suggests[products['latte'].product_id].done(user=user)

        required_v2 = [
            {
                'product_id': components['coffee1'].product_id,
                'count': 1,
            },
            {
                'product_id': products['latte'].product_id,
                'count': 1,
            },
            {
                'product_id': products['cappuccino'].product_id,
                'count': 1,
            },
        ]

        order.vars['required'] = required_v2
        tap.ok(await order.save(), 'отредактировали заказ')

        await wait_order_status(order, ('processing', 'waiting'))

        await order.business.order_changed()
        await order.reload()

        required = {r.product_id: r for r in order.required}

        if done:
            tap.eq(
                required[components['coffee1'].product_id].count,
                1,
                'обычный товар отредактирован',
            )
            tap.eq(
                required[products['latte'].product_id].count,
                2,
                'латте не отредактирован',
            )
            tap.eq(
                required[products['cappuccino'].product_id].count,
                1,
                'капучино отредактирован',
            )
        else:
            tap.eq(
                required[components['coffee1'].product_id].count,
                1,
                'обычный отредактирован',
            )
            tap.eq(
                required[products['latte'].product_id].count,
                1,
                'латте отредактирован',
            )
            tap.eq(
                required[products['cappuccino'].product_id].count,
                1,
                'капучино отредактирован',
            )


# pylint: disable=too-many-locals
@pytest.mark.parametrize('done', [True, False])
async def test_rm_full(tap, dataset, wait_order_status, now, done):
    with tap.plan(9, 'полностью удаляем позиции по кухне'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, _, components, products = await dataset.coffee(
            shelves_meta=(
                ('store', 'store'),
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
            ),
            stocks_meta=(
                ('store', 'coffee1', 10),
                ('comp', 'coffee1', 10),
                ('comp', 'milk1', 10),
                ('comp', 'glass1', 10),
            ),
            store=store,
        )

        required_v1 = [
            {
                'product_id': components['coffee1'].product_id,
                'count': 2,
            },
            {
                'product_id': products['latte'].product_id,
                'count': 2,
            },
            {
                'product_id': products['cappuccino'].product_id,
                'count': 2,
            },
        ]

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            acks=[user.user_id],
            approved=now(),
            required=required_v1,
            vars={'editable': True},
        )

        await wait_order_status(order, ('processing', 'waiting'))

        await order.business.order_changed()
        await order.reload()

        tap.eq(order.required, required_v1, 'требования в порядке')

        suggests = {
            s.product_id: s
            for s in await Suggest.list_by_order(order, tags=['kitchen'])
        }
        tap.eq(len(suggests), 2, 'есть  саджесты по кухне')
        tap.eq(
            suggests[products['latte'].product_id].status,
            'request',
            'саджест по латте не исполнен',
        )

        if done:
            await suggests[products['latte'].product_id].done(user=user)

        required_v2 = [
            {
                'product_id': components['coffee1'].product_id,
                'count': 1,
            },
        ]

        order.vars['required'] = required_v2
        tap.ok(await order.save(), 'отредактировали заказ')

        await wait_order_status(order, ('processing', 'waiting'))

        await order.business.order_changed()
        await order.reload()

        required = {r.product_id: r for r in order.required}

        if done:
            tap.eq(
                required[components['coffee1'].product_id].count,
                1,
                'обычный товар отредактирован',
            )
            tap.eq(
                required[products['latte'].product_id].count,
                2,
                'латте не отредактирован',
            )
            tap.ok(
                products['cappuccino'].product_id not in required,
                'капучино полностью убран',
            )
        else:
            tap.eq(
                required[components['coffee1'].product_id].count,
                1,
                'обычный отредактирован',
            )
            tap.ok(
                products['latte'].product_id not in required,
                'латте полностью убран',
            )
            tap.ok(
                products['cappuccino'].product_id not in required,
                'капучино полностью убран',
            )
