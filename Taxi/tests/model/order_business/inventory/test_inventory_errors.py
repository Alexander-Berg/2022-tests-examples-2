import pytest


async def test_failed_not_inventory(tap, dataset, wait_order_status):
    with tap.plan(4, 'склад не инвентаризируется'):
        order = await dataset.order(type='inventory', status='reserving')
        tap.eq(order.fstatus,
               ('reserving', 'begin'), 'ордер инвентаризации создан')
        await wait_order_status(order, ('failed', 'done'))

        tap.eq(len(order.problems), 1, 'одна проблема')
        tap.eq(order.problems[0].type,
               'store_is_not_inventory',
               'не инвентаризируется')


@pytest.mark.parametrize('shelf_type', [
    'store',  # реальная полка
    'found',  # виртуальная
])
async def test_failed_nonzero_reserves(
        tap, dataset, wait_order_status, shelf_type):
    with tap.plan(9, 'есть резервы на складе'):
        store = await dataset.store(estatus='inventory')
        tap.eq(store.estatus, 'inventory', 'склад создан')

        order = await dataset.order(
            store=store,
            type='inventory',
            status='reserving'
        )
        tap.eq(order.fstatus,
               ('reserving', 'begin'), 'ордер инвентаризации создан')

        stock = await dataset.stock(
            store_id=order.store_id,
            reserve=1,
            shelf_type=shelf_type
        )
        tap.eq(stock.store_id, order.store_id, 'остаток создан')
        tap.ok(stock.reserve, 'резерв есть')

        await wait_order_status(order, ('failed', 'done'))

        tap.eq(len(order.problems), 1, 'одна проблема')
        with order.problems[0] as p:
            tap.eq(p.type, 'product_reserved', 'есть резервы')
            tap.eq(p.product_id, stock.product_id, 'товар')
            tap.eq(p.reserve, stock.reserve, 'количество резерва')


async def test_nosheves(tap, dataset, wait_order_status):
    with tap.plan(6, 'нет полок на складе'):
        store = await dataset.store(estatus='inventory')
        tap.eq(store.estatus, 'inventory', 'склад создан')

        shelf = await dataset.shelf(store=store, status='disabled')
        tap.eq(shelf.store_id, store.store_id, 'полка создана')
        tap.ne(shelf.status, 'active', 'не активна')

        order = await dataset.order(
            store=store,
            type='inventory',
            status='reserving'
        )
        tap.eq(order.fstatus,
               ('reserving', 'begin'), 'ордер инвентаризации создан')

        await wait_order_status(order, ('complete', 'done'))
        tap.eq(order.vars('child_orders'), [], 'пустой список дочерних ордеров')
