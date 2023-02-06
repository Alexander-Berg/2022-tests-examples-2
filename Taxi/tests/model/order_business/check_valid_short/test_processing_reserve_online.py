# pylint: disable=too-many-locals,too-many-statements,unused-variable

from datetime import timedelta
from stall.model.stock import Stock

async def test_reserve(tap, now, dataset, uuid, wait_order_status):
    with tap.plan(25, 'Онлайн резервирование'):

        product = await dataset.product(valid=10, write_off_before=1)

        store = await dataset.store()
        user = await dataset.user(store=store)

        shelf = await dataset.shelf(store=store, type='store', order=1)
        trash = await dataset.shelf(store=store, type='trash', order=2)

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=10,
            valid=now() - timedelta(days=100),  # Просрочен
            lot=uuid(),
        )
        stock2 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=20,
            valid=now() + timedelta(days=100),  # Не просрочен
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

        await wait_order_status(
            order, ('processing', 'waiting'), user_done=user)

        tap.eq(
            order.vars['write_off'][shelf.shelf_id][product.product_id],
            [stock1.stock_id],
            'Просроченные остатки 1'
        )

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
            ('processing', 'waiting'),
            user_done=user,
        )

        await wait_order_status(order, ('complete', 'begin'), user_done=user)

        await order.reload()
        tap.eq(order.vars['suggests_write_off'], True, 'саджесты сгенерированы')

        suggests = await dataset.Suggest.list_by_order(order.order_id)
        tap.eq(len(suggests), 2, 'Саджесты созданы')
        suggests = dict(((x.type, x.count), x) for x in suggests)

        with suggests[('shelf2box', 10)] as suggest:
            tap.eq(suggest.type, 'shelf2box', 'type=shelf2box')
            tap.eq(suggest.count, 10, 'count=10')
            tap.eq(suggest.result_count, 10, 'result_count=10')
            tap.eq(suggest.status, 'done', 'status=done')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.eq(suggest.vars('problem', None), None, 'нет проблем')

        with suggests[('box2shelf', 10)] as suggest:
            tap.eq(suggest.type, 'box2shelf', 'type=box2shelf')
            tap.eq(suggest.count, 10, 'count=10')
            tap.eq(suggest.result_count, 10, 'result_count=10')
            tap.eq(suggest.status, 'done', 'status=done')
            tap.eq(suggest.shelf_id, trash.shelf_id, 'shelf=trash')
            tap.eq(suggest.vars('problem', None), None, 'нет проблем')

        stocks = await dataset.Stock.list_by_order(order)
        with stocks[0] as stock:
            tap.eq(stock.stock_id, stock1.stock_id, 'Просроченный остаток')
            tap.eq(stock.count, 10, 'count')
            tap.eq(stock.reserve, 10, 'reserve')
            tap.eq(stock.reserves[order.order_id], 10, 'reserves')


async def test_reserve_fail(tap, now, dataset, uuid, wait_order_status):
    with tap.plan(55, 'Недостаточно товара для резервирования'):
        product = await dataset.product(valid=10, write_off_before=1)

        store = await dataset.store()
        user = await dataset.user(store=store)

        shelf = await dataset.shelf(store=store, type='store', order=1)
        trash = await dataset.shelf(store=store, type='trash', order=2)

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=10,
            valid=now() - timedelta(days=100),  # Просрочен
            lot=uuid(),
        )
        stock2 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=20,
            valid=now() + timedelta(days=100),  # Не просрочен
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

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        tap.eq(
            order.vars['write_off'][shelf.shelf_id][product.product_id],
            [stock1.stock_id],
            'Просроченные остатки 1'
        )

        with await dataset.order(store=store, type='order') as other:
            tap.ok(
                await stock1.do_reserve(other, 3),
                'Часть уже зарезервирована'
            )
            with await stock1.reload() as stock:
                tap.eq(stock.count, 10, 'count')
                tap.eq(stock.reserve, 3, 'reserve')
                tap.eq(stock.reserves[other.order_id], 3, 'reserves')

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Саджесты созданы')
        suggests = dict(((x.type, x.count), x) for x in suggests)

        with suggests[('shelf2box', 10)] as suggest:
            tap.eq(suggest.type, 'shelf2box', 'type=shelf2box')
            tap.eq(suggest.count, 10, 'count=10')
            tap.eq(suggest.result_count, None, 'result_count=None')
            tap.eq(suggest.status, 'request', 'status=request')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.ok(await suggest.done(count=10), 'Берем всю просрочку')
            tap.eq(suggest.vars('problem', None), None, 'нет проблем')

        await wait_order_status(
            order,
            ('processing', 'suggests_rollback_online')
        )
        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await dataset.Suggest.list_by_order(order.order_id)
        tap.eq(len(suggests), 2, 'Саджесты созданы 2')
        suggests = dict(((x.type, x.count), x) for x in suggests)

        with suggests[('shelf2box', 10)] as suggest:  # на взятие
            tap.eq(suggest.type, 'shelf2box', 'type=shelf2box')
            tap.eq(suggest.count, 10, 'count=10')
            tap.eq(suggest.result_count, 10, 'result_count=10')
            tap.eq(suggest.status, 'done', 'status=done')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.eq(suggest.vars('problem', None), 'too_low', 'проблема')
        # на возврат что не смогли зарезервировать
        with suggests[('box2shelf', 3)] as suggest:
            tap.eq(suggest.type, 'box2shelf', 'type=box2shelf')
            tap.eq(suggest.count, 3, 'count=3')
            tap.eq(suggest.result_count, None, 'result_count=None')
            tap.eq(suggest.status, 'request', 'status=request')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.ok(await suggest.done(count=3), 'Положили назад перебор')
            tap.eq(suggest.vars('problem', None), None, 'нет проблем')

        tap.ok(
            await order.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )
        await wait_order_status(order, ('processing', 'waiting'))
        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await dataset.Suggest.list_by_order(order.order_id)

        tap.eq(len(suggests), 3, 'Саджесты созданы 3')
        suggests = dict(((x.type, x.count), x) for x in suggests)

        with suggests[('shelf2box', 10)] as suggest:  # на взятие
            tap.eq(suggest.status, 'done', 'status=done')
        # на возврат что не смогли зарезервировать
        with suggests[('box2shelf', 3)] as suggest:
            tap.eq(suggest.type, 'box2shelf', 'type=box2shelf')
            tap.eq(suggest.count, 3, 'count=3')
            tap.eq(suggest.result_count, 3, 'result_count=3')
            tap.eq(suggest.status, 'done', 'status=done')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.eq(suggest.vars('problem', None), None, 'нет проблем')
        with suggests[('box2shelf', 7)] as suggest:  # на выброс
            tap.eq(suggest.type, 'box2shelf', 'type=box2shelf')
            tap.eq(suggest.count, 7, 'count=7')
            tap.eq(suggest.result_count, None, 'result_count=None')
            tap.eq(suggest.status, 'request', 'status=request')
            tap.eq(suggest.shelf_id, trash.shelf_id, 'shelf=trash')
            tap.ok(await suggest.done(count=7), 'Положили на полку списаний')
            tap.eq(suggest.vars('problem', None), None, 'нет проблем')

        stocks = await dataset.Stock.list_by_order(order)
        with stocks[0] as stock:
            tap.eq(stock.stock_id, stock1.stock_id, 'Просроченный остаток')
            tap.eq(stock.count, 10, 'count')
            tap.eq(stock.reserve, 10, 'reserve')
            tap.eq(stock.reserves[order.order_id], 7, 'reserves')

        await wait_order_status(order, ('complete', 'begin'), user_done=user)


async def test_reserve_restart(tap, now, dataset, uuid, wait_order_status):
    with tap.plan(32, 'Проверяем правильность работы при перезапуске статуса'):

        product = await dataset.product(valid=10, write_off_before=1)

        store = await dataset.store()
        user = await dataset.user(store=store)

        shelf = await dataset.shelf(store=store, type='store', order=1)
        trash = await dataset.shelf(store=store, type='trash', order=2)

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=10,
            valid=now() - timedelta(days=100),  # Просрочен
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

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        tap.eq(
            order.vars['write_off'][shelf.shelf_id][product.product_id],
            [stock1.stock_id],
            'Просроченные остатки 1'
        )

        with await dataset.order(store=store, type='order') as other:
            tap.ok(
                await stock1.do_reserve(other, 3),
                'Часть уже зарезервирована'
            )
            with await stock1.reload() as stock:
                tap.eq(stock.count, 10, 'count')
                tap.eq(stock.reserve, 3, 'reserve')
                tap.eq(stock.reserves[other.order_id], 3, 'reserves')

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Саджесты созданы')
        suggests = dict(((x.type, x.count), x) for x in suggests)

        with suggests[('shelf2box', 10)] as suggest:
            tap.eq(suggest.type, 'shelf2box', 'type=shelf2box')
            tap.eq(suggest.count, 10, 'count=10')
            tap.eq(suggest.result_count, None, 'result_count=None')
            tap.eq(suggest.status, 'request', 'status=request')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.ok(await suggest.done(count=10), 'Берем всю просрочку')
            tap.eq(suggest.vars('problem', None), None, 'нет проблем')

        await wait_order_status(
            order,
            ('processing', 'suggests_rollback_online')
        )
        # выполним suggests_rollback_online
        await order.business.order_changed()
        # имитируем падение
        order.estatus = 'suggests_rollback_online'
        tap.ok(await order.save(), 'Вернулись  к suggests_rollback_online')

        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await dataset.Suggest.list_by_order(order.order_id)
        tap.eq(len(suggests), 2, 'Саджесты созданы 2')
        suggests = dict(((x.type, x.count), x) for x in suggests)

        with suggests[('shelf2box', 10)] as suggest:  # на взятие
            tap.eq(suggest.type, 'shelf2box', 'type=shelf2box')
            tap.eq(suggest.count, 10, 'count=10')
            tap.eq(suggest.result_count, 10, 'result_count=10')
            tap.eq(suggest.status, 'done', 'status=done')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.eq(suggest.vars('problem', None), 'too_low', 'проблема')
        # на возврат что не смогли зарезервировать
        with suggests[('box2shelf', 3)] as suggest:
            tap.eq(suggest.type, 'box2shelf', 'type=box2shelf')
            tap.eq(suggest.count, 3, 'count=3')
            tap.eq(suggest.result_count, None, 'result_count=None')
            tap.eq(suggest.status, 'request', 'status=request')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.ok(await suggest.done(count=3), 'Положили назад перебор')
            tap.eq(suggest.vars('problem', None), None, 'нет проблем')


async def test_cancel(tap, now, dataset, uuid, wait_order_status):
    with tap.plan(35, 'Недостаточно товара для резервирования'):

        product = await dataset.product(valid=10, write_off_before=1)

        store = await dataset.store()
        user = await dataset.user(store=store)

        shelf = await dataset.shelf(store=store, type='store', order=1)
        trash = await dataset.shelf(store=store, type='trash', order=2)

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=10,
            valid=now() - timedelta(days=100),  # Просрочен
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

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        tap.eq(
            order.vars['write_off'][shelf.shelf_id][product.product_id],
            [stock1.stock_id],
            'Просроченные остатки 1'
        )

        with await dataset.order(store=store, type='order') as other:
            tap.ok(
                await stock1.do_reserve(other, 3),
                'Часть уже зарезервирована'
            )
            with await stock1.reload() as stock:
                tap.eq(stock.count, 10, 'count')
                tap.eq(stock.reserve, 3, 'reserve')
                tap.eq(stock.reserves[other.order_id], 3, 'reserves')

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Саджесты созданы')
        suggests = dict(((x.type, x.count), x) for x in suggests)

        with suggests[('shelf2box', 10)] as suggest:
            tap.eq(suggest.type, 'shelf2box', 'type=shelf2box')
            tap.eq(suggest.count, 10, 'count=10')
            tap.eq(suggest.result_count, None, 'result_count=None')
            tap.eq(suggest.status, 'request', 'status=request')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.ok(await suggest.done(count=10), 'Берем всю просрочку')
            tap.eq(suggest.vars('problem', None), None, 'нет проблем')

        await wait_order_status(
            order,
            ('processing', 'suggests_rollback_online')
        )
        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await dataset.Suggest.list_by_order(order.order_id)
        tap.eq(len(suggests), 2, 'Саджесты созданы 2')
        suggests = dict(((x.type, x.count), x) for x in suggests)


        with suggests[('shelf2box', 10)] as suggest:  # на взятие
            tap.eq(suggest.type, 'shelf2box', 'type=shelf2box')
            tap.eq(suggest.count, 10, 'count=10')
            tap.eq(suggest.result_count, 10, 'result_count=10')
            tap.eq(suggest.status, 'done', 'status=done')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.eq(suggest.vars('problem', None), 'too_low', 'проблема')
            tap.ok(await suggest.done(
                status='cancel',
            ), 'отменили')

        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(len(order.problems), 0, 'Нет проблем')
        await order.business.order_changed()

        suggests = await dataset.Suggest.list_by_order(order.order_id)

        tap.eq(len(suggests), 1, 'Саджесты 1')
        suggests = dict(((x.type, x.count), x) for x in suggests)
        with suggests[('shelf2box', 10)] as suggest:  # на взятие
            tap.eq(suggest.type, 'shelf2box', 'type=shelf2box')
            tap.eq(suggest.count, 10, 'count=10')
            tap.eq(suggest.result_count, None, 'result_count=10')
            tap.eq(suggest.status, 'request', 'status=request')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.eq(suggest.vars['reserved'], False, 'reserved')

        stocks = await Stock.list_by_order(order)
        tap.eq(len(stocks), 0, 'нет резервов')


async def test_cancel_two_stocks(tap, now, dataset, uuid, wait_order_status):
    with tap.plan(47, 'Недостаточно товара для резервирования'):

        product = await dataset.product(valid=10, write_off_before=1)

        store = await dataset.store()
        user = await dataset.user(store=store)

        shelf = await dataset.shelf(store=store, type='store', order=1)
        trash = await dataset.shelf(store=store, type='trash', order=2)

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=10,
            valid=now() - timedelta(days=100),  # Просрочен
            lot=uuid(),
        )

        product2 = await dataset.product(valid=10, write_off_before=1)
        stock2 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product2,
            count=20,
            valid=now() - timedelta(days=200),  # Просрочен
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

        await wait_order_status(
            order,
            ('processing', 'waiting'),
        )

        tap.eq(
            order.vars['write_off'][shelf.shelf_id][product.product_id],
            [stock1.stock_id],
            'Просроченные остатки 1'
        )

        with await dataset.order(store=store, type='order') as other:
            tap.ok(
                await stock1.do_reserve(other, 3),
                'Часть уже зарезервирована'
            )
            with await stock1.reload() as stock:
                tap.eq(stock.count, 10, 'count')
                tap.eq(stock.reserve, 3, 'reserve')
                tap.eq(stock.reserves[other.order_id], 3, 'reserves')

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'Саджесты созданы')
        suggests = dict(((x.type, x.count), x) for x in suggests)

        with suggests[('shelf2box', 10)] as suggest:
            tap.eq(suggest.type, 'shelf2box', 'type=shelf2box')
            tap.eq(suggest.count, 10, 'count=10')
            tap.eq(suggest.result_count, None, 'result_count=None')
            tap.eq(suggest.status, 'request', 'status=request')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.ok(await suggest.done(count=10), 'Берем всю просрочку')
            tap.eq(suggest.vars('problem', None), None, 'нет проблем')

        with suggests[('shelf2box', 20)] as suggest:
            tap.eq(suggest.type, 'shelf2box', 'type=shelf2box')
            tap.eq(suggest.count, 20, 'count=20')
            tap.eq(suggest.result_count, None, 'result_count=None')
            tap.eq(suggest.status, 'request', 'status=request')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.ok(await suggest.done(count=20), 'Берем всю просрочку')
            tap.eq(suggest.vars('problem', None), None, 'нет проблем')

        await wait_order_status(
            order,
            ('processing', 'suggests_rollback_online')
        )
        await wait_order_status(order, ('processing', 'waiting'))

        tap.eq(len(order.problems), 0, 'Нет проблем')

        suggests = await dataset.Suggest.list_by_order(order.order_id)
        tap.eq(len(suggests), 3, 'Саджесты созданы 3')
        suggests = dict(((x.type, x.count), x) for x in suggests)


        with suggests[('shelf2box', 10)] as suggest:  # на взятие
            tap.eq(suggest.type, 'shelf2box', 'type=shelf2box')
            tap.eq(suggest.count, 10, 'count=10')
            tap.eq(suggest.result_count, 10, 'result_count=10')
            tap.eq(suggest.status, 'done', 'status=done')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.eq(suggest.vars('problem', None), 'too_low', 'проблема')
            tap.ok(await suggest.done(
                status='cancel',
            ), 'отменили')

        await wait_order_status(order, ('processing', 'waiting'))
        tap.eq(len(order.problems), 0, 'Нет проблем')
        await order.business.order_changed()

        suggests = await dataset.Suggest.list_by_order(order.order_id)

        tap.eq(len(suggests), 2, 'Саджесты 2')
        suggests = dict(((x.type, x.count), x) for x in suggests)
        with suggests[('shelf2box', 10)] as suggest:  # на взятие
            tap.eq(suggest.type, 'shelf2box', 'type=shelf2box')
            tap.eq(suggest.count, 10, 'count=10')
            tap.eq(suggest.result_count, None, 'result_count=10')
            tap.eq(suggest.status, 'request', 'status=request')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.eq(suggest.vars['reserved'], False, 'reserved')
            tap.eq(len(suggest.vars['logs']), 2, 'vars canceled')
            tap.eq(suggest.vars['logs'][1]['result_count'], 10,
                   'сохранили старый result_count')
            tap.eq(suggest.vars['logs'][1]['status'], 'done',
                   'сохранили старый status')


        stocks = await Stock.list_by_order(order)
        tap.eq(len(stocks), 1, 'Только на один продукт резервов')

        with stocks[0] as stock:
            tap.eq(stock.product_id, product2.product_id, 'product_id')
            tap.eq(stock.count, 20, 'count')


async def test_no_vars_reserved(tap, uuid, now, dataset, wait_order_status):
    with tap.plan(18, 'Онлайн резервирование'):
        product = await dataset.product(valid=10, write_off_before=1)

        store = await dataset.store()
        user = await dataset.user(store=store)

        shelf = await dataset.shelf(store=store, type='store', order=1)
        trash = await dataset.shelf(store=store, type='trash', order=2)

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=10,
            valid=now() - timedelta(days=100),  # Просрочен
            lot=uuid(),
        )

        order = await dataset.order(
            store=store,
            type='check_valid_short',
            status='reserving',
            estatus='begin',
            acks=[user.user_id],
            approved=now(),
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )

        tap.eq(
            order.vars['write_off'][shelf.shelf_id][product.product_id],
            [stock1.stock_id],
            'Просроченные остатки 1'
        )

        suggests = await dataset.Suggest.list_by_order(order.order_id)
        tap.eq(len(suggests), 1, 'Саджесты созданы')
        suggests = dict(((x.type, x.count), x) for x in suggests)

        with suggests[('shelf2box', 10)] as suggest:
            tap.eq(suggest.type, 'shelf2box', 'type=shelf2box')
            tap.eq(suggest.count, 10, 'count=10')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.eq(suggest.vars('problem', None), None, 'нет проблем')
            tap.eq(suggest.vars('revision'),
                   suggest.revision, 'revision')
            # Достаем ревизию
            suggest.vars.pop('revision', None)
            suggest.rehashed('vars', True)
            await suggest.save()

        await wait_order_status(
            order,
            ('processing', 'unreserve_cancel'),
            user_done=user,
        )

        await stock1.reload()
        tap.eq(stock1.stock_id, stock1.stock_id, 'Разрезервировали')
        tap.eq(stock1.count, 10, 'count')
        tap.eq(stock1.reserve, 0, 'reserve')

        await wait_order_status(
            order,
            ('processing', 'reserve_online'),
            user_done=user,
        )
        await order.business.order_changed()

        with suggests[('shelf2box', 10)] as suggest:
            await suggest.reload()
            tap.eq(suggest.vars('revision'),
                   suggest.revision, 'revision')
            tap.eq(suggest.vars('reserved'),
                   True, 'reserved')

        await stock1.reload()
        tap.eq(stock1.stock_id, stock1.stock_id, 'Перерезервировали')
        tap.eq(stock1.count, 10, 'count')
        tap.eq(stock1.reserve, 10, 'reserve')
