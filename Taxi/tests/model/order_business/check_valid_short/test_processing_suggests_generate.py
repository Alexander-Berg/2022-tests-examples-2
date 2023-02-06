# pylint: disable=too-many-locals,unused-variable

from datetime import timedelta

from stall.model.suggest import Suggest


async def test_suggests_generate(tap, uuid, now, dataset, wait_order_status):
    with tap.plan(26, 'Генерация новых саджестов'):

        product1 = await dataset.product(valid=10)
        product2 = await dataset.product(valid=10)

        store = await dataset.store()
        user = await dataset.user(store=store)

        shelf1 = await dataset.shelf(store=store, type='store', order=1)
        shelf2 = await dataset.shelf(store=store, type='store', order=2)
        trash  = await dataset.shelf(store=store, type='trash', order=1)

        await dataset.stock(
            store=store,
            shelf=shelf1,
            product=product1,
            count=7,
            valid='2020-01-01',
            lot=uuid(),
        )

        await dataset.stock(
            store=store,
            shelf=shelf1,
            product=product1,
            count=3,
            valid='2020-01-01',
            lot=uuid(),
        )

        await dataset.stock(
            store=store,
            shelf=shelf2,
            product=product2,
            count=20,
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

        suggest1 = await dataset.suggest(
            order,
            type='shelf2box',
            shelf_id=shelf1.shelf_id,
            product_id=product1.product_id,
            count=2,
        )
        tap.ok(suggest1, 'Саджест 1')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Какие-то саджесты уже были')

        tap.ok(
            await wait_order_status(
                order,
                ('processing', 'suggests_generate'),
            ),
            'Выполнили резервирование'
        )

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'suggests_generate', 'suggests_generate')
        tap.eq(order.target, 'complete', 'target: complete')

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'processing', 'processing')
        tap.eq(order.estatus, 'waiting', 'waiting')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(order.problems, [], 'Нет проблем')
        tap.eq(
            sorted(order.shelves),
            sorted([x.shelf_id for x in (shelf1, shelf2)]),
            'Список полок'
        )

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'Список саджестов')

        with suggests[0] as suggest:
            tap.eq(suggest.type, 'shelf2box', f'type={suggest.type}')
            tap.eq(
                suggest.product_id,
                product1.product_id,
                f'product_id={suggest.product_id}'
            )
            tap.eq(
                suggest.shelf_id,
                shelf1.shelf_id,
                f'shelf_id={suggest.shelf_id}'
            )
            tap.eq(
                suggest.count,
                10,
                f'valid={suggest.count}'
            )

        with suggests[1] as suggest:
            tap.eq(suggest.type, 'shelf2box', f'type={suggest.type}')
            tap.eq(
                suggest.product_id,
                product2.product_id,
                f'product_id={suggest.product_id}'
            )
            tap.eq(
                suggest.shelf_id,
                shelf2.shelf_id,
                f'shelf_id={suggest.shelf_id}'
            )
            tap.eq(
                suggest.count,
                20,
                f'valid={suggest.count}'
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
            ('complete', 'done'),
            user_done=user,
        )


async def test_none(tap, uuid, dataset, now, wait_order_status):
    with tap.plan(11, 'Проверка поведение с valid=None'):

        product1 = await dataset.product(valid=10)
        store = await dataset.store()
        user = await dataset.user(store=store)
        shelf1 = await dataset.shelf(store=store, type='store', order=1)
        await dataset.shelf(store=store, type='trash', order=1)
        await dataset.stock(
            store=store,
            shelf=shelf1,
            product=product1,
            count=10,
            valid=None,
            lot=uuid(),
        )
        await dataset.stock(
            store=store,
            shelf=shelf1,
            product=product1,
            count=20,
            valid=now().date(),
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
        tap.ok(order, 'Заказ создан')

        await wait_order_status(
            order,
            ('processing', 'suggests_generate'),
        )

        await order.business.order_changed()

        tap.eq(order.problems, [], 'Нет проблем')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 1, 'Список саджестов')

        with suggests[0] as suggest:
            tap.eq(suggest.type, 'shelf2box', f'type={suggest.type}')
            tap.eq(
                suggest.product_id,
                product1.product_id,
                f'product_id={suggest.product_id}'
            )
            tap.eq(
                suggest.shelf_id,
                shelf1.shelf_id,
                f'shelf_id={suggest.shelf_id}'
            )
            tap.eq(
                suggest.count,
                30,
                f'valid={suggest.count}'
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
            ('complete', 'done'),
            user_done=user,
        )


async def test_empty_write_off(tap, dataset, now, uuid, wait_order_status):
    with tap.plan(14, 'Нет ни одного просроченного продукта, нет саджестов'):
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
            await wait_order_status(
                order,
                ('processing', 'waiting'),
            ),
            'Выполнили резервирование'
        )

        tap.ok(await order.reload(), 'Перезабрали заказ')

        tap.eq(order.problems, [], 'Нет проблем')

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 0, 'Нет саджестов')

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
            ('complete', 'done'),
            user_done=user,
        )
