# pylint: disable=too-many-locals,too-many-statements,unused-variable

from datetime import timedelta

from libstall.util import now
from stall.model.stock import Stock
from stall.model.suggest import Suggest


async def test_multi_lots(tap, uuid, dataset, wait_order_status):
    with tap.plan(
            32,
            'Кучка лотов. Проверяем что остатки на разных полках'
            'не перетирают даные друг друга'
    ):

        product = await dataset.product(valid=10, write_off_before=9)
        assortment = await dataset.assortment()
        await dataset.assortment_product(assortment=assortment, product=product)

        store   = await dataset.store(markdown_assortment=assortment)
        user    = await dataset.user(store=store)

        shelf1 = await dataset.shelf(store=store, type='store', order=1)
        shelf2 = await dataset.shelf(store=store, type='store', order=2)

        trash  = await dataset.shelf(store=store, type='trash', order=3)
        markdown = await dataset.shelf(store=store, type='markdown', order=4)

        stock1_all = await dataset.stock(
            store=store,
            shelf=shelf1,
            product=product,
            count=10,
            reserve=0,
            valid=now().date() - timedelta(days=3),
            lot=uuid(),
        )
        tap.ok(stock1_all, 'Просроченный остаток на полке 1')

        stock1_part = await dataset.stock(
            store=store,
            shelf=shelf1,
            product=product,
            count=20,
            reserve=0,
            valid=now().date() - timedelta(days=2),
            lot=uuid(),
        )
        tap.ok(stock1_part, 'Частично просроченный остаток на полке 1')

        stock1_ok = await dataset.stock(
            store=store,
            shelf=shelf1,
            product=product,
            count=30,
            reserve=0,
            valid=now().date() + timedelta(days=10),
            lot=uuid(),
        )
        tap.ok(stock1_ok, 'Годный остаток на полке 1')

        stock2_all = await dataset.stock(
            store=store,
            shelf=shelf2,
            product=product,
            count=40,
            reserve=0,
            valid=now().date() - timedelta(days=3),
            lot=uuid(),
        )
        tap.ok(stock2_all, 'Просроченный остаток на полке 2')

        stock2_part = await dataset.stock(
            store=store,
            shelf=shelf2,
            product=product,
            count=50,
            reserve=0,
            valid=now().date() - timedelta(days=2),
            lot=uuid(),
        )
        tap.ok(stock2_part, 'Частично просроченный остаток на полке 2')

        stock2_ok = await dataset.stock(
            store=store,
            shelf=shelf2,
            product=product,
            count=60,
            reserve=0,
            valid=now().date() + timedelta(days=10),
            lot=uuid(),
        )
        tap.ok(stock2_ok, 'Годный остаток на полке 2')

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='reserving',
            estatus='begin',
            target='complete',
            approved=now(),
            acks=[user.user_id],
            vars={'mode': 'store2markdown'},
        )
        tap.ok(order, 'Заказ создан')

        await wait_order_status(order, ('processing', 'waiting'))

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 2, 'Саджесты 2 шт. агрегированы по полкам')
        suggests = dict(((x.shelf_id, x.count), x) for x in suggests)

        with shelf1 as shelf:
            with suggests[shelf.shelf_id, 10+20+30] as suggest:
                tap.ok(
                    await suggest.done(
                        'done',
                        count=10+2,
                        valid=now().date() + timedelta(days=9)
                    ),
                    'Закрыт с просрочкой'
                )

        with shelf2 as shelf:
            with suggests[shelf.shelf_id, 40+50+60] as suggest:
                tap.ok(
                    await suggest.done(
                        'done',
                        count=40+5,
                        valid=now().date() + timedelta(days=9)
                    ),
                    'Закрыт с просрочкой'
                )

        await wait_order_status(order, ('processing', 'waiting'))
        await wait_order_status(
            order, ('processing', 'waiting'), user_done=user)

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

        suggests = await Suggest.list_by_order(order)
        tap.eq(len(suggests), 4, 'Саджесты 2 на взятие и 2 на положить')
        suggests = dict(((x.shelf_id, x.count), x) for x in suggests)

        with shelf1 as shelf:
            with suggests[shelf.shelf_id, 10+20+30] as suggest1:
                tap.eq(suggest1.status, 'done', 'Уже выполнен')
                tap.eq(suggest1.result_count, 10+2, 'Частичное закрытие')

        with shelf2 as shelf:
            with suggests[shelf.shelf_id, 40+50+60] as suggest2:
                tap.eq(suggest2.status, 'done', 'Уже выполнен')
                tap.eq(suggest2.result_count, 40+5, 'Частичное закрытие')

        with markdown as shelf:
            with suggests[shelf.shelf_id, 10+2] as suggest:
                tap.eq(
                    suggest.vars['parent_id'],
                    suggest1.suggest_id,
                    'Связь с родителем сохранена'
                )
                tap.ok(await suggest.done('done'), 'Положили 1')

            with suggests[shelf.shelf_id, 40+5] as suggest:
                tap.eq(
                    suggest.vars['parent_id'],
                    suggest2.suggest_id,
                    'Связь с родителем сохранена'
                )
                tap.ok(await suggest.done('done'), 'Положили 2')

        await wait_order_status(
            order,
            ('complete', 'done'),
            user_done=user,
        )

        stocks_on_trash = await Stock.list_by_shelf(
            store_id=store.store_id,
            shelf_id=trash.shelf_id,
        )
        tap.eq(len(stocks_on_trash), 0, 'КСГ идет на полку уценки')

        stocks_on_markdown = await Stock.list_by_shelf(
            store_id=store.store_id,
            shelf_id=markdown.shelf_id,
        )
        tap.eq(len(stocks_on_markdown), 4, 'Списано на полку уценки')
        stocks = dict(((x.shelf_id, x.count), x) for x in stocks_on_markdown)

        with stocks[markdown.shelf_id, 10] as stock:
            tap.eq(
                stock.lot,
                f'{stock1_all.lot}:{stock1_all.shelf_id}',
                'Весь лот с полки 1'
            )

        with stocks[markdown.shelf_id, 2] as stock:
            tap.eq(
                stock.lot,
                f'{stock1_part.lot}:{stock1_part.shelf_id}',
                'Частичный лот с полки 1'
            )

        with stocks[markdown.shelf_id, 40] as stock:
            tap.eq(
                stock.lot,
                f'{stock2_all.lot}:{stock2_all.shelf_id}',
                'Весь лот с полки 2'
            )

        with stocks[markdown.shelf_id, 5] as stock:
            tap.eq(
                stock.lot,
                f'{stock2_part.lot}:{stock2_part.shelf_id}',
                'Частичный лот с полки 2'
            )
