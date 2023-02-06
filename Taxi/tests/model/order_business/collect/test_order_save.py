async def test_save(tap, dataset, wait_order_status):
    with tap.plan(4, 'сохранение/переход по статусам'):
        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        product = await dataset.product()
        tap.ok(product, 'товар')

        order = await dataset.order(
            store=store,
            type='collect',
            product=[
                {
                    'product_id': product.product_id,
                    'count': 27,
                }
            ],
        )
        tap.eq(order.store_id, store.store_id, 'ордер создан')

        await wait_order_status(order, ('processing', 'begin'))
