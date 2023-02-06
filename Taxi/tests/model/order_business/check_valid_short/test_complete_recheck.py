# pylint: disable=too-many-locals,unused-variable
from datetime import timedelta


async def test_recheck(tap, dataset, now, uuid, wait_order_status):
    with tap.plan(22, 'Проверяем создание дочернего заказа на перепроверку'):
        product = await dataset.product(valid=10, write_off_before=1)
        store   = await dataset.store()
        user    = await dataset.user(store=store)
        shelf   = await dataset.shelf(store=store, type='store', order=1)
        trash   = await dataset.shelf(store=store, type='trash', order=2)
        stock1  = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=10,
            valid='2020-01-01',  # Просрочен
            lot=uuid(),
        )
        stock2  = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=10,
            valid=now() + timedelta(days=100),  # Не просрочен
            lot=uuid(),
        )
        stock3  = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=30,
            valid='2020-01-01',  # Просрочен, но будет взят полностью
            lot=uuid(),
        )

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status = 'reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
        )

        with await dataset.order(store=store, type='order') as other:
            tap.ok(await stock1.do_reserve(other, 3), 'Уже зарезервировано')
            with await stock1.reload() as stock:
                tap.eq(stock.count, 10, 'count')
                tap.eq(stock.reserve, 3, 'reserve')
                tap.eq(stock.reserves[other.order_id], 3, 'reserves')

        await wait_order_status(
            order,
            ('processing', 'reserve_online'),
            user_done=user,
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
        await wait_order_status(
            order,
            ('complete', 'check_recheck'),
            user_done=user,
        )

        await order.business.order_changed()
        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'create_recheck', 'create_recheck')
        tap.eq(order.target, 'complete', 'target: complete')
        tap.ok(order.estatus_vars['external_id'],
               'Будущий идентификатор заказа записан')

        external_id = order.estatus_vars['external_id']

        await wait_order_status(order, ('complete', 'done'))

        recheck = await dataset.Order.load(
            (store.store_id, external_id), by='external')
        tap.ok(recheck, 'Создан новый ордер')
        tap.eq(recheck.parent, [order.order_id], 'parent')
        tap.eq(
            order.vars('child_order_id'),
            recheck.order_id,
            'Новый ордер сохранен у родителя',
        )
        tap.eq(recheck.company_id, order.company_id, 'company_id')
        tap.eq(
            recheck.vars.get('mode'),
            order.vars.get('mode'),
            'режим сохранен'
        )

        tap.eq(len(recheck.required), 1, 'Список требований на повтор')
        with recheck.required[0] as require:
            tap.eq(require.shelf_id, shelf.shelf_id, 'shelf_id')
            tap.eq(require.product_id, product.product_id, 'product_id')


async def test_recheck_no_create(tap, dataset, now, uuid, wait_order_status):
    with tap.plan(6, 'Проверяем что  заказа на перепроверку не создан'):
        product = await dataset.product(valid=10, write_off_before=1)
        store   = await dataset.store()
        user    = await dataset.user(store=store)
        shelf   = await dataset.shelf(store=store, type='store', order=1)
        trash   = await dataset.shelf(store=store, type='trash', order=2)
        stock1  = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=10,
            valid='2020-01-01',  # Просрочен
            lot=uuid(),
        )
        stock2  = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=10,
            valid=now() + timedelta(days=100),  # Не просрочен
            lot=uuid(),
        )
        stock3  = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=30,
            valid='2020-01-01',  # Просрочен, но будет взят полностью
            lot=uuid(),
        )

        external_id = uuid()
        order = await dataset.order(
            store=store,
            type='check_valid_short',
            status='complete',
            estatus='check_recheck',
            acks=[user.user_id],
            approved=now(),
            estatus_vars={
                'external_id': external_id,
            }
        )

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'check_recheck', 'check_recheck')
        tap.eq(order.target, 'complete', 'target: complete')

        await wait_order_status(order, ('complete', 'done'))
        recheck = await dataset.Order.load(
            (store.store_id, external_id), by='external')
        tap.eq(recheck, None, 'recheck не создан')
