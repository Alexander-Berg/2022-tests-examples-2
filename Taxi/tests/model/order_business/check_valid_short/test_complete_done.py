from datetime import timedelta


async def test_done(tap, dataset):
    with tap.plan(9, 'Начало завершения выполненного заказа'):

        store = await dataset.store()

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='complete',
            estatus='done',
        )
        tap.ok(order, 'Заказ получен')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'done', 'done')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')


async def test_empty_write_off(tap, dataset, now, uuid, wait_order_status):
    with tap.plan(10, 'Нет ни одного просроченного продукта, нет саджестов'):
        product1 = await dataset.product(valid=10)
        product2 = await dataset.product(valid=10)

        store = await dataset.store()
        user = await dataset.user(store=store)

        shelf1 = await dataset.shelf(store=store, type='store', order=1)
        shelf2 = await dataset.shelf(store=store, type='store', order=2)
        await dataset.shelf(store=store, type='trash', order=1)

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf1,
            product=product1,
            count=7,
            valid=now() + timedelta(days=30),
            lot=uuid(),
        )
        tap.ok(stock1,
               f'Остаток на полке 1 не просрочен: {stock1.stock_id}')

        stock2 = await dataset.stock(
            store=store,
            shelf=shelf2,
            product=product2,
            count=28,
            valid=now() + timedelta(days=30),
            lot=uuid(),
        )
        tap.ok(stock2,
               f'Остаток на полке 2 не просрочен: {stock2.stock_id}')

        order = await dataset.order(
            store=store,
            type='check_valid_short',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.ok(
            await order.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        tap.ok(
            await wait_order_status(
                order,
                ('complete', 'done'),
                user_done=user
            ),
            'Выполнили до конца'
        )

        tap.eq(order.problems, [], 'Нет проблем')


async def test_done_box2shelf_off(tap, dataset, now, uuid,
                                  wait_order_status, cfg):
    cfg.set('business.order.check_valid_short.trash_suggests', False)
    with tap.plan(10, 'Не генерируются саджесты на полку trash'):
        product1 = await dataset.product(valid=10)
        product2 = await dataset.product(valid=10)

        store = await dataset.store()
        user = await dataset.user(store=store)

        shelf1 = await dataset.shelf(store=store, type='store', order=1)
        shelf2 = await dataset.shelf(store=store, type='store', order=2)
        await dataset.shelf(store=store, type='trash', order=1)

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf1,
            product=product1,
            count=7,
            valid=now() - timedelta(days=30),
            lot=uuid(),
        )
        tap.ok(stock1,
               f'Остаток на полке 1 просрочен: {stock1.stock_id}')

        stock2 = await dataset.stock(
            store=store,
            shelf=shelf2,
            product=product2,
            count=28,
            valid=now() - timedelta(days=30),
            lot=uuid(),
        )
        tap.ok(stock2,
               f'Остаток на полке 2 просрочен: {stock2.stock_id}')

        order = await dataset.order(
            store=store,
            type='check_valid_short',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'reserving', 'reserving')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.ok(
            await order.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        tap.ok(
            await wait_order_status(
                order,
                ('complete', 'done'),
                user_done=user
            ),
            'Выполнили до конца'
        )

        tap.eq(order.problems, [], 'Нет проблем')
    cfg.set('business.order.check_valid_short.trash_suggests', True)
