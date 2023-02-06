from datetime import timedelta
from libstall.util import now


async def test_fix_valid(tap, uuid, dataset):
    with tap.plan(15, 'Корректировка срока годности'):

        product1 = await dataset.product(valid=10)

        store = await dataset.store()

        shelf1 = await dataset.shelf(store=store, type='store', order=1)

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='complete',
            estatus='fix_valid',
            target='complete',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'fix_valid', 'fix_valid')
        tap.eq(order.target, 'complete', 'target: complete')

        with product1 as product:
            date1 = (now() + timedelta(days=1)).date()
            stock1 = await dataset.stock(
                store=store,
                order=order,
                shelf=shelf1,
                product=product,
                count=3,
                reserve=3,
                valid=date1,
                lot=uuid(),
            )

            date2 = (now() + timedelta(days=30)).date()
            stock2 = await dataset.stock(
                store=store,
                order=order,
                shelf=shelf1,
                product=product,
                count=7,
                reserve=7,
                valid=date2,
                lot=uuid(),
            )

            suggest1 = await dataset.suggest(
                order,
                type='shelf2box',
                status='done',
                count=10,
                result_count=10,
                result_valid=now() + timedelta(days=7),
                shelf_id=shelf1.shelf_id,
                product_id=product.product_id,
            )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'check_recheck', 'check_recheck')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        # Остатки на складе
        with stock1 as stock:
            tap.ok(await stock.reload(), 'Остатки получены')
            tap.eq(stock.shelf_id, shelf1.shelf_id, 'Полка')
            tap.eq(stock.valid, suggest1.result_valid,
                   'Срок годности подвинули')

        with stock2 as stock:
            tap.ok(await stock.reload(), 'Остатки получены')
            tap.eq(stock.shelf_id, shelf1.shelf_id, 'Полка')
            tap.eq(stock.valid, date2, 'Срок годности не менялся')


async def test_none(tap, uuid, dataset):
    with tap.plan(12, 'Пользователь не указал срок годности'):

        product1 = await dataset.product(valid=10)

        store = await dataset.store()

        shelf1 = await dataset.shelf(store=store, type='store', order=1)

        order = await dataset.order(
            store=store,
            type = 'check_valid_short',
            status='complete',
            estatus='fix_valid',
            target='complete',
        )
        tap.ok(order, 'Заказ создан')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'fix_valid', 'fix_valid')
        tap.eq(order.target, 'complete', 'target: complete')

        with product1 as product:
            date1 = (now() + timedelta(days=1)).date()
            stock1 = await dataset.stock(
                store=store,
                order=order,
                shelf=shelf1,
                product=product,
                count=3,
                reserve=3,
                valid=date1,
                lot=uuid(),
            )

            await dataset.suggest(
                order,
                type='shelf2box',
                status='done',
                count=10,
                result_count=10,
                result_valid=None,
                shelf_id=shelf1.shelf_id,
                product_id=product.product_id,
            )

        await order.business.order_changed()

        tap.ok(await order.reload(), 'Перезабрали заказ')
        tap.eq(order.status, 'complete', 'complete')
        tap.eq(order.estatus, 'check_recheck', 'check_recheck')
        tap.eq(order.target, 'complete', 'target: complete')

        tap.eq(len(order.problems), 0, 'Нет проблем')

        # Остатки на складе
        with stock1 as stock:
            tap.ok(await stock.reload(), 'Остатки получены')
            tap.eq(stock.shelf_id, shelf1.shelf_id, 'Полка')
            tap.eq(stock.valid, date1, 'Срок годности не меняли')
