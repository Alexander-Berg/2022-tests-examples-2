from stall.model.order import Order
from libstall.util import now


async def test_visual_control_generate(tap, dataset, wait_order_status):
    with tap.plan(16, 'создение vc'):

        product = await dataset.product(
            vars={
                'imported': {
                    'leftover_for_visual_control': 10,
                }
            }
        )

        store = await dataset.store(options={'exp_humpty_dumpty': True})
        user = await dataset.user(store=store)

        stock1 = await dataset.stock(product=product, store=store, count=5)
        tap.eq(stock1.count, 5, 'Остаток 1 положен')
        tap.eq(stock1.reserve, 0, 'Резерва 1 нет')

        stock2 = await dataset.stock(product=product, store=store, count=10)
        tap.eq(stock2.count, 10, 'Остаток 2 положен')
        tap.eq(stock2.reserve, 0, 'Резерва 2 нет')

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            required=[
                {
                    'product_id': product.product_id,
                    'count': 6
                },
            ],
        )

        tap.ok(order, 'Заказ создан')

        tap.ok(await wait_order_status(
            order,
            ('complete', 'visual_control_generate'),
            user_done=user,
        ), 'Прошли до статуса')

        tap.ok(await order.reload(), 'Заказ получен')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'visual_control_generate',
               'visual_control_generate')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Заказ получен')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'check_product_on_shelf_generate',
               'check_product_on_shelf_generate')
        tap.eq(order.target, 'complete', 'target: complete')

        order_vc = await Order.list(
            by='look',
            # INDEX: orders_history_type_idx
            conditions=[
                ('type', 'visual_control'),
                ('store_id', store.store_id),
            ],
        )

        tap.eq(len(order_vc.list), 1, 'vc создан')


async def test_parcel(tap, dataset, wait_order_status):
    with tap.plan(13, 'Проверка заказа с одной посылкой'):

        store = await dataset.store(options={'exp_humpty_dumpty': True})
        item = await dataset.item(store=store)
        user = await dataset.user(store=store)

        stock3 = await dataset.stock(item=item, store=store, count=1)
        tap.eq(stock3.count, 1, 'Остаток 3 положен')
        tap.eq(stock3.reserve, 0, 'Резерва 3 нет')

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            required=[
                {
                    'item_id': item.item_id,
                    'count': 1,
                },
            ],
        )

        tap.ok(order, 'Заказ создан')

        tap.ok(await wait_order_status(
            order,
            ('complete', 'visual_control_generate'),
            user_done=user,
        ), 'Прошли до статуса')

        tap.ok(await order.reload(), 'Заказ получен')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'visual_control_generate',
               'visual_control_generate')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Заказ получен')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'check_product_on_shelf_generate',
               'check_product_on_shelf_generate')
        tap.eq(order.target, 'complete', 'target: complete')


async def test_zero_stocks(tap, dataset, wait_order_status):
    with tap.plan(14, 'Отсутствие vc при нулевом остатке после заказа'):
        product = await dataset.product(
            vars={
                'imported': {
                    'leftover_for_visual_control': 10,
                }
            }
        )

        store = await dataset.store(options={'exp_humpty_dumpty': True})
        user = await dataset.user(store=store)

        stock1 = await dataset.stock(product=product, store=store, count=15)
        tap.eq(stock1.count, 15, 'Остаток 1 положен')
        tap.eq(stock1.reserve, 0, 'Резерва 1 нет')

        order = await dataset.order(
            store=store,
            type='order',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            required=[
                {
                    'product_id': product.product_id,
                    'count': 15
                },
            ],
        )

        tap.ok(order, 'Заказ создан')

        tap.ok(await wait_order_status(
            order,
            ('complete', 'visual_control_generate'),
            user_done=user,
        ), 'Прошли до статуса')

        tap.ok(await order.reload(), 'Заказ получен')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'visual_control_generate',
               'visual_control_generate')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Заказ получен')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'check_product_on_shelf_generate',
               'check_product_on_shelf_generate')
        tap.eq(order.target, 'complete', 'target: complete')

        order_vc = await Order.list(
            by='look',
            # INDEX: orders_history_type_idx
            conditions=[
                ('type', 'visual_control'),
                ('store_id', store.store_id),
            ],
        )

        tap.eq(len(order_vc.list), 0, 'vc не создался так как остатка нет')
