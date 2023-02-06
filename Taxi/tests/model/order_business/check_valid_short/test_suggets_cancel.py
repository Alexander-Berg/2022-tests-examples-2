# pylint: disable=too-many-statements, too-many-locals

from datetime import timedelta
from stall.model.suggest import Suggest


async def test_more_product(tap, now, dataset, uuid, wait_order_status):
    with tap.plan(75, 'Различные вариации отмен'):
        product1 = await dataset.product(valid=10, write_off_before=1)
        product2 = await dataset.product(valid=10, write_off_before=1)
        product3 = await dataset.product(valid=10, write_off_before=1)

        product4 = await dataset.product(valid=10, write_off_before=1)

        store = await dataset.store()
        user = await dataset.user(store=store)

        shelf = await dataset.shelf(store=store, type='store', order=1)
        trash = await dataset.shelf(store=store, type='trash', order=2)

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product1,
            count=1,
            valid=now() - timedelta(days=100),  # Просрочен
            lot=uuid(),
        )

        stock2 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product2,
            count=2,
            valid=now() - timedelta(days=100),  # Просрочен
            lot=uuid(),
        )

        stock3 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product3,
            count=3,
            valid=now() - timedelta(days=100),  # Просрочен
            lot=uuid(),
        )

        stock4 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product4,
            count=4,
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

        suggests = await dataset.Suggest.list_by_order(order)
        tap.eq(len(suggests), 4, 'Саджесты созданы')
        suggests = dict(((x.type, x.count), x) for x in suggests)

        # закрываем первый в 0, потом отмена, потом закрываем правильно
        with suggests[('shelf2box', 1)] as suggest:  # на 1 продукт
            tap.eq(suggest.type, 'shelf2box', 'type=shelf2box')
            tap.eq(suggest.count, 1, 'count=1')
            tap.eq(suggest.result_count, None, 'result_count=None')
            tap.eq(suggest.status, 'request', 'status=request')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.ok(await suggest.done(count=0), 'Берем 1 продукт в 0')
            tap.eq(suggest.vars('problem', None), None, 'нет проблем')

            tap.ok(await suggest.done(
                status='cancel',
            ), 'отменили')
            await wait_order_status(
                order,
                ('processing', 'unreserve_cancel'),
            )
            await wait_order_status(
                order,
                ('processing', 'reserve_online'),
            )
            await order.business.order_changed()

            tap.ok(await suggest.done(count=1), 'Берем 1 продукт в 1')

        # закрываем первый правильно, потом отмена, потом закрываем в 0
        with suggests[('shelf2box', 2)] as suggest:  # на 2 продукт
            tap.eq(suggest.type, 'shelf2box', 'type=shelf2box')
            tap.eq(suggest.count, 2, 'count=2')
            tap.eq(suggest.result_count, None, 'result_count=None')
            tap.eq(suggest.status, 'request', 'status=request')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.ok(await suggest.done(count=2), 'Берем 2 продукт в 2')
            tap.eq(suggest.vars('problem', None), None, 'нет проблем')
            # ---------
            await wait_order_status(
                order,
                ('processing', 'waiting'),
            )

            tap.ok(await suggest.done(
                status='cancel',
            ), 'отменили')
            await wait_order_status(
                order,
                ('processing', 'waiting'),
            )
            tap.ok(await suggest.done(count=0), 'Берем 2 продукт в 0')


        # закрываем первый в меньшее, потом отмена, потом закрываем в правильно
        with suggests[('shelf2box', 3)] as suggest:  # на 3 продукт
            tap.eq(suggest.type, 'shelf2box', 'type=shelf2box')
            tap.eq(suggest.count, 3, 'count=3')
            tap.eq(suggest.result_count, None, 'result_count=None')
            tap.eq(suggest.status, 'request', 'status=request')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.ok(await suggest.done(count=2), 'Берем 3 продукт в 2(меньше)')
            tap.eq(suggest.vars('problem', None), None, 'нет проблем')
            # ---------
            await wait_order_status(
                order,
                ('processing', 'waiting'),
            )

            tap.ok(await suggest.done(
                status='cancel',
            ), 'отменили')
            await wait_order_status(
                order,
                ('processing', 'waiting'),
            )
            tap.ok(await suggest.done(count=3), 'Берем 2 продукт в 3')
            await wait_order_status(
                order,
                ('processing', 'reserve_online'),
            )
            await order.business.order_changed()


        with suggests[('shelf2box', 4)] as suggest:  # на 4 продукт
            tap.eq(suggest.type, 'shelf2box', 'type=shelf2box')
            tap.eq(suggest.count, 4, 'count=3')
            tap.eq(suggest.result_count, None, 'result_count=None')
            tap.eq(suggest.status, 'request', 'status=request')
            tap.eq(suggest.shelf_id, shelf.shelf_id, 'shelf=store')
            tap.ok(await suggest.done(count=4),
                   'Берем 4 продукт в 4(правильное закрытие)')
            tap.eq(suggest.vars('problem', None), None, 'нет проблем')
            await wait_order_status(
                order,
                ('processing', 'reserve_online'),
            )
            await order.business.order_changed()
            # ---------

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
            ('complete', 'write_off'),
            user_done=user,
        )

        suggests = await Suggest.list_by_order(
            order,
            types=['box2shelf'],
        )
        tap.eq(len(suggests), 3, 'Саджесты на полку списания')

        suggests = dict(((x.type, x.count), x) for x in suggests)
        with suggests[('box2shelf', 1)] as suggest:
            tap.eq(suggest.type, 'box2shelf', 'type=box2shelf')
            tap.eq(suggest.count, 1, 'count=1')
            tap.eq(suggest.result_count, 1, 'result_count=1')
            tap.eq(suggest.shelf_id, trash.shelf_id, 'shelf=trash')
            tap.eq(suggest.product_id, product1.product_id, 'product1')
            tap.ok(await suggest.done(count=1), 'Закрыли product1')

        with suggests[('box2shelf', 3)] as suggest:
            tap.eq(suggest.type, 'box2shelf', 'type=box2shelf')
            tap.eq(suggest.count, 3, 'count=3')
            tap.eq(suggest.result_count, 3, 'result_count=1')
            tap.eq(suggest.shelf_id, trash.shelf_id, 'shelf=trash')
            tap.eq(suggest.product_id, product3.product_id, 'product3')
            tap.ok(await suggest.done(count=3), 'Закрыли product3')

        with suggests[('box2shelf', 4)] as suggest:
            tap.eq(suggest.type, 'box2shelf', 'type=box2shelf')
            tap.eq(suggest.count, 4, 'count=3')
            tap.eq(suggest.result_count, 4, 'result_count=1')
            tap.eq(suggest.shelf_id, trash.shelf_id, 'shelf=trash')
            tap.eq(suggest.product_id, product4.product_id, 'product4')
            tap.ok(await suggest.done(count=4), 'Закрыли product4')


        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user,
        )

        await order.business.order_changed()

        # Проверим стоки
        with await stock1.reload() as stock:
            tap.eq(stock.count, 0, 'Все списано')
            tap.eq(stock.reserve, 0, 'Резерва нет')

        with await stock2.reload() as stock:
            tap.eq(stock.count, 2, 'На втором стоке продукт')
            tap.eq(stock.reserve, 0, 'Резерва нет')

        with await stock3.reload() as stock:
            tap.eq(stock.count, 0, 'Все списано')
            tap.eq(stock.reserve, 0, 'Резерва нет')

        with await stock4.reload() as stock:
            tap.eq(stock.count, 0, 'Все списано')
            tap.eq(stock.reserve, 0, 'Резерва нет')
