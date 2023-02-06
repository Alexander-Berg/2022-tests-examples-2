from stall.model.shelf import (
    SHELF_TYPES_VIRTUAL
)


# pylint: disable=too-many-statements,too-many-locals,too-many-branches
async def test_final_inventory(tap, dataset, wait_order_status):
    with tap.plan(7, 'Финальная инвентаризация'):
        store = await dataset.store(estatus='inventory')

        for shelf_type in SHELF_TYPES_VIRTUAL:
            virtual_shelf = await dataset.shelf(
                store=store,
                type=shelf_type,
            )
            await dataset.stock(
                store=store,
                shelf=virtual_shelf,
                count=5
            )

        usual_shelves = [await dataset.shelf(
            store=store, type='store'
        ) for _ in range(10)]

        for shelf in usual_shelves:
            for _ in range(10):
                await dataset.stock(
                    store=store,
                    shelf=shelf,
                    count=0
                )

        order = await dataset.order(
            store=store,
            type='inventory',
            status='reserving',
            vars={'final_inventory': True}
        )

        await wait_order_status(order, ('complete', 'done'))

        snapshot = await dataset.InventoryRecord.list(
            by='full',
            conditions=[('order_id', order.order_id)],
        )
        tap.eq(snapshot.list, [], 'Нет snapshot')

        async for stock in dataset.Stock.ilist(
                by='look',
                conditions=[
                    ('store_id', order.store_id),
                    ('shelf_type', SHELF_TYPES_VIRTUAL),
                ]
        ):
            tap.eq(stock.count, 0, 'Проверка остатка на виртуальной полке')

        await store.reload()

        tap.eq(store.status, 'closed', 'Склад закрыт')


# pylint: disable=too-many-statements,too-many-locals,too-many-branches
async def test_have_stock(tap, dataset, wait_order_status):
    with tap.plan(14, 'На полках есть остатки'):
        store = await dataset.store(estatus='inventory')

        lost_shelf = await dataset.shelf(
            store=store,
            type='lost',
        )
        await dataset.stock(
            store=store,
            shelf=lost_shelf,
            count=5
        )

        usual_shelves = [await dataset.shelf(
            store=store, type='store'
        ) for _ in range(10)]

        for shelf_number in range(10):
            await dataset.stock(
                store=store,
                shelf=usual_shelves[shelf_number],
                count=0
            )

        stocks = []
        problems = set()

        for shelf_number in range(3, 6):
            stock = await dataset.stock(
                store=store,
                shelf=usual_shelves[shelf_number],
                count=1
            )
            stocks.append(stock)
            problems.add(stock.shelf_id)

        order = await dataset.order(
            store=store,
            type='inventory',
            status='reserving',
            vars={'final_inventory': True}
        )

        await wait_order_status(order, ('failed', 'done'))

        tap.eq(
            len(order.problems), 3, 'Правильное количество проблем')

        tap.eq(
            problems,
            set(problem.shelf_id for problem in order.problems),
            'Правильные полки в проблемах'
        )

        tap.eq(store.status, 'active', 'Склад открыт')

        snapshot = await dataset.InventoryRecord.list(
            by='full',
            conditions=[('order_id', order.order_id)],
        )
        tap.eq(snapshot.list, [], 'Нет snapshot')

        for stock in stocks:
            await stock.do_reserve(
                order=order, count=stock.count)
            result = await stock.do_write_off(
                order=order,
                count=stock.count
            )
            tap.ok(result, 'списали остаток')

        new_order = await dataset.order(
            store=store,
            type='inventory',
            status='reserving',
            vars={'final_inventory': True}
        )

        await wait_order_status(new_order, ('complete', 'done'))

        tap.eq(len(new_order.problems), 0, 'проблем не обнаружено')

        snapshot = await dataset.InventoryRecord.list(
            by='full',
            conditions=[('order_id', new_order.order_id)],
        )
        tap.eq(snapshot.list, [], 'Нет snapshot')

        async for stock in dataset.Stock.ilist(
                by='look',
                conditions=[
                    ('store_id', order.store_id),
                    ('shelf_type', SHELF_TYPES_VIRTUAL),
                ]
        ):
            tap.eq(stock.count, 0, 'Проверка остатка на виртуальной полке')

        await store.reload()

        tap.eq(store.status, 'closed', 'Склад закрыт')
        tap.eq(store.estatus, 'inventory', 'Правильный estatus')
