# pylint: disable=unused-variable

from stall.model.suggest import Suggest


async def test_waiting(tap, uuid, dataset, now, wait_order_status):
    with tap.plan(6, 'Ожидание выполнения'):

        product1 = await dataset.product(valid=10)
        product2 = await dataset.product(valid=10)

        store = await dataset.store()
        user  = await dataset.user(store=store)

        shelf1 = await dataset.shelf(store=store, type='store', order=1)
        shelf2 = await dataset.shelf(store=store, type='store', order=2)
        trash  = await dataset.shelf(store=store, type='trash', order=100)

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
        )

        await dataset.stock(
            store=store,
            order=order,
            shelf=shelf1,
            product=product1,
            count=7,
            reserve=7,
            valid='2020-01-01',
            lot=uuid(),
        )

        await dataset.stock(
            store=store,
            order=order,
            shelf=shelf1,
            product=product1,
            count=3,
            reserve=3,
            valid='2020-01-01',
            lot=uuid(),
        )

        await dataset.stock(
            store=store,
            order=order,
            shelf=shelf2,
            product=product2,
            count=20,
            reserve=20,
            valid='2020-01-01',
            lot=uuid(),
        )

        await wait_order_status(order, ('processing', 'waiting'))

        await order.business.order_changed()
        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')


async def test_waiting_no_suggests(tap, uuid, dataset, wait_order_status, cfg):
    cfg.set('business.order.check_valid_short.trash_suggests', False)
    with tap.plan(15, 'Не генерируются саджесты на полку trash'):
        product1 = await dataset.product(valid=10)
        product2 = await dataset.product(valid=10)

        store = await dataset.store()
        user = await dataset.user(store=store)
        await dataset.shelf(store=store, type='trash', order=3)

        shelf1 = await dataset.shelf(store=store, type='store', order=1)
        shelf2 = await dataset.shelf(store=store, type='store', order=2)

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

        await dataset.stock(
            store=store,
            order=order,
            shelf=shelf1,
            product=product1,
            count=7,
            reserve=7,
            valid='2020-01-01',
            lot=uuid(),
        )

        await dataset.stock(
            store=store,
            order=order,
            shelf=shelf1,
            product=product1,
            count=3,
            reserve=3,
            valid='2020-01-01',
            lot=uuid(),
        )

        await dataset.stock(
            store=store,
            order=order,
            shelf=shelf2,
            product=product2,
            count=20,
            reserve=20,
            valid='2020-01-01',
            lot=uuid(),
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user
        )
        tap.ok(
            await order.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )

        tap.ok(await order.done('complete', user=user), 'Завершаем заказ')

        await wait_order_status(
            order,
            ('complete', 'begin'),
            user_done=user
        )

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'begin', 'begin')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await Suggest.list_by_order(
            order,
            types=['box2shelf'],
        )
        tap.ok(not suggests, 'Саджестов на полку списания нет')
    cfg.set('business.order.check_valid_short.trash_suggests', True)
