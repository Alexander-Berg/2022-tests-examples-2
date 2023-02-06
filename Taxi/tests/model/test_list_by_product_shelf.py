async def test_list(tap, dataset):
    with tap.plan(9):
        product = await dataset.product()
        tap.ok(product, 'товар создан')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        stock1 = await dataset.stock(store=store, product=product)
        tap.eq(stock1.store_id, store.store_id, 'остаток на полке 1 создан')
        tap.eq(stock1.product_id, product.product_id, 'товар')

        stock2 = await dataset.stock(store=store, product=product)
        tap.eq(stock2.store_id, store.store_id, 'остаток на полке 2 создан')
        tap.eq(stock2.product_id, product.product_id, 'товар')

        tap.ne(stock2.shelf_id, stock1.shelf_id, 'разные полки')


        stocks = await dataset.Stock.list_by_product(
            shelf_id=stock2.shelf_id,
            product_id=product.product_id,
            store_id=store.store_id,
        )
        tap.eq(len(stocks), 1, 'получен один остаток')
        with stocks[0] as s:
            tap.eq(s.stock_id, stock2.stock_id, 'это ожидаемый остаток')
