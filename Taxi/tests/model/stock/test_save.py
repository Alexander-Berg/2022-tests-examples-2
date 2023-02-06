from stall.model.stock import Stock


async def test_direct_save(tap, dataset):
    '''Запрещено напрямую использовать save'''
    tap.plan(7)

    product = await dataset.product()
    tap.ok(product, 'продукт сгенерирован')

    store = await dataset.store()
    tap.ok(store, 'склад сгенерирован')

    shelf = await dataset.shelf(store_id=store.store_id)
    tap.ok(shelf, 'полка создана')
    tap.eq(shelf.store_id, store.store_id, 'На складе')

    stock = Stock({
        'product_id': product.product_id,
        'company_id': store.company_id,
        'store_id': store.store_id,
        'shelf_id': shelf.shelf_id,
        'shelf_type' : shelf.type
    })

    tap.ok(stock, 'инстанцирован')
    tap.eq(stock.stock_id, None, 'нет id')

    try:
        await stock.save()
    except RuntimeError as exc:
        tap.ok(exc, 'Напрямую записывать нельзя')

    tap()
