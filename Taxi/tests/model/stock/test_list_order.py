from stall.model.stock import Stock


async def test_stock_order(tap, dataset):
    with tap.plan(7):
        products = [await dataset.product() for _ in range(5)]
        tap.ok(products, 'продукты сгенерированы')

        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        order = await dataset.order(store_id=store.store_id)
        tap.ok(order, 'ордер сгенерирован')

        stocks = [await dataset.stock(store=store,
                                      product=p,
                                      order=order,
                                      reserve=10)
                  for p in products]

        tap.ok(stocks, 'остатки на складах сгенерированы')
        tap.eq(stocks[0].reserve, 10, 'есть резервы')

        items = await Stock.list_by_order(order)

        tap.ok(items, 'список получен')
        tap.eq(len(items), 5, 'Количество элементов в выдаче')




async def test_stock_order_by_product(tap, dataset):
    with tap.plan(8):
        products = [await dataset.product() for _ in range(5)]
        tap.ok(products, 'продукты сгенерированы')

        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        order = await dataset.order(store_id=store.store_id)
        tap.ok(order, 'ордер сгенерирован')

        stocks = [await dataset.stock(store=store,
                                      product=p,
                                      order=order,
                                      reserve=10)
                  for p in products]

        tap.ok(stocks, 'остатки на складах сгенерированы')
        tap.eq(stocks[0].reserve, 10, 'есть резервы')

        items = await Stock.list_by_order(order, products[2].product_id)

        tap.ok(items, 'список получен')
        tap.eq(len(items), 1, 'Количество элементов в выдаче')
        tap.eq(items[0].product_id, products[2].product_id,
               'Только нужный продукт')


