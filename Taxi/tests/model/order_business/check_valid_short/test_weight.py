# pylint: disable=too-many-locals,unused-variable
from datetime import date, timedelta
from stall.model.stock import Stock
from stall.model.suggest import Suggest


async def test_store2markdown(
        tap,
        uuid,
        dataset,
        now,
        wait_order_status,
):
    with tap.plan(17, 'Полный цикл перемещения на полку уценки вес товара'):

        parent = await dataset.weight_parent(
            valid=10,
            write_off_before=1
        )

        child_1 = await dataset.product(
            parent_id=parent.product_id,
            valid=10,
            write_off_before=1,
            lower_weight_limit=100,
            upper_weight_limit=200,
            type_accounting='weight',
        )
        child_2 = await dataset.product(
            parent_id=parent.product_id,
            valid=10,
            write_off_before=1,
            lower_weight_limit=200,
            upper_weight_limit=500,
            type_accounting='weight',
        )
        assortment = await dataset.assortment()
        await dataset.assortment_product(
            assortment=assortment,
            product=child_1
        )
        await dataset.assortment_product(
            assortment=assortment,
            product=child_2
        )

        store = await dataset.store(markdown_assortment=assortment)
        user  = await dataset.user(store=store)

        shelf  = await dataset.shelf(store=store, type='store', order=1)
        trash  = await dataset.shelf(store=store, type='trash', order=3)
        mark   = await dataset.shelf(store=store, type='markdown', order=4)

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=child_1,
            count=7,
            valid='2020-01-01',
            lot=uuid(),
        )

        stock2 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=child_2,
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
    with tap.plan(16, 'Полный цикл перемещения на полку списания'):
        parent = await dataset.weight_parent(
            valid=10,
            write_off_before=1
        )

        child_1 = await dataset.product(
            parent_id=parent.product_id,
            valid=10,
            write_off_before=1,
            lower_weight_limit=100,
            upper_weight_limit=200,
            type_accounting='weight',
        )
        child_2 = await dataset.product(
            parent_id=parent.product_id,
            valid=10,
            write_off_before=1,
            lower_weight_limit=200,
            upper_weight_limit=500,
            type_accounting='weight',
        )
        assortment = await dataset.assortment()
        await dataset.assortment_product(
            assortment=assortment,
            product=child_1
        )
        await dataset.assortment_product(
            assortment=assortment,
            product=child_2
        )

        store = await dataset.store(markdown_assortment=assortment)
        user  = await dataset.user(store=store)

        trash  = await dataset.shelf(store=store, type='trash', order=3)
        mark   = await dataset.shelf(store=store, type='markdown', order=4)

        stock1 = await dataset.stock(
            store=store,
            shelf=mark,
            product=child_1,
            count=7,
            valid='2020-01-01',
            lot=uuid(),
        )

        stock2 = await dataset.stock(
            store=store,
            shelf=mark,
            product=child_2,
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
            tap.eq(stock.count, 0,
                   f'Все списано со второго стока {stock.shelf_type}')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=trash.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks), 2, 'Перемещено на полку списания')

        stocks = dict((x.lot, x) for x in stocks)

        with stocks[f'{stock1.lot}:{stock1.shelf_id}'] as stock:
            tap.eq(stock.count, 7, 'партия на уценке')

        with stocks[f'{stock2.lot}:{stock2.shelf_id}'] as stock:
            tap.eq(stock.count, 3, 'партия на уценке')


async def test_complete(tap, dataset, now, uuid, wait_order_status):
    with tap.plan(22, 'Проверяем что все удачно завершится'):
        parent = await dataset.weight_parent(
            valid=10,
            write_off_before=1
        )

        child_1 = await dataset.product(
            parent_id=parent.product_id,
            valid=10,
            write_off_before=1,
            lower_weight_limit=100,
            upper_weight_limit=200,
            type_accounting='weight',
        )
        child_2 = await dataset.product(
            parent_id=parent.product_id,
            valid=10,
            write_off_before=1,
            lower_weight_limit=200,
            upper_weight_limit=500,
            type_accounting='weight',
        )
        assortment = await dataset.assortment()
        await dataset.assortment_product(
            assortment=assortment,
            product=child_1
        )
        await dataset.assortment_product(
            assortment=assortment,
            product=child_2
        )

        store = await dataset.store()
        user = await dataset.user(store=store)

        shelf = await dataset.shelf(store=store, type='store', order=1)
        shelf2 = await dataset.shelf(store=store, type='store', order=1)
        trash = await dataset.shelf(store=store, type='trash', order=2)

        stock1 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=child_1,
            count=10,
            valid=date(2020, 1, 1),  # Просрочен
            lot=uuid(),
            lot_price=101,
        )
        stock2 = await dataset.stock(
            store=store,
            shelf=shelf2,
            product=child_2,
            count=20,
            valid=now() + timedelta(days=100),  # Не просрочен
            lot=uuid(),
            lot_price=202,
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
            ('processing', 'reserve_online'),
            user_done=user,
        )
        await wait_order_status(
            order,
            ('processing', 'waiting'),
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

        suggests = await Suggest.list_by_order(order,
                                               status=['request'],
                                               types=['box2shelf'],
                                               )
        tap.eq(len(suggests), 0, 'ничего лишнего')

        stocks = await dataset.Stock.list_by_order(order)
        stocks = dict((x.stock_id, x) for x in stocks)
        with stocks[stock1.stock_id] as stock:
            tap.eq(stock.count, 10, 'count')
            tap.eq(stock.reserve, 10, 'reserve')
            tap.eq(stock.reserves[order.order_id], 10, 'reserves')

        await wait_order_status(order,
                                ('complete', 'done'),
                                user_done=user,
                                )

        stocks = await Stock.list(
            by='full',
            conditions=[
                ('store_id', store.store_id),
                ('shelf_id', [shelf.shelf_id, shelf2.shelf_id])
            ],
            sort=(),
        )
        tap.eq(len(stocks.list), 2, 'Остатки на полке склада')
        stocks = dict((x.stock_id, x) for x in stocks)
        with stocks[stock1.stock_id] as stock:
            tap.eq(stock.count, 0, 'count')
            tap.eq(stock.reserve, 0, 'reserve')
        with stocks[stock2.stock_id] as stock:
            tap.eq(stock.count, 20, 'count')
            tap.eq(stock.reserve, 0, 'reserve')

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=trash.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks), 1, 'Остатки на полке списания')
        with stocks[0] as stock:
            tap.eq(stock.count, 10, 'count')
            tap.eq(stock.reserve, 0, 'reserve')
            tap.eq(
                stock.lot,
                f'{stock1.lot}:{shelf.shelf_id}',
                'К партии добавлена полка откуда списывали'
            )
            tap.eq(stock.lot_price, 101, 'Цена')
            tap.eq(stock.valid, date(2020, 1, 1), 'Срок годности')
            tap.eq(len(stock.vars['reasons']), 1, 'Записана причина')
            tap.eq(
                stock.vars['reasons'][0][order.order_id]['reason_code'],
                'TRASH_TTL',
                'Код записан'
            )
