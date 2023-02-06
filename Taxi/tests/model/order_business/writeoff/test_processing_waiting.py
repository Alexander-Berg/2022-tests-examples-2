async def test_waiting(tap, dataset):
    with tap.plan(10, 'Ожидание выполнения'):

        product = await dataset.product(valid=10)
        store   = await dataset.store()
        trash   = await dataset.shelf(store=store, type='trash')

        order = await dataset.order(
            store=store,
            type = 'writeoff',
            status='processing',
            estatus='waiting',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        suggest1 = await dataset.suggest(
            order,
            type='check',
            shelf_id=trash.shelf_id,
            product_id=product.product_id,
            count=10,
        )
        tap.ok(suggest1, 'Саджест 1')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')


async def test_waiting_done(tap, dataset):
    with tap.plan(11, 'Саджесты проверки выполнены'):

        product = await dataset.product(valid=10)
        store   = await dataset.store()
        trash   = await dataset.shelf(store=store, type='trash')
        user    = await dataset.user(store=store)

        order = await dataset.order(
            store=store,
            type = 'writeoff',
            status='processing',
            estatus='waiting',
            user_done=user.user_id,
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        suggest1 = await dataset.suggest(
            order,
            type='check',
            shelf_id=trash.shelf_id,
            product_id=product.product_id,
            count=10,
        )
        tap.ok(suggest1, 'Саджест 1')
        tap.ok(
            await suggest1.done(status='done'),
            'Закрыли саджест'
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

