from stall.model.suggest import Suggest

async def test_done(tap, dataset):
    with tap.plan(8, 'Заказ обработан'):

        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='failed',
            estatus='done',
            target='failed',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'failed', 'target: failed')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'failed', 'target: failed')


async def test_defibrillation(tap, uuid, dataset, wait_order_status):
    with tap.plan(29, 'Реанимирование заказа'):

        product1 = await dataset.product(valid=10)
        product2 = await dataset.product(valid=10)

        store = await dataset.full_store()

        user = await dataset.user(store=store)

        shelf1 = await dataset.shelf(store=store, type='store', order=1)
        shelf2 = await dataset.shelf(store=store, type='store', order=2)

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='failed',
            estatus='unreserve',
            target='failed',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'unreserve', 'unreserve')
        tap.eq(order.target, 'failed', 'target: failed')

        stock1 = await dataset.stock(
            store=store,
            order=order,
            shelf=shelf1,
            product=product1,
            count=7,
            reserve=7,
            valid='2020-01-01',
            lot=uuid(),
        )

        stock2 = await dataset.stock(
            store=store,
            order=order,
            shelf=shelf1,
            product=product1,
            count=3,
            reserve=3,
            valid='2020-01-01',
            lot=uuid(),
        )

        stock3 = await dataset.stock(
            store=store,
            order=order,
            shelf=shelf2,
            product=product2,
            count=20,
            reserve=20,
            valid='2020-01-01',
            lot=uuid(),
        )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'failed', 'failed')
        tap.eq(order.estatus, 'suggests_drop', 'suggests_drop')
        tap.eq(order.target, 'failed', 'target: failed')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        tap.ok(await stock1.reload(), 'Остаток 1 получен')
        tap.eq(stock1.count, 7, 'Остаток 1 есть')
        tap.eq(stock1.reserve, 0, 'Зарезервировано 1')

        tap.ok(await stock2.reload(), 'Остаток 2 получен')
        tap.eq(stock2.count, 3, 'Остаток 2 есть')
        tap.eq(stock2.reserve, 0, 'Зарезервировано 2')

        tap.ok(await stock3.reload(), 'Остаток 3 получен')
        tap.eq(stock3.count, 20, 'Остаток 3 есть')
        tap.eq(stock3.reserve, 0, 'Зарезервировано 3')

        await wait_order_status(
            order,
            ('failed', 'done'),
        )

        tap.ok(await order.signal({'type': 'order_defibrillation'}),
               'сигнал отправлен')

        await order.business.order_changed()
        await order.reload()
        tap.eq(order.status, 'reserving', 'status reserving')
        tap.eq(order.estatus, 'begin', 'estatus begin')

        await wait_order_status(
            order,
            ('request', 'begin'),
        )

        tap.ok(await order.ack(user), 'ack')
        tap.in_ok(user.user_id, order.acks, 'попал в acks')

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )
        await order.reload()
        tap.eq(order.status, 'processing', 'status processing')
        tap.eq(order.estatus, 'waiting', 'estatus waiting')

        suggests = await Suggest.list_by_order(
            order,
            status='request',
        )

        tap.ne(len(suggests), 0, 'Есть саджесты взятия просрочки')
