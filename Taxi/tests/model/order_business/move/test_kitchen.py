from stall.model.stock import Stock


# pylint: disable=too-many-locals
async def test_kitchen_to_trash(
        tap, dataset, uuid, wait_order_status,
):
    with tap.plan(
            11, 'при перемещении ПФ на треш не создаем фантомные остатки',
    ):
        product = await dataset.product(quants=330)

        store = await dataset.store()
        shelf_store = await dataset.shelf(type='store', store=store)
        shelf_components = await dataset.shelf(
            type='kitchen_components', store=store,
        )
        shelf_trash = await dataset.shelf(
            type='kitchen_trash', store=store,
        )

        stock1 = await dataset.stock(
            shelf=shelf_store, product=product, count=1, lot=uuid(),
        )
        stock2 = await dataset.stock(
            shelf=shelf_store, product=product, count=2, lot=uuid(),
        )
        tap.ok(stock1.shelf_id == stock2.shelf_id, 'товар на одной полке')
        tap.ok(stock1.lot != stock2.lot, 'из разных партий')

        move1 = await dataset.order(
            type='move',
            status='reserving',
            store=store,
            required=[
                {
                    'product_id': product.product_id,
                    'count': 3,
                    'src_shelf_id': shelf_store.shelf_id,
                    'dst_shelf_id': shelf_components.shelf_id,
                }
            ]
        )

        await wait_order_status(move1, ('complete', 'done'))

        stocks_store1 = await Stock.list_by_product(
            product_id=product.product_id,
            store_id=store.store_id,
            shelf_type=shelf_store.type,
            empty=False,
        )
        tap.eq(len(stocks_store1), 0, 'на обычных полках товара нет')

        stocks_kitchen1 = await Stock.list_by_product(
            product_id=product.product_id,
            store_id=store.store_id,
            shelf_type=shelf_components.type,
            empty=False,
        )
        tap.eq(len(stocks_kitchen1), 2, 'на полке компонент 2 партии')
        tap.eq(
            stocks_kitchen1[0].count + stocks_kitchen1[1].count,
            330 + 330 * 2,
            '3 пачки в квантах на полке ПФ',
        )

        product.quants = 300
        await product.save()
        tap.eq(product.quants, 300, 'сменили квант')

        move2 = await dataset.order(
            type='move',
            status='reserving',
            store=store,
            required=[
                {
                    'product_id': product.product_id,
                    'count': 300 * 3,
                    'src_shelf_id': shelf_components.shelf_id,
                    'dst_shelf_id': shelf_trash.shelf_id,
                }
            ]
        )

        await wait_order_status(move2, ('complete', 'done'))

        stocks_trash2 = await Stock.list_by_product(
            product_id=product.product_id,
            store_id=store.store_id,
            shelf_type=shelf_trash.type,
            empty=False,
        )
        tap.eq(len(stocks_trash2), 2, 'в треше 2 партии')
        tap.eq(
            sum(s.count for s in stocks_trash2),
            900,
            '900 квантов'
        )

        stocks_kitchen2 = await Stock.list_by_product(
            product_id=product.product_id,
            store_id=store.store_id,
            shelf_type=shelf_components.type,
            empty=False,
        )

        tap.eq(stocks_kitchen2[0].count, 990 - 900, 'остались ПФ')
