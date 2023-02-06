# pylint: disable=too-many-locals,unused-variable


async def test_store2markdown(
        tap,
        uuid,
        dataset,
        now,
        wait_order_status,
):
    with tap.plan(17, 'Полный цикл перемещения на полку уценки'):

        product = await dataset.product(valid=10, write_off_before=1)
        assortment = await dataset.assortment()
        await dataset.assortment_product(assortment=assortment, product=product)

        store = await dataset.store(markdown_assortment=assortment)
        user  = await dataset.user(store=store)

        shelf  = await dataset.shelf(store=store, type='store', order=1)
        trash  = await dataset.shelf(store=store, type='trash', order=3)
        mark   = await dataset.shelf(store=store, type='markdown', order=4)

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=7,
            valid='2020-01-01',
            lot=uuid(),
        )

        stock2 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=3,
            valid='2020-01-01',
            lot=uuid(),
        )

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='reserving',
            estatus='begin',
            accepted=now(),
            acks=[user.user_id],
            vars={'mode': 'store2markdown'},
        )

        await wait_order_status(
            order,
            ('processing', 'reserve_online'),
            user_done=user,
        )
        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )
        await order.reload()
        tap.eq(order.vars['stage'],
               'control',
               'проставлена стадия control')
        tap.eq(order.vars['suggests_write_off'],
               False,
               'саджесты на списание не сгенерированы')

        tap.ok(
            await order.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )

        await order.reload()
        tap.eq(order.vars['stage'], 'trash', 'проставлена стадия')

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )
        await order.reload()
        tap.eq(order.vars['suggests_write_off'], True, 'саджесты сгенерированы')

        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user,
            )

        tap.eq(len(order.problems), 0, 'Нет проблем')

        with await stock1.reload() as stock:
            tap.eq(stock.count, 0, 'Все списано')

        with await stock2.reload() as stock:
            tap.eq(stock.count, 0, 'Все списано')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=trash.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks), 0, 'На полке списания ничего нет')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=mark.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks), 2, 'Перемещено на полку уценки')

        stocks = dict((x.lot, x) for x in stocks)

        with stocks[f'{stock1.lot}:{stock1.shelf_id}'] as stock:
            tap.eq(stock.count, 7, 'партия на уценке')

        with stocks[f'{stock2.lot}:{stock2.shelf_id}'] as stock:
            tap.eq(stock.count, 3, 'партия на уценке')


async def test_markdown2trash(
        tap,
        uuid,
        dataset,
        now,
        wait_order_status,
):
    with tap.plan(17, 'Полный цикл перемещения на полку списания'):

        product1 = await dataset.product(valid=10)
        product2 = await dataset.product(valid=10, write_off_before=1)

        assortment = await dataset.assortment()
        await dataset.assortment_product(
            assortment=assortment, product=product2)

        store = await dataset.store(markdown_assortment=assortment)
        user  = await dataset.user(store=store)

        shelf  = await dataset.shelf(store=store, type='store', order=1)
        trash  = await dataset.shelf(store=store, type='trash', order=3)
        mark   = await dataset.shelf(store=store, type='markdown', order=4)
        repacking = await dataset.shelf(store=store, type='repacking', order=5)

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product1,
            count=7,
            valid='2020-01-01',
            lot=uuid(),
        )

        stock2 = await dataset.stock(
            store=store,
            shelf=mark,
            product=product2,
            count=3,
            valid='2020-01-01',
            lot=uuid(),
        )

        stock3 = await dataset.stock(
            store=store,
            shelf=repacking,
            product=product2,
            count=3,
            valid='2020-01-01',
            lot=uuid(),
        )

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='reserving',
            estatus='begin',
            accepted=now(),
            acks=[user.user_id],
            vars={'mode': 'markdown2trash'},
        )

        await wait_order_status(
            order,
            ('processing', 'reserve_online'),
            user_done=user,
        )
        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )
        await order.reload()
        tap.eq(order.vars['stage'],
               'control',
               'проставлена стадия control')
        tap.eq(order.vars['suggests_write_off'],
               False,
               'саджесты на списание не сгенерированы')

        tap.ok(
            await order.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )

        await order.reload()
        tap.eq(order.vars['stage'], 'trash', 'проставлена стадия')

        await wait_order_status(
            order,
            ('processing', 'waiting'),
            user_done=user,
        )
        await order.reload()
        tap.eq(order.vars['suggests_write_off'], True, 'саджесты сгенерированы')

        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user,
        )
        tap.eq(len(order.problems), 0, 'Нет проблем')

        with await stock1.reload() as stock:
            tap.eq(stock.count, 0, f'Все списано {stock.shelf_type}')

        with await stock2.reload() as stock:
            tap.eq(stock.count, 0, f'Все списано {stock.shelf_type}')

        with await stock3.reload() as stock:
            tap.eq(stock.count, 0, f'Все списано {stock.shelf_type}')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=trash.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks), 3, 'Перемещено на полку списания')

        stocks = dict((x.lot, x) for x in stocks)

        with stocks[f'{stock1.lot}:{stock1.shelf_id}'] as stock:
            tap.eq(stock.count, 7, 'партия на уценке')

        with stocks[f'{stock2.lot}:{stock2.shelf_id}'] as stock:
            tap.eq(stock.count, 3, 'партия на уценке')
