# pylint: disable=too-many-locals,too-many-statements,unused-variable


async def test_early(tap, now, wait_order_status, uuid, dataset):
    with tap.plan(8, 'Отмена сразу после взятия: убирает все саджесты'):
        product = await dataset.product(valid=10)
        store   = await dataset.store()
        user    = await dataset.user(store=store)
        shelf  = await dataset.shelf(store=store, type='store', order=1)
        trash   = await dataset.shelf(store=store, type='trash')

        await dataset.stock(
            product=product,
            store=store,
            shelf=shelf,
            count=100,
            valid='2020-01-01',
            lot=uuid(),
        )

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
        )

        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(await order.cancel(), 'Пришла отмена')
        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'suggests_error', 'suggests_error')
        tap.eq(order.target, 'canceled', 'target: canceled')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 0, 'Саджестов нет')


async def test_shelf2box(tap, now, wait_order_status, uuid, dataset):
    with tap.plan(21, 'Откат саджестов при взятии просрочки с полки'):
        product1 = await dataset.product(valid=10)
        product2 = await dataset.product(valid=10)

        store   = await dataset.store()
        user    = await dataset.user(store=store)

        shelf1  = await dataset.shelf(store=store, type='store', order=1)
        shelf2  = await dataset.shelf(store=store, type='store', order=2)
        trash   = await dataset.shelf(store=store, type='trash')

        await dataset.stock(
            product=product1,
            store=store,
            shelf=shelf1,
            count=100,
            valid='2020-01-01',
            lot=uuid(),
        )

        await dataset.stock(
            product=product2,
            store=store,
            shelf=shelf2,
            count=200,
            valid='2020-01-01',
            lot=uuid(),
        )

        await dataset.stock(
            product=product1,
            store=store,
            shelf=shelf1,
            count=300,
            valid='2020-01-01',
            lot=uuid(),
        )

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'Саджесты взятия просрочки')
        suggests = dict(((x.product_id, x.type), x) for x in suggests)

        with suggests[product1.product_id, 'shelf2box'] as suggest:
            tap.eq(suggest.count, 100+300, 'count')
            tap.ok(suggest.conditions.cancelable, 'отменяемый')
            tap.ok(await suggest.done(), 'Саджест выполнен')

        with suggests[product2.product_id, 'shelf2box'] as suggest:
            tap.eq(suggest.count, 200, 'count')
            tap.ok(suggest.conditions.cancelable, 'отменяемый')
            tap.ok(
                await suggest.done(count=5),
                'Саджест выполнен с меньшем количеством'
            )

        await wait_order_status(order, ('processing', 'waiting'))

        tap.ok(await order.cancel(), 'Пришла отмена')
        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'suggests_error', 'suggests_error')
        tap.eq(order.target, 'canceled', 'target: canceled')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)

        tap.eq(len(suggests), 4, 'Саджесты отката добавлены')
        suggests = dict(((x.product_id, x.type), x) for x in suggests)

        with suggests[product1.product_id, 'shelf2box'] as suggest:
            tap.eq(suggest.result_count, 100+300, 'count')

        with suggests[product2.product_id, 'shelf2box'] as suggest:
            tap.eq(suggest.result_count, 5, 'count')

        with suggests[product1.product_id, 'box2shelf'] as suggest:
            tap.eq(suggest.count, 100+300, 'count')

        with suggests[product2.product_id, 'box2shelf'] as suggest:
            tap.eq(suggest.count, 5, 'count')

        await wait_order_status(order, ('canceled', 'begin'), user_done=user)


async def test_box2shelf(tap, now, wait_order_status, uuid, dataset):
    with tap.plan(42, 'Откат саджестов при раскладке на полку списания'):
        product1 = await dataset.product(valid=10)
        product2 = await dataset.product(valid=10)

        store   = await dataset.store()
        user    = await dataset.user(store=store)

        shelf1  = await dataset.shelf(store=store, type='store', order=1)
        shelf2  = await dataset.shelf(store=store, type='store', order=2)
        trash   = await dataset.shelf(store=store, type='trash')

        await dataset.stock(
            product=product1,
            store=store,
            shelf=shelf1,
            count=100,
            valid='2020-01-01',
            lot=uuid(),
        )

        await dataset.stock(
            product=product2,
            store=store,
            shelf=shelf2,
            count=200,
            valid='2020-01-01',
            lot=uuid(),
        )

        await dataset.stock(
            product=product1,
            store=store,
            shelf=shelf1,
            count=300,
            valid='2020-01-01',
            lot=uuid(),
        )

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
        )

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'Саджесты взятия просрочки')
        suggests = dict(((x.product_id, x.type), x) for x in suggests)

        with suggests[product1.product_id, 'shelf2box'] as suggest:
            tap.eq(suggest.count, 100+300, 'count')
            tap.ok(suggest.conditions.cancelable, 'отменяемый')
            tap.ok(await suggest.done(), 'Саджест выполнен')

        with suggests[product2.product_id, 'shelf2box'] as suggest:
            tap.eq(suggest.count, 200, 'count')
            tap.ok(suggest.conditions.cancelable, 'отменяемый')
            tap.ok(
                await suggest.done(count=5),
                'Саджест выполнен с меньшем количеством'
            )

        await wait_order_status(order, ('processing', 'reserve_online'))
        tap.ok(
            await order.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )

        await wait_order_status(
            order, ('processing', 'suggests_write_off_prepare'))
        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 4, 'Саджесты взятия и раскладки в уценку')
        suggests = dict(((x.product_id, x.type), x) for x in suggests)

        with suggests[product1.product_id, 'shelf2box'] as suggest:
            tap.eq(suggest.result_count, 100+300, 'count')
            tap.ok(not suggest.conditions.cancelable, 'больше не отменяемый')

        with suggests[product2.product_id, 'shelf2box'] as suggest:
            tap.eq(suggest.result_count, 5, 'count')
            tap.ok(not suggest.conditions.cancelable, 'больше не отменяемый')

        with suggests[product1.product_id, 'box2shelf'] as suggest:
            tap.eq(suggest.count, 100+300, 'count')
            tap.eq(suggest.shelf_id, trash.shelf_id, 'trash')
            tap.ok(not suggest.conditions.cancelable, 'не отменяемый')
            tap.ok(await suggest.done(), 'Саджест раскладки')

        # Не будем выполнять
        with suggests[product2.product_id, 'box2shelf'] as suggest:
            tap.eq(suggest.count, 5, 'count')
            tap.eq(suggest.shelf_id, trash.shelf_id, 'trash')
            tap.ok(not suggest.conditions.cancelable, 'не отменяемый')

        tap.ok(await order.cancel(), 'Пришла отмена')
        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'suggests_error', 'suggests_error')
        tap.eq(order.target, 'canceled', 'target: canceled')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await dataset.Suggest.list_by_order(order)

        tap.eq(len(suggests), 6, 'Саджесты отката добавлены')
        suggests = dict(((x.product_id, x.shelf_id, x.type), x)
                        for x in suggests)

        with suggests[product1.product_id, shelf1.shelf_id, 'shelf2box'] as s:
            tap.eq(s.result_count, 100+300, 'count взять')

        with suggests[product2.product_id, shelf2.shelf_id, 'shelf2box'] as s:
            tap.eq(s.result_count, 5, 'count взять')

        with suggests[product1.product_id, trash.shelf_id, 'box2shelf'] as s:
            tap.eq(s.result_count, 100+300, 'count положить')

        with suggests[product1.product_id, shelf1.shelf_id, 'box2shelf'] as s:
            tap.eq(s.count, 100+300, 'count вернуть взятое')
            tap.ok(await s.done(), 'Саджест отката выполнен')

        with suggests[product2.product_id, shelf2.shelf_id, 'box2shelf'] as s:
            tap.eq(s.count, 5, 'count вернуть взятое')
            tap.ok(await s.done(), 'Саджест отката выполнен')

        with suggests[product1.product_id, trash.shelf_id, 'shelf2box'] as s:
            tap.eq(s.count, 100+300, 'count взять с уценки для возврата')
            tap.ok(await s.done(), 'Саджест отката выполнен')

        await wait_order_status(order, ('canceled', 'begin'), user_done=user)
