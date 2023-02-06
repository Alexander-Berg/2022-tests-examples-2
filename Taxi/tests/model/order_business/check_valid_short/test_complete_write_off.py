# pylint: disable=too-many-locals,too-many-statements

from datetime import date, timedelta
from stall.model.suggest import Suggest

async def test_complete(tap, dataset, now, uuid, wait_order_status):
    with tap.plan(24, 'Проверяем что все удачно завершится'):

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
            valid=date(2020, 1, 1),  # Просрочен
            lot=uuid(),
            lot_price=101,
        )
        stock2 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
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
        tap.eq(
            order.signals[order.vars['signo']].type,
            'next_stage',
            'сигнал next_stage'
        )
        tap.ok(
            order.signals[order.vars['signo']].done is not None,
            'сигнал закрыт'
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

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks), 2, 'Остатки на полке склада')
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


async def test_repeat(tap, dataset, now, uuid, wait_order_status):
    with tap.plan(30, 'Проверяем повторную обработку списаний'):
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
            valid=date(2020, 1, 1),  # Просрочен
            lot=uuid(),
            lot_price=101,
        )
        stock2 = await dataset.stock(
            store=store,
            shelf=shelf,
            product=product,
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

        await wait_order_status(
            order,
            ('complete', 'write_off'),
            user_done=user,
        )
        await order.business.order_changed()

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks), 2, 'Остатки на полке склада')
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
            tap.eq(stock.reserve, 10, 'reserve')
            tap.eq(
                stock.lot,
                f'{stock1.lot}:{shelf.shelf_id}',
                'К партии добавлена полка откуда списывали'
            )
            tap.eq(stock.lot_price, 101, 'Цена')
            tap.eq(stock.valid, date(2020, 1, 1), 'Срок годности')

        order.estatus='write_off'
        tap.ok(await order.save(), 'Имитация ошибки сохранения статуса')

        await order.business.order_changed()

        stocks = await dataset.Stock.list_by_shelf(
            shelf_id=shelf.shelf_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks), 2, 'Остатки на полке склада')
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
            tap.eq(stock.reserve, 10, 'reserve')
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
