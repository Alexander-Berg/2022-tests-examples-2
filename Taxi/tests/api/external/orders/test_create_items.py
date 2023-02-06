async def test_create(tap, dataset, uuid, api):
    with tap.plan(12, 'Создание ордера с экземплярами'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')

        product = await dataset.product()
        tap.ok(product, 'товар создан')

        t = await api(role='token:web.external.tokens.0')

        external_id = uuid()

        await t.post_ok('api_external_orders_create',
                        json={
                            'external_id': external_id,
                            'required': [
                                {
                                    'product_id': product.product_id,
                                    'count': 123,
                                },
                                {
                                    'item_id': item.item_id,
                                }
                            ],
                            'store_id': store.store_id
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('order.external_id', external_id)
        t.json_is('order.store_id', store.store_id)

        order = await dataset.Order.load([store.store_id, external_id],
                                         by='conflict')
        tap.ok(order, 'ордер загружен')

        with next(r for r in order.required if r.item_id) as r:
            tap.ok(r, 'required про item')
            tap.eq(r.item_id, item.item_id, 'item_id')
            tap.eq(r.count, 1, 'количество 1')
