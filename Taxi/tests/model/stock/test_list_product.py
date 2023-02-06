# pylint: disable=invalid-name

from stall.model.stock import Stock


async def test_stock_product(tap, dataset):
    with tap.plan(6):
        products = [await dataset.product() for _ in range(5)]
        tap.ok(products, 'продукты сгенерированы')

        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        stocks = [await dataset.stock(store=store, product=p)
                  for p in products]

        tap.ok(stocks, 'остатки на складах сгенерированы')

        items = await Stock.list_by_product(product_id=products[0].product_id,
                                            store_id=store.store_id)

        tap.ok(items, 'список получен')
        tap.eq(len(items), 1, 'Один элемент в выдаче')
        tap.eq(items[0].stock_id,
               stocks[0].stock_id,
               'ожидаемый элемент')


async def test_stock_product_from_store_shelf(tap, dataset):
    with tap.plan(7):
        products = [await dataset.product() for _ in range(5)]
        tap.ok(products, 'продукты сгенерированы')

        store = await dataset.store()
        tap.ok(store, 'склад сгенерирован')

        stocks = []
        stocks.extend(
            [await dataset.stock(store=store, product=p) for p in products]
        )

        shelf = await dataset.shelf(store=store, type='incoming')
        tap.ok(shelf, 'полка in сгенерирована')

        stocks.extend(
            [await dataset.stock(store=store, product=p, shelf=shelf)
             for p in products]
        )

        tap.ok(stocks, 'остатки на складах сгенерированы')

        items = await Stock.list_by_product(
            product_id=products[0].product_id,
            store_id=store.store_id,
            shelf_type='store',
        )

        tap.ok(items, 'список получен')
        tap.eq(len(items), 1, 'Один элемент в выдаче')
        tap.eq(items[0].stock_id,
               stocks[0].stock_id,
               'ожидаемый элемент')


async def test_stock_empty(tap, dataset):
    with tap.plan(4):
        product1 = await dataset.product()
        product2 = await dataset.product()
        store   = await dataset.store()
        shelf   = await dataset.shelf(store=store)
        stock1  = await dataset.stock(shelf=shelf, product=product1, count=1)
        stock2  = await dataset.stock(shelf=shelf, product=product1, count=0)
        await dataset.stock(shelf=shelf, product=product2, count=3)
        await dataset.stock(shelf=shelf, product=product2, count=0)

        items = await Stock.list_by_product(
            product_id=product1.product_id,
            store_id=store.store_id,
        )
        tap.ok(items, 'список получен')
        tap.eq(
            set(x.stock_id for x in items),
            set((stock1.stock_id, stock2.stock_id)),
            'С нулями'
        )

        items2 = await Stock.list_by_product(
            product_id=product1.product_id,
            store_id=store.store_id,
            empty=False,
        )
        tap.ok(items2, 'список получен')
        tap.eq(
            set(x.stock_id for x in items),
            set((stock1.stock_id,)),
            'Без нулей'
        )
