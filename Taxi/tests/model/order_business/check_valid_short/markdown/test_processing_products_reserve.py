# pylint: disable=too-many-locals,unused-variable

from datetime import timedelta


async def test_write_off(tap, uuid, now, dataset, wait_order_status):
    with tap.plan(
            14,
            'Проверяем что просрочка с markdown списывается после истечения'
            ' срока годности'
    ):

        product = await dataset.product(valid=10, write_off_before=5)
        assortment = await dataset.assortment()
        await dataset.assortment_product(assortment=assortment, product=product)

        store = await dataset.store(markdown_assortment=assortment)
        user  = await dataset.user(store=store)

        shelf       = await dataset.shelf(store=store, type='store')
        trash       = await dataset.shelf(store=store, type='trash')
        markdown    = await dataset.shelf(store=store, type='markdown')

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=10,
            valid=now() + timedelta(days=2),
            lot=uuid(),
        )

        order1 = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='reserving',
            estatus='begin',
            accepted=now(),
            acks=[user.user_id],
            vars={'mode': 'store2markdown'},
        )

        await wait_order_status(
            order1,
            ('processing', 'reserve_online'),
            user_done=user,
        )
        await wait_order_status(
            order1,
            ('processing', 'waiting'),
            user_done=user,
        )

        tap.ok(
            await order1.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(order1, ('complete', 'done'), user_done=user)

        with await stock1.reload() as stock:
            tap.eq(stock.count, 0, 'Все списано')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=markdown.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks), 1, 'Перемещено на уценку')
        stock2 = stocks[0]

        with stock2 as stock:
            tap.eq(stock.count, 10, 'Все уценено')
            tap.eq(stock.product_id, product.product_id, 'product_id')

        order2 = await dataset.order(
            store=store,
            type='check_valid_short',
            status='reserving',
            estatus='begin',
            accepted=now(),
            acks=[user.user_id],
            vars={'mode': 'markdown2trash'},
        )

        await wait_order_status(
            order2,
            ('processing', 'waiting'),
            user_done=user,
        )

        tap.ok(
            await order2.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(order2, ('complete', 'done'), user_done=user)

        with await stock2.reload() as stock:
            tap.eq(stock.count, 10, 'Списания не было')
            tap.eq(stock.reserve, 0, 'Не резервировалось')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=trash.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks), 0, 'Полка списаний пуста')


async def test_store2trash(tap, uuid, now, dataset, wait_order_status):
    with tap.plan(
            13,
            'Проверяем что просрочка из ассортимента распродажи списывается'
            ' если она не подходит под уценку'
    ):

        product = await dataset.product(valid=10, write_off_before=0)
        assortment = await dataset.assortment()
        await dataset.assortment_product(assortment=assortment, product=product)

        store = await dataset.store(markdown_assortment=assortment)
        user  = await dataset.user(store=store)

        shelf       = await dataset.shelf(store=store, type='store')
        trash       = await dataset.shelf(store=store, type='trash')
        markdown    = await dataset.shelf(store=store, type='markdown')

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=10,
            valid='2021-01-01',
            lot=uuid(),
        )

        order1 = await dataset.order(
            store=store,
            type='check_valid_short',
            status='reserving',
            estatus='begin',
            accepted=now(),
            acks=[user.user_id],
            vars={'mode': 'store2markdown'},
        )


        await wait_order_status(
            order1,
            ('processing', 'waiting'),
            user_done=user,
        )

        tap.ok(
            await order1.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(order1, ('complete', 'done'), user_done=user)

        with await stock1.reload() as stock:
            tap.eq(stock.count, 10, 'Списания не было')
            tap.eq(stock.reserve, 0, 'Не резервировалось')

        order2 = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='reserving',
            estatus='begin',
            accepted=now(),
            acks=[user.user_id],
            vars={'mode': 'markdown2trash'},
        )

        await wait_order_status(
            order2,
            ('processing', 'reserve_online'),
            user_done=user,
        )

        await wait_order_status(
            order2,
            ('processing', 'waiting'),
            user_done=user,
        )

        tap.ok(
            await order2.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(order2, ('complete', 'done'), user_done=user)

        with await stock1.reload() as stock:
            tap.eq(stock.count, 0, 'Все списано')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=trash.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks), 1, 'Полка списаний')

        with stocks[0] as stock:
            tap.eq(len(stock.vars['reasons']), 1, 'Записана причина')
            tap.eq(
                stock.vars['reasons'][0][order2.order_id]['reason_code'],
                'TRASH_TTL',
                'Код записан'
            )

async def test_markdown2trash(tap, uuid, now, dataset, wait_order_status):
    with tap.plan(
            13,
            'Проверяем что просрочка не из ассортимента распродажи списывается'
    ):

        product = await dataset.product(valid=10, write_off_before=0)
        assortment = await dataset.assortment()

        store = await dataset.store(markdown_assortment=assortment)
        user  = await dataset.user(store=store)

        shelf       = await dataset.shelf(store=store, type='store')
        trash       = await dataset.shelf(store=store, type='trash')
        markdown    = await dataset.shelf(store=store, type='markdown')

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
            count=10,
            valid='2021-01-01',
            lot=uuid(),
        )

        order1 = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='reserving',
            estatus='begin',
            accepted=now(),
            acks=[user.user_id],
            vars={'mode': 'store2markdown'},
        )

        await wait_order_status(
            order1,
            ('processing', 'waiting'),
            user_done=user,
        )

        tap.ok(
            await order1.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(order1, ('complete', 'done'), user_done=user)

        with await stock1.reload() as stock:
            tap.eq(stock.count, 10, 'Списания не было')
            tap.eq(stock.reserve, 0, 'Не резервировалось')

        order2 = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='reserving',
            estatus='begin',
            accepted=now(),
            acks=[user.user_id],
            vars={'mode': 'markdown2trash'},
        )
        await wait_order_status(
            order2,
            ('processing', 'reserve_online'),
            user_done=user,
        )

        await wait_order_status(
            order2,
            ('processing', 'waiting'),
            user_done=user,
        )

        tap.ok(
            await order2.signal({'type': 'next_stage'}),
            'сигнал next_stage'
        )

        await wait_order_status(order2, ('complete', 'done'), user_done=user)

        with await stock1.reload() as stock:
            tap.eq(stock.count, 0, 'Все списано')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=trash.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks), 1, 'Полка списаний')
        with stocks[0] as stock:
            tap.eq(len(stock.vars['reasons']), 1, 'Записана причина')
            tap.eq(
                stock.vars['reasons'][0][order2.order_id]['reason_code'],
                'TRASH_TTL',
                'Код записан'
            )
