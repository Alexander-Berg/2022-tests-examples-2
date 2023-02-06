async def test_create_item_only(tap, dataset, api, uuid):
    with tap.plan(16, 'создание приёмки с экземплярами'):
        external_id = uuid()

        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'запись об экземпляре создана')

        t = await api(role='token:web.external.tokens.0')

        await t.post_ok('api_integration_orders_create',
                        json={
                            'external_id': external_id,
                            'store_id': store.store_id,
                            'type': 'acceptance',
                            'required': [
                                {
                                    'item_id': item.item_id,
                                },
                            ],
                            'attr': {
                                'doc_number': '700303-000001',
                                'doc_date': '1970-03-03',
                                'contractor': 'some_contractor',
                            }
                        })

        t.status_is(200, diag=True)

        t.json_has('order.external_id')
        t.json_has('order.order_id')
        t.json_has('order.required.0')
        t.json_hasnt('order.required.1')
        t.json_is('order.status', 'reserving')
        t.json_is('order.required.0.item_id', item.item_id)
        t.json_is('order.required.0.count', 1)

        t.json_has('order.order_id')
        order_id = t.res['json']['order']['order_id']


        await t.post_ok('api_integration_orders_create',
                        json={
                            'external_id': external_id,
                            'store_id': store.store_id,
                            'type': 'acceptance',
                            'required': [
                                {
                                    'item_id': item.item_id,
                                },
                            ],
                            'attr': {
                                'doc_number': '700303-000001',
                                'doc_date': '1970-03-03',
                                'contractor': 'some_contractor',
                            },
                        },
                        desc='Идемпотентный запрос')

        t.status_is(200, diag=True)
        t.json_is('order.order_id', order_id)


async def test_create(tap, dataset, api, uuid):
    with tap.plan(20, 'создание приёмки с экземплярами'):
        external_id = uuid()
        product_one = await dataset.product()
        tap.ok(product_one, 'товар создан')

        product_two = await dataset.product()
        tap.ok(product_two, 'второй товар создан')

        store = await dataset.full_store()
        tap.ok(store, 'склад создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'экземпляр создан')

        item = await dataset.item(store=store)
        tap.eq(item.store_id, store.store_id, 'запись об экземпляре создана')

        t = await api(role='token:web.external.tokens.0')

        await t.post_ok('api_integration_orders_create',
                        json={
                            'external_id': external_id,
                            'store_id': store.store_id,
                            'type': 'acceptance',
                            'required': [
                                {
                                    'item_id': item.item_id,
                                },
                                {
                                    'product_id': product_one.product_id,
                                    'count': 22,
                                },
                                {
                                    'product_id': product_two.product_id,
                                    'weight': 9999
                                }
                            ],
                            'attr': {
                                'doc_number': '700303-000001',
                                'doc_date': '1970-03-03',
                                'contractor': 'some_contractor',
                            },
                        })

        t.status_is(200, diag=True)

        t.json_has('order.external_id')
        t.json_has('order.order_id')
        t.json_is('order.status', 'reserving')
        t.json_is('order.required.0.item_id', item.item_id)
        t.json_is('order.required.0.count', 1)

        t.json_is('order.required.1.product_id', product_one.product_id)
        t.json_is('order.required.1.count', 22)

        t.json_is('order.required.2.product_id', product_two.product_id)
        t.json_is('order.required.2.weight', 9999)

        t.json_has('order.order_id')
        order_id = t.res['json']['order']['order_id']

        await t.post_ok('api_integration_orders_create',
                        json={
                            'external_id': external_id,
                            'store_id': store.store_id,
                            'type': 'acceptance',
                            'required': [
                                {
                                    'item_id': item.item_id,
                                },
                                {
                                    'product_id': product_one.product_id,
                                    'count': 22,
                                },
                                {
                                    'product_id': product_two.product_id,
                                    'weight': 9999
                                }
                            ],
                            'attr': {
                                'doc_number': '700303-000001',
                                'doc_date': '1970-03-03',
                                'contractor': 'some_contractor',
                            }
                        },
                        desc='Идемпотентный запрос')

        t.status_is(200, diag=True)
        t.json_is('order.order_id', order_id)


async def test_create_shipment(tap, dataset, api, uuid):
    with tap.plan(16, 'создание отгрузки с экземплярами'):
        external_id = uuid()
        product = await dataset.product()

        store = await dataset.full_store()

        item1 = await dataset.item(store=store)
        item2 = await dataset.item(store=store)

        t = await api(role='token:web.external.tokens.0')

        await t.post_ok('api_integration_orders_create',
                        json={
                            'external_id': external_id,
                            'store_id': store.store_id,
                            'type': 'shipment',
                            'required': [
                                {
                                    'item_id': item1.item_id,
                                },
                                {
                                    'item_id': item2.item_id,
                                    'count': 1,
                                },
                                {
                                    'product_id': product.product_id,
                                    'count': 22,
                                },
                            ],
                            'attr': {
                                'doc_number': '700303-000001',
                                'doc_date': '1970-03-03',
                                'contractor': 'some_contractor',
                            }
                        })

        t.status_is(200, diag=True)

        t.json_has('order.external_id')
        t.json_has('order.order_id')
        t.json_has('order.required.0')
        t.json_has('order.required.1')
        t.json_has('order.required.2')
        t.json_hasnt('order.required.3')
        t.json_is('order.status', 'reserving')

        t.json_has('order.order_id')
        order_id = t.res['json']['order']['order_id']

        required = t.res['json']['order']['required']
        required_items = {
            r['item_id']: r for r in required if r.get('item_id')
        }
        tap.eq_ok(required_items[item1.item_id]['count'], 1, 'Item1 in order')
        tap.eq_ok(required_items[item2.item_id]['count'], 1, 'Item2 in order')

        required_products = {
            r['product_id']: r for r in required if r.get('product_id')
        }
        tap.eq_ok(required_products[product.product_id]['count'], 22,
                  'Product in order')

        await t.post_ok('api_integration_orders_create',
                        json={
                            'external_id': external_id,
                            'store_id': store.store_id,
                            'type': 'shipment',
                            'required': [
                                {
                                    'item_id': item1.item_id,
                                },
                                {
                                    'item_id': item2.item_id,
                                    'count': 1,
                                },
                                {
                                    'product_id': product.product_id,
                                    'count': 22,
                                },
                            ],
                            'attr': {
                                'doc_number': '700303-000001',
                                'doc_date': '1970-03-03',
                                'contractor': 'some_contractor',
                            },
                        },
                        desc='Идемпотентный запрос')

        t.status_is(200, diag=True)
        t.json_is('order.order_id', order_id)
