# pylint: disable=too-many-locals, too-many-statements
import pytest

from stall.model.suggest import Suggest
from stall.model.stock import Stock


async def test_write_off(tap, uuid, dataset, wait_order_status, now):
    with tap.plan(20, 'Списание'):

        product1 = await dataset.product(valid=10)
        product2 = await dataset.product(valid=10)
        product3 = await dataset.product(valid=10)
        product4 = await dataset.product(valid=10, quants=11)

        store = await dataset.store()
        user  = await dataset.user(store=store)

        trash  = await dataset.shelf(store=store, type='trash')
        kitchen_trash = await dataset.shelf(store=store, type='kitchen_trash')

        stock1 = await dataset.stock(
            store=store,
            shelf=trash,
            product=product1,
            count=10,
            valid='2020-01-01',
            lot=uuid(),
            lot_price=101,
        )
        stock1_more = await dataset.stock(
            store=store,
            shelf=trash,
            product=product1,
            count=11,
            valid='2020-01-02',
            lot=uuid(),
        )
        stock2 = await dataset.stock(
            store=store,
            shelf=trash,
            product=product2,
            count=20,
            valid='2020-01-03',
            lot=uuid(),
        )
        stock3 = await dataset.stock(
            store=store,
            shelf=kitchen_trash,
            product=product3,
            count=30,
            valid='2020-01-04',
            lot=uuid(),
        )
        stock4 = await dataset.stock(
            store=store,
            shelf=trash,
            product=product4,
            count=40,
            valid='2020-01-05',
            lot=uuid(),
        )

        order = await dataset.order(
            store=store,
            type = 'writeoff',
            status='reserving',
            estatus='begin',
            target='complete',
            acks=[user.user_id],
            approved=now(),
        )

        await wait_order_status(
            order,
            ('processing', 'waiting')
        )

        suggests = await Suggest.list_by_order(order)
        suggests = dict((x.count, x) for x in suggests)

        with suggests[21] as suggest:
            tap.eq(suggest.status, 'request', 'request')
            tap.eq(suggest.product_id, product1.product_id, 'Продукт 1')
            tap.ok(
                await suggest.done('done', count=15),
                'Закрыли частично, но больше чем с одного остатка'
            )

        with suggests[20] as suggest:
            tap.eq(suggest.status, 'request', 'request')
            tap.eq(suggest.product_id, product2.product_id, 'Продукт 2')
            tap.ok(
                await suggest.done('done', count=2),
                'Закрыли как будто частично нашли'
            )

        with suggests[30] as suggest:
            tap.eq(suggest.status, 'request', 'Не будем закрывать')
            tap.eq(suggest.product_id, product3.product_id, 'Продукт 3')

        with suggests[40] as suggest:
            tap.eq(suggest.status, 'request', 'request')
            tap.eq(suggest.product_id, product4.product_id, 'Продукт 4')
            tap.ok(
                await suggest.done('done', count=0),
                'Закрыли как будто не нашли'
            )

        tap.ok(
            await order.done('complete', user=user),
            'Заказ выполнен'
        )

        await wait_order_status(
            order,
            ('complete', 'write_off'),
        )

        tap.ok(
            await order.business.order_changed(),
            'Списываем'
        )

        with await stock1.reload() as stock:
            tap.eq(stock.count, 0, 'Количество')
        with await stock1_more.reload() as stock:
            tap.eq(stock.count, 6, 'Количество')

        with await stock2.reload() as stock:
            tap.eq(stock.count, 18, 'Количество')

        with await stock3.reload() as stock:
            tap.eq(stock.count, 30, 'Количество')

        with await stock4.reload() as stock:
            tap.eq(stock.count, 40, 'Количество')


@pytest.mark.parametrize('write_off_count, expect_count', [
    (8, 0),
    (3, 5), # создается только один сток
    (4, 4)
])
async def test_write_off_with_reason(
        tap,
        dataset,
        uuid,
        wait_order_status,
        now,
        write_off_count,
        expect_count
):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)
        src_shelf = await dataset.shelf(store_id=store.store_id,
                                        type='store')
        stock = await dataset.stock(
            shelf=src_shelf,
            valid='2007-10-11',
        )
        tap.ok(stock, 'остаток создан')

        stock2 = await dataset.stock(
            store_id=stock.store_id,
            shelf_id=stock.shelf_id,
            product_id=stock.product_id,
            lot=uuid(),
            valid='2007-10-12',
        )
        tap.eq(stock2.product_id, stock.product_id, 'остаток 2 создан')
        tap.eq(stock2.shelf_id, stock.shelf_id, 'полка')
        tap.eq(stock2.store_id, stock.store_id, 'склад')
        tap.ne(stock2.stock_id, stock.stock_id, 'другой остаток')

        shelf = await dataset.shelf(store_id=stock.store_id,
                                    type='trash')
        tap.eq(shelf.store_id, stock.store_id, 'полка создана')

        # Первое перемещение
        order = await dataset.order(
            type='move',
            status='reserving',
            estatus='begin',
            store_id=stock.store_id,
            user_id=user.user_id,
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 3,
                    'src_shelf_id': stock.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                    'reason_code': 'TRASH_TTL',
                }
            ]
        )
        tap.eq(order.store_id, stock2.store_id, 'ордер создан')

        await wait_order_status(order, ('complete', 'done'))

        # Второе перемещение
        order = await dataset.order(
            type='move',
            status='reserving',
            estatus='begin',
            store_id=stock.store_id,
            user_id=user.user_id,
            required=[
                {
                    'product_id': stock.product_id,
                    'count': 5,
                    'src_shelf_id': stock.shelf_id,
                    'dst_shelf_id': shelf.shelf_id,
                    'reason_code': 'TRASH_DAMAGE',
                }
            ]
        )
        await wait_order_status(order, ('complete', 'done'))
        stocks = [
            s for s in await Stock.list_by_product(
                product_id=stock.product_id,
                store_id=stock.store_id,
                shelf_type='trash',
            ) if s.count
        ]

        tap.eq(len(stocks), 1, 'получился 1 сток')
        tap.eq(len(stocks[0].vars['reasons']), 2, 'добавлен reason')

        order = await dataset.order(
            store_id=stock.store_id,
            type='writeoff',
            status='reserving',
            estatus='begin',
            target='complete',
            acks=[user.user_id],
            approved=now(),
        )

        await wait_order_status(
            order,
            ('processing', 'waiting')
        )

        suggests = await Suggest.list_by_order(order)
        suggests = dict((x.count, x) for x in suggests)

        with suggests[8] as suggest:
            tap.eq(suggest.status, 'request', 'request')
            tap.eq(suggest.product_id, stock.product_id, 'Продукт 1')
            tap.ok(
                await suggest.done('done', count=write_off_count),
                'Закрыли'
            )

        tap.ok(
            await order.done('complete', user=user),
            'Заказ выполнен'
        )

        await wait_order_status(
            order,
            ('complete', 'write_off'),
        )

        tap.ok(
            await order.business.order_changed(),
            'Списываем'
        )

        with await stocks[0].reload() as stock:
            tap.eq(stock.count, expect_count, 'Количество')

        logs = (await stocks[0].list_log()).list
        # для последнего смотрим что все удалилось ок
        with logs[-1] as log:
            tap.eq(log.type, 'write_off', f'log type={log.type}')
            tap.eq(log.count, stocks[0].count, f'log count={log.count}')
            tap.eq(log.reserve, stocks[0].reserve, f'log reserve={log.reserve}')
            tap.ne(log.vars['reasons'], None, "Проставился reason")
            tap.ne(log.vars['write_off'], None, "Проставился write_off")


async def test_write_off_again(tap, dataset, uuid, now, wait_order_status):
    with tap.plan(14, 'Списание после неудачи'):
        product1 = await dataset.product(valid=10)
        product2 = await dataset.product(valid=10)
        product3 = await dataset.product(valid=10)
        product4 = await dataset.product(valid=10)

        store = await dataset.store()
        user = await dataset.user(store=store)

        trash = await dataset.shelf(store=store, type='trash')

        stock1 = await dataset.stock(
            store=store,
            shelf=trash,
            product=product1,
            count=3,
            valid='2020-01-01',
            lot=uuid(),
            lot_price=101,
        )
        stock1_more = await dataset.stock(
            store=store,
            shelf=trash,
            product=product1,
            count=5,
            valid='2020-01-02',
            lot=uuid(),
        )
        stock2 = await dataset.stock(
            store=store,
            shelf=trash,
            product=product2,
            count=11,
            valid='2020-01-03',
            lot=uuid(),
        )
        stock3 = await dataset.stock(
            store=store,
            shelf=trash,
            product=product3,
            count=13,
            valid='2020-01-04',
            lot=uuid(),
        )
        stock4 = await dataset.stock(
            store=store,
            shelf=trash,
            product=product4,
            count=40,
            valid='2020-01-05',
            lot=uuid(),
        )

        order = await dataset.order(
            store=store,
            type='writeoff',
            status='reserving',
            estatus='begin',
            target='complete',
            acks=[user.user_id],
            approved=now(),
        )

        await wait_order_status(
            order,
            ('processing', 'waiting')
        )

        suggests = await Suggest.list_by_order(order)
        suggests = dict((x.count, x) for x in suggests)

        tap.ok(
            await suggests[8].done('done', count=6),
            'Закрыли частично, но больше чем с одного остатка'
        )
        tap.ok(
            await suggests[11].done('done', count=11),
            'Закрыли целиком'
        )
        tap.ok(
            await suggests[13].done('done', count=6),
            'Частично закрыли'
        )
        tap.ok(
            await order.done('complete', user=user),
            'Заказ выполнен'
        )
        await wait_order_status(
            order,
            ('complete', 'write_off'),
        )

        tap.ok(
            await stock1.do_write_off(order, 3),
            'В первой итерации списали один из стоков',
        )
        tap.ok(
            await stock2.do_write_off(order, 11),
            'В первой итерации успели списать целиком',
        )
        tap.ok(
            await order.business.order_changed(),
            'Вторая итерация'
        )

        with await stock1.reload() as stock:
            tap.eq(stock.count, 0, 'Количество')
        with await stock1_more.reload() as stock:
            tap.eq(stock.count, 2, 'Количество')
        with await stock2.reload() as stock:
            tap.eq(stock.count, 0, 'Количество')
        with await stock3.reload() as stock:
            tap.eq(stock.count, 7, 'Количество')
        with await stock4.reload() as stock:
            tap.eq(stock.count, 40, 'Количество')
