from stall.model.order import Order
from stall.model.suggest import Suggest


# pylint: disable=too-many-locals
async def test_complete_cpos(tap, dataset, wait_order_status, now, api):
    with tap.plan(12, 'Создание ордера check_product_on_shelf'):
        product1 = await dataset.product()
        product2 = await dataset.product()

        store = await dataset.store()
        user = await dataset.user(store=store)

        stock1 = await dataset.stock(product=product1, store=store,
                                     count=10)
        stock2 = await dataset.stock(product=product2, store=store,
                                     count=12)

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            total_price='1230.00',
            approved=now(),
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 6,
                },
                {
                    'product_id': product2.product_id,
                    'count': 7,
                },
            ],

        )

        await wait_order_status(
            order,
            ('processing', 'begin'),
            user_done=user,
        )

        suggests = await Suggest.list_by_order(order)
        tap.eq_ok(len(suggests), 2, '2 suggests')

        t = await api(user=user)

        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'shortfall',
                            'data': {'suggest_id': suggests[0].suggest_id},
                        })
        t.status_is(200, diag=True)
        await t.post_ok('api_tsd_order_signal',
                        desc='POST send the same signal one more time',
                        json={
                            'order_id': order.order_id,
                            'signal': 'shortfall',
                            'data': {'suggest_id': suggests[0].suggest_id},
                        })
        t.status_is(200, diag=True)
        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'shortfall',
                            'data': {'suggest_id': suggests[1].suggest_id},
                        })
        t.status_is(200, diag=True)

        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user,
        )

        cpos_orders = await Order.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('type', 'check_product_on_shelf'),
            ],
            sort=(),
        )
        cpos_orders = cpos_orders.list
        tap.eq_ok(len(cpos_orders), 2,
                  'Order check_product_on_shelf created')
        tap.eq_ok(
            sorted([
                (cpos.required[0].product_id, cpos.required[0].shelf_id)
                for cpos in cpos_orders
            ]),
            sorted([
                (stock1.product_id, stock1.shelf_id),
                (stock2.product_id, stock2.shelf_id),
            ]),
            'Correct products and shelves'
        )
        with tap.subtest(None, 'Проверяем созданные ордера') as taps:
            for cpos in cpos_orders:
                taps.eq_ok(cpos.parent, [order.order_id], 'correct parent')
                taps.ok(cpos.vars.get('reserve'), 'reserve flag is set')


async def test_product_removed(tap, dataset, wait_order_status, now, api):
    with tap.plan(10, 'Создание ордера check_product_on_shelf, '
                      'когда из ордера удален товар'):
        product1 = await dataset.product()
        product2 = await dataset.product()

        store = await dataset.store()
        user = await dataset.user(store=store)

        await dataset.stock(product=product1, store=store,
                            count=10)
        await dataset.stock(product=product2, store=store,
                            count=12)

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            total_price='1230.00',
            approved=now(),
            required=[
                {
                    'product_id': product1.product_id,
                    'count': 6,
                },
                {
                    'product_id': product2.product_id,
                    'count': 7,
                },
            ],

        )

        await wait_order_status(
            order,
            ('processing', 'begin'),
            user_done=user,
        )

        suggests = await Suggest.list_by_order(order)
        tap.eq_ok(len(suggests), 2, '2 suggests')

        t = await api(user=user)

        await t.post_ok('api_tsd_order_signal',
                        json={
                            'order_id': order.order_id,
                            'signal': 'shortfall',
                            'data': {'suggest_id': suggests[0].suggest_id},
                        })
        t.status_is(200, diag=True)

        tap.ok(await suggests[0].rm(), 'удаляем саджест')

        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user,
        )

        cpos_order = await Order.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('type', 'check_product_on_shelf'),
            ],
            sort=(),
        )
        tap.eq_ok(len(cpos_order.list), 1,
                  'Order check_product_on_shelf created')
        cpos_order = cpos_order.list[0]
        tap.eq_ok(
            {
                (r.product_id, r.shelf_id) for r in cpos_order.required
            },
            {
                (suggests[0].product_id, suggests[0].shelf_id),
            },
            'Correct products and shelves'
        )
        tap.eq_ok(cpos_order.parent, [order.order_id], 'correct parent')
        tap.ok(cpos_order.vars.get('reserve'), 'reserve flag is set')
