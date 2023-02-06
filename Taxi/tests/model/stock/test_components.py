import pytest


@pytest.mark.parametrize('method', ['do_put', 'do_write_in'])
async def test_components(tap, dataset, method, uuid):
    with tap.plan(18, f'работа с квантами компонент: {method}'):
        product = await dataset.product(quants=27)
        tap.eq(product.quants, 27, 'товар с квантами')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        shelf = await dataset.shelf(store=store)
        tap.eq(shelf.store_id, store.store_id, 'полка создана')

        kitchen_shelf = await dataset.shelf(
            store=store,
            type='kitchen_components',
        )
        tap.eq(kitchen_shelf.store_id,
               store.store_id,
               'полка с компонентами создана')
        tap.ok(kitchen_shelf.is_components, 'полка компонентная')


        order = await dataset.order(
            store=store,
            type='inventory_check_product_on_shelf'
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        do_action = getattr(dataset.Stock, method)

        stock = await do_action(
            order,
            shelf,
            product,
            count=123,
            lot = uuid(),
        )
        tap.eq(stock.store_id, store.store_id, 'остаток создан')
        tap.eq(stock.shelf_id, shelf.shelf_id, 'полка')
        tap.eq(stock.quants, 1, 'квантов нет')
        tap.eq(stock.count, 123, 'количество')


        stock = await do_action(
            order,
            kitchen_shelf,
            product,
            count=123,
            lot = uuid(),
        )
        tap.eq(stock.store_id, store.store_id, 'остаток создан')
        tap.eq(stock.quants, product.quants, 'кванты есть')
        tap.eq(stock.shelf_id, kitchen_shelf.shelf_id, 'полка')
        tap.eq(stock.count, 123, 'количество')


        stock = await do_action(
            order,
            kitchen_shelf,
            product,
            count=123,
            lot = uuid(),
            src_shelf=shelf,
        )
        tap.eq(stock.store_id, store.store_id, 'остаток создан')
        tap.eq(stock.quants, product.quants, 'кванты есть')
        tap.eq(stock.shelf_id, kitchen_shelf.shelf_id, 'полка')
        tap.eq(stock.count, 123 * product.quants, 'количество')
