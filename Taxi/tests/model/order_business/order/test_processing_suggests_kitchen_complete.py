from stall.model.suggest import Suggest


async def test_status(tap, dataset, wait_order_status, now):
    with tap.plan(4, 'переход в саб-статус генерации саджестов для кухни'):
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

        await wait_order_status(
            order, ('processing', 'suggests_kitchen_complete'),
        )

        await order.business.order_changed()
        await order.reload()

        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'print_kitchen', 'print_kitchen')
        tap.eq(order.target, 'complete', 'target: complete')


async def test_add_some(tap, dataset, wait_order_status, now):
    with tap.plan(9, 'добавление саджестов при добавлении порций'):
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

        suggests = await Suggest.list_by_order(order, tags=['kitchen'])
        tap.eq(len(suggests), 1, 'есть один саджест по кухне')

        tap.eq(suggests[0].status, 'request', 'саджест не исполнен')
        tap.ok(await suggests[0].done(user=user), 'исполняем')

        required_v2 = [
            {
                'product_id': components['coffee1'].product_id,
                'count': 2,
            },
            {
                'product_id': products['latte'].product_id,
                'count': 3,
            },
        ]

        order.vars['required'] = required_v2
        tap.ok(await order.save(), 'отредактировали заказ')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order, tags=['kitchen'])
        tap.eq(len(suggests), 2, 'саджестов по кухне прибавилось')

        suggests = {s.status: s for s in suggests}

        tap.eq(suggests['done'].result_count, 1, 'с количеством один')

        tap.eq(suggests['request'].count, 3 - 1, 'с количеством два')


async def test_rm_some(tap, dataset, wait_order_status, now):
    with tap.plan(9, 'количество саджестов не изменилось, но count другой'):
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

        suggests = await Suggest.list_by_order(order, tags=['kitchen'])
        tap.eq(len(suggests), 1, 'есть один саджест по кухне')

        tap.eq(suggests[0].status, 'request', 'саджест не исполнен')
        tap.eq(suggests[0].count, 2, 'корректное количество')

        required_v2 = [
            {
                'product_id': components['coffee1'].product_id,
                'count': 2,
            },
            {
                'product_id': products['latte'].product_id,
                'count': 1,
            },
        ]

        order.vars['required'] = required_v2
        tap.ok(await order.save(), 'отредактировали заказ')

        await wait_order_status(order, ('processing', 'waiting'))

        await order.business.order_changed()
        await order.reload()

        suggests = await Suggest.list_by_order(order, tags=['kitchen'])
        tap.eq(len(suggests), 1, 'саджестов по кухне не прибавилось')

        tap.eq(suggests[0].status, 'request', 'саджест не исполнен')
        tap.eq(suggests[0].count, 1, 'количество уменьшилось')


async def test_add_rm(tap, dataset, wait_order_status, now):
    with tap.plan(10, 'редактируем кухню по всякому'):
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

        suggests = await Suggest.list_by_order(order, tags=['kitchen'])
        tap.eq(len(suggests), 2, 'два саджеста по кухне')

        tap.ok(await suggests[0].done(user=user), 'исполняем первый')
        tap.ok(await suggests[1].done(user=user), 'исполняем второй')

        required_v2 = [
            {
                'product_id': components['coffee1'].product_id,
                'count': 2,
            },
            {
                'product_id': products['cappuccino'].product_id,
                'count': 3,
            },
        ]

        order.vars['required'] = required_v2
        tap.ok(await order.save(), 'отредактировали заказ')

        await wait_order_status(order, ('processing', 'waiting'))

        await order.business.order_changed()
        await order.reload()

        suggests = {
            (s.product_id, s.status): s
            for s in await Suggest.list_by_order(order, tags=['kitchen'])
        }
        tap.eq(len(suggests), 3, 'саджестов по кухне прибавилось')

        tap.eq(
            suggests[(products['latte'].product_id, 'done')].result_count,
            2,
            'есть старый саджест по латте',
        )

        tap.eq(
            suggests[(products['cappuccino'].product_id, 'done')].result_count,
            2,
            'есть старый саджест по капучино',
        )

        tap.eq(
            suggests[(products['cappuccino'].product_id, 'request')].count,
            1,
            'есть новый незакрытый саджест на капучино',
        )


async def test_after_prepare_lost(tap, dataset, wait_order_status, now):
    with tap.plan(10, 'корректное количество в саджестах при порче кофе'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        _, _, _, products = await dataset.coffee(
            shelves_meta=(
                ('comp', 'kitchen_components'),
                ('on_demand', 'kitchen_on_demand'),
            ),
            stocks_meta=(
                ('comp', 'coffee1', 10),
                ('comp', 'milk1', 10),
                ('comp', 'glass1', 10),
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
                    'product_id': products['latte'].product_id,
                    'count': 1,
                },
            ],
            vars={'editable': True},
        )

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()

        suggests = await Suggest.list_by_order(order, tags=['kitchen'])

        tap.eq(len(suggests), 1, '1 саджест по кухне')
        tap.ok(
            await suggests[0].done('error', reason={'count': 1}),
            'разлили 1 кофе',
        )

        await wait_order_status(order, ('processing', 'waiting'))

        await order.reload()

        over_required = {
            r['product_id']: r['count']
            for r in order.vars('over_required')
        }

        tap.eq(
            len(over_required), 1, 'кофе положули в оувер',
        )
        tap.eq(
            over_required[products['latte'].product_id],
            1,
            '1 порция',
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
        tap.eq(
            suggests[products['latte'].product_id].type,
            'shelf2box',
            'положи в корзину',
        )
        tap.eq(
            suggests[products['latte'].product_id].count,
            1,
            '1 латте',
        )


async def test_rm_kitchen(tap, dataset, wait_order_status, now):
    with tap.plan(8, 'полностью удаляем кухню из заказа 1 -> 0'):
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

        suggests = {
            s.product_id: s
            for s in await Suggest.list_by_order(order)
        }
        tap.eq(len(suggests), 2, '2 саджеста всего')
        tap.ok(
            components['coffee1'].product_id in suggests,
            'саджест на обычный товар',
        )
        tap.ok(
            products['latte'].product_id in suggests,
            'саджест на кухню товар',
        )

        required_v2 = [
            {
                'product_id': components['coffee1'].product_id,
                'count': 2,
            },
        ]

        order.vars['required'] = required_v2
        tap.ok(await order.save(), 'отредактировали заказ')

        await wait_order_status(order, ('processing', 'waiting'))

        await order.business.order_changed()
        await order.reload()

        suggests = {
            s.product_id: s
            for s in await Suggest.list_by_order(order)
        }
        tap.eq(len(suggests), 1, 'всего 1 саджест')
        tap.ok(
            components['coffee1'].product_id in suggests,
            'только 1 саджест на обычный товар',
        )
