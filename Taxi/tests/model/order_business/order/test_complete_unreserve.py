from libstall.util import now


async def test_unreserve(tap, dataset, wait_order_status):
    with tap.plan(32, 'Резервирование товара'):

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        store = await dataset.store()
        user  = await dataset.user(store=store)

        stock1 = await dataset.stock(product=product1, store=store, count=10)
        tap.eq(stock1.count, 10, 'Остаток 1 положен')
        tap.eq(stock1.reserve, 0, 'Резерва 1 нет')

        stock2 = await dataset.stock(product=product2, store=store, count=20)
        tap.eq(stock2.count, 20, 'Остаток 2 положен')
        tap.eq(stock2.reserve, 0, 'Резерва 2 нет')

        stock3 = await dataset.stock(product=product3, store=store, count=30)
        tap.eq(stock3.count, 30, 'Остаток 3 положен')
        tap.eq(stock3.reserve, 0, 'Резерва 3 нет')

        order = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            required = [
                {
                    'product_id': product1.product_id,
                    'count': 1
                },
                {
                    'product_id': product3.product_id,
                    'count': 3
                },
                {
                    'product_id': product2.product_id,
                    'count': 2
                },
            ],
        )
        tap.ok(order, 'Заказ создан')

        tap.ok(await wait_order_status(
            order,
            ('complete', 'unreserve'),
            user_done=user,
        ), 'Прошли до статуса')

        tap.ok(await order.reload(), 'Заказ получен')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'unreserve', 'unreserve')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

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

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'update_required', 'update_required')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        with await stock1.reload() as stock:
            tap.eq(stock.count, 9, 'Остаток есть')
            tap.eq(stock.reserve, 0, 'Не зарезервировано')

        with await stock2.reload() as stock:
            tap.eq(stock.count, 18, 'Остаток есть')
            tap.eq(stock.reserve, 0, 'Не зарезервировано')

        with await stock3.reload() as stock:
            tap.eq(stock.count, 27, 'Остаток есть')
            tap.eq(stock.reserve, 0, 'Не зарезервировано')


async def test_unreserve_lots(tap, dataset, uuid, wait_order_status):
    with tap.plan(32, 'Резервирование товара'):

        product = await dataset.product()

        store   = await dataset.store()
        user    = await dataset.user(store=store)
        shelf1  = await dataset.shelf(store=store, order=1)
        shelf2  = await dataset.shelf(store=store, order=2)

        stock1 = await dataset.stock(
            product=product,
            shelf=shelf1,
            count=10,
            lot=uuid(),
        )
        tap.eq(stock1.count, 10, 'Остаток 1 положен')
        tap.eq(stock1.reserve, 0, 'Резерва 1 нет')

        stock2 = await dataset.stock(
            product=product,
            shelf=shelf1,
            count=20,
            lot=uuid(),
        )
        tap.eq(stock2.count, 20, 'Остаток 2 положен')
        tap.eq(stock2.reserve, 0, 'Резерва 2 нет')

        stock3 = await dataset.stock(
            product=product,
            shelf=shelf2,
            count=30,
            lot=uuid(),
        )
        tap.eq(stock3.count, 30, 'Остаток 3 положен')
        tap.eq(stock3.reserve, 0, 'Резерва 3 нет')

        order = await dataset.order(
            store=store,
            type = 'order',
            status='reserving',
            estatus='begin',
            approved=now(),
            acks=[user.user_id],
            required = [
                {
                    'product_id': product.product_id,
                    'count': 45
                },
            ],
        )
        tap.ok(order, 'Заказ создан')

        tap.ok(await wait_order_status(
            order,
            ('complete', 'unreserve'),
            user_done=user,
        ), 'Прошли до статуса')

        tap.ok(await order.reload(), 'Заказ получен')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'unreserve', 'unreserve')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

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

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'update_required', 'update_required')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        with await stock1.reload() as stock:
            tap.eq(stock.count, 0, 'Остаток взят')
            tap.eq(stock.reserve, 0, 'Не зарезервировано')

        with await stock2.reload() as stock:
            tap.eq(stock.count, 0, 'Остаток взят')
            tap.eq(stock.reserve, 0, 'Не зарезервировано')

        with await stock3.reload() as stock:
            tap.eq(stock.count, 15, 'Остаток взят')
            tap.eq(stock.reserve, 0, 'Не зарезервировано')
