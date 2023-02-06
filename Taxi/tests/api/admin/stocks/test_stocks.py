async def test_product(api, tap, dataset):
    with tap.plan(20):
        t = await api(role='admin')
        store = await dataset.store()
        shelf1 = await dataset.shelf(store=store, type='store')
        shelf2 = await dataset.shelf(store=store, type='markdown')
        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        await dataset.stock(product=product1,
                            shelf=shelf1,
                            store=store,
                            lot='lot11', count=13, reserve=3)
        await dataset.stock(product=product2,
                            shelf=shelf1,
                            store=store,
                            lot='lot21', count=14, reserve=4)
        await dataset.stock(product=product3,
                            shelf=shelf1,
                            store=store, count=15, reserve=5)

        await dataset.stock(product=product1,
                            shelf=shelf2,
                            store=store, count=16, reserve=6)
        await dataset.stock(product=product2,
                            shelf=shelf2,
                            store=store, count=17, reserve=7)

        await dataset.stock(product=product1,
                            shelf=shelf1,
                            store=store,
                            lot='lot12', count=18, reserve=8)
        await dataset.stock(product=product2,
                            shelf=shelf1,
                            store=store,
                            lot='lot22', count=19, reserve=9)

        await t.post_ok('api_admin_stocks_product',
                        json={'store_id': store.store_id,
                              'product_id': product1.product_id})
        t.status_is(200, diag=True)
        t.json_has('stocks')
        shelves = t.res['json']['stocks']
        tap.eq_ok(
            {shelf['shelf_id']: shelf['count'] for shelf in shelves},
            {
                shelf1.shelf_id: 31,
                shelf2.shelf_id: 16,
            },
            'Правильно посчитаны остатки товара 1 на полках'
        )
        tap.eq_ok(
            {shelf['shelf_id']: shelf['reserve'] for shelf in shelves},
            {
                shelf1.shelf_id: 11,
                shelf2.shelf_id: 6,
            },
            'Правильно посчитаны резервы товара 1 на полках'
        )

        await t.post_ok('api_admin_stocks_product',
                        json={'store_id': store.store_id,
                              'product_id': product2.product_id})
        t.status_is(200, diag=True)
        t.json_has('stocks')
        shelves = t.res['json']['stocks']
        tap.eq_ok(
            {shelf['shelf_id']: shelf['count'] for shelf in shelves},
            {
                shelf1.shelf_id: 33,
                shelf2.shelf_id: 17,
            },
            'Правильно посчитаны остатки товара 2 на полках'
        )
        tap.eq_ok(
            {shelf['shelf_id']: shelf['reserve'] for shelf in shelves},
            {
                shelf1.shelf_id: 13,
                shelf2.shelf_id: 7,
            },
            'Правильно посчитаны резервы товара 2 на полках'
        )

        await t.post_ok('api_admin_stocks_product',
                        json={'store_id': store.store_id,
                              'product_id': product3.product_id})
        t.status_is(200, diag=True)
        t.json_has('stocks')
        shelves = t.res['json']['stocks']
        tap.eq_ok(
            {shelf['shelf_id']: shelf['count'] for shelf in shelves},
            {
                shelf1.shelf_id: 15,
            },
            'Правильно посчитаны остатки товара 3 на полках'
        )
        tap.eq_ok(
            {shelf['shelf_id']: shelf['reserve'] for shelf in shelves},
            {
                shelf1.shelf_id: 5,
            },
            'Правильно посчитаны резервы товара 3 на полках'
        )

        await t.post_ok('api_admin_stocks_product',
                        json={'store_id': store.store_id,
                              'product_id': [product1.product_id,
                                             product2.product_id,
                                             product3.product_id]})
        t.status_is(200, diag=True)
        t.json_has('stocks')
        shelves = t.res['json']['stocks']
        tap.eq_ok(
            {(shelf['shelf_id'], shelf['product_id']): shelf['count']
             for shelf in shelves},
            {
                (shelf1.shelf_id, product1.product_id): 31,
                (shelf2.shelf_id, product1.product_id): 16,
                (shelf1.shelf_id, product2.product_id): 33,
                (shelf2.shelf_id, product2.product_id): 17,
                (shelf1.shelf_id, product3.product_id): 15,
            },
            'Правильно посчитаны остатки товаров 1, 2 и 3 на полках'
        )
        tap.eq_ok(
            {(shelf['shelf_id'], shelf['product_id']): shelf['reserve']
             for shelf in shelves},
            {
                (shelf1.shelf_id, product1.product_id): 11,
                (shelf2.shelf_id, product1.product_id): 6,
                (shelf1.shelf_id, product2.product_id): 13,
                (shelf2.shelf_id, product2.product_id): 7,
                (shelf1.shelf_id, product3.product_id): 5,
            },
            'Правильно посчитаны резервы товаров 1, 2 и 3 на полках'
        )


async def test_shelf(api, tap, dataset):
    with tap.plan(15):
        store = await dataset.store()
        user = await dataset.user(store=store)
        t = await api(role='admin', user=user)
        shelf1 = await dataset.shelf(store=store, type='store')
        shelf2 = await dataset.shelf(store=store, type='store')
        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()

        await dataset.stock(product=product1,
                            shelf=shelf1,
                            store=store,
                            lot='lot11', count=13, reserve=3)
        await dataset.stock(product=product2,
                            shelf=shelf1,
                            store=store,
                            lot='lot21', count=14, reserve=4)
        await dataset.stock(product=product3,
                            shelf=shelf1,
                            store=store, count=15, reserve=5)

        await dataset.stock(product=product1,
                            shelf=shelf2,
                            store=store, count=16, reserve=6)
        await dataset.stock(product=product2,
                            shelf=shelf2,
                            store=store, count=17, reserve=7)

        await dataset.stock(product=product1,
                            shelf=shelf1,
                            store=store,
                            lot='lot12', count=18, reserve=8)
        await dataset.stock(product=product2,
                            shelf=shelf1,
                            store=store,
                            lot='lot22', count=19, reserve=9)

        await t.post_ok('api_admin_stocks_shelf',
                        json={'shelf_id': shelf1.shelf_id})
        t.status_is(200, diag=True)
        t.json_has('stocks')
        products = t.res['json']['stocks']
        tap.eq_ok(
            {product['product_id']: product['count'] for product in products},
            {
                product1.product_id: 31,
                product2.product_id: 33,
                product3.product_id: 15,
            },
            'Правильно посчитаны остатки товаров на полке 1'
        )
        tap.eq_ok(
            {p['product_id']: p['reserve'] for p in products},
            {
                product1.product_id: 11,
                product2.product_id: 13,
                product3.product_id: 5,
            },
            'Правильно посчитаны резервы товаров на полке 1'
        )

        await t.post_ok('api_admin_stocks_shelf',
                        json={'shelf_id': shelf2.shelf_id})
        t.status_is(200, diag=True)
        t.json_has('stocks')
        products = t.res['json']['stocks']
        tap.eq_ok(
            {product['product_id']: product['count'] for product in products},
            {
                product1.product_id: 16,
                product2.product_id: 17,
            },
            'Правильно посчитаны остатки товаров на полке 2'
        )
        tap.eq_ok(
            {p['product_id']: p['reserve'] for p in products},
            {
                product1.product_id: 6,
                product2.product_id: 7,
            },
            'Правильно посчитаны резервы товаров на полке 2'
        )

        await t.post_ok('api_admin_stocks_shelf',
                        json={'store_id': store.store_id,
                              'shelf_id': [shelf1.shelf_id,
                                           shelf2.shelf_id]})
        t.status_is(200, diag=True)
        t.json_has('stocks')
        shelves = t.res['json']['stocks']
        tap.eq_ok(
            {(shelf['shelf_id'], shelf['product_id']): shelf['count']
             for shelf in shelves},
            {
                (shelf1.shelf_id, product1.product_id): 31,
                (shelf1.shelf_id, product2.product_id): 33,
                (shelf1.shelf_id, product3.product_id): 15,
                (shelf2.shelf_id, product1.product_id): 16,
                (shelf2.shelf_id, product2.product_id): 17,
            },
            'Правильно посчитаны остатки товаров на полках 1 и 2'
        )
        tap.eq_ok(
            {(shelf['shelf_id'], shelf['product_id']): shelf['reserve']
             for shelf in shelves},
            {
                (shelf1.shelf_id, product1.product_id): 11,
                (shelf1.shelf_id, product2.product_id): 13,
                (shelf1.shelf_id, product3.product_id): 5,
                (shelf2.shelf_id, product1.product_id): 6,
                (shelf2.shelf_id, product2.product_id): 7,
            },
            'Правильно посчитаны резервы товаров на полках 1 и 2'
        )


# pylint: disable=too-many-locals
async def test_shelf_type(api, tap, dataset):
    with tap:
        store = await dataset.store()

        shelf1 = await dataset.shelf(store=store, type='store')
        shelf2 = await dataset.shelf(store=store, type='store')
        shelf3 = await dataset.shelf(store=store, type='parcel')
        shelf4 = await dataset.shelf(store=store, type='parcel')

        product = await dataset.product()
        item1 = await dataset.item()
        item2 = await dataset.item()

        await dataset.stock(product=product,
                            shelf=shelf1,
                            store=store, count=13, reserve=3)
        await dataset.stock(product=product,
                            shelf=shelf2,
                            store=store, count=14, reserve=3)
        await dataset.stock(product_id=item1.item_id,
                            shelf=shelf3,
                            store=store, count=1)
        await dataset.stock(product_id=item2.item_id,
                            shelf=shelf4,
                            store=store, count=1)

        user = await dataset.user(role='admin', store=store)
        t = await api(user=user)
        await t.post_ok('api_admin_stocks_shelf',
                        json={'store_id': store.store_id,
                              'shelf_id': [shelf1.shelf_id,
                                           shelf2.shelf_id,
                                           shelf3.shelf_id,
                                           shelf4.shelf_id]})

        t.status_is(200, diag=True)
        t.json_has('stocks')
        shelf_types = {
            (s['shelf_id'], s['product_id']): s['shelf_type']
            for s in t.res['json']['stocks']
        }
        expected_shelf_types = {
            (shelf1.shelf_id, product.product_id): 'store',
            (shelf2.shelf_id, product.product_id): 'store',
            (shelf3.shelf_id, item1.item_id): 'parcel',
            (shelf4.shelf_id, item2.item_id): 'parcel',
        }
        for k in shelf_types:
            tap.eq_ok(shelf_types[k], expected_shelf_types.get(k),
                      'Correct shelf type received')


async def test_shelf_not_found(api, tap, dataset):
    with tap.plan(4):
        t = await api(role='admin')
        store = await dataset.store()
        await dataset.shelf(store=store, type='store')
        await dataset.shelf(store=store, type='store')

        await t.post_ok('api_admin_stocks_shelf',
                        json={'shelf_id': 'does_not_exist'})
        t.status_is(403, diag=True)
        await t.post_ok('api_admin_stocks_shelf',
                        json={'shelf_id': ['not_exist1', 'not_exist2']})
        t.status_is(403, diag=True)


async def test_product_not_found(api, tap, dataset):
    with tap.plan(4):
        t = await api(role='admin')
        store = await dataset.store()
        await dataset.product()
        await dataset.product()
        await dataset.product()

        await t.post_ok('api_admin_stocks_product',
                        json={'store_id': store.store_id,
                              'product_id': 'does_not_exist'})
        t.status_is(403, diag=True)
        await t.post_ok('api_admin_stocks_product',
                        json={'store_id': store.store_id,
                              'product_id': ['not_exist1', 'not_exist2']})
        t.status_is(403, diag=True)


async def test_product_shelf_type(api, tap, dataset):
    with tap.plan(25):
        t = await api(role='admin')
        store = await dataset.store(options={'exp_illidan': True})
        shelf1 = await dataset.shelf(store=store, type='kitchen_components')
        shelf2 = await dataset.shelf(store=store, type='office')
        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()
        product4 = await dataset.product(
            vars={
                'imported': {
                    'nomenclature_type': 'consumable',
                }
            }
        )

        await dataset.stock(product=product1,
                            shelf=shelf1,
                            store=store,
                            quants=11,
                            lot='lot11', count=13, reserve=3)
        await dataset.stock(product=product2,
                            shelf=shelf1,
                            store=store,
                            quants=12,
                            lot='lot21', count=14, reserve=4)
        await dataset.stock(product=product3,
                            shelf=shelf1,
                            quants=13,
                            store=store, count=15, reserve=5)

        await dataset.stock(product=product4,
                            shelf=shelf2,
                            quants=21,
                            store=store, count=16, reserve=6)

        await dataset.stock(product=product1,
                            shelf=shelf1,
                            store=store,
                            quants=11,
                            lot='lot12', count=18, reserve=8)
        await dataset.stock(product=product2,
                            shelf=shelf1,
                            store=store,
                            quants=12,
                            lot='lot22', count=19, reserve=9)

        await t.post_ok('api_admin_stocks_product',
                        json={'store_id': store.store_id,
                              'product_id': product1.product_id,
                              'shelf_type': 'kitchen_components'})
        t.status_is(200, diag=True)
        t.json_has('stocks')
        shelves = t.res['json']['stocks']
        tap.eq_ok(
            {shelf['shelf_id']: shelf['count'] for shelf in shelves},
            {
                shelf1.shelf_id: 31,
            },
            'Правильно посчитаны остатки товара 1 на полках'
        )
        tap.eq_ok(
            {shelf['shelf_id']: shelf['reserve'] for shelf in shelves},
            {
                shelf1.shelf_id: 11,
            },
            'Правильно посчитаны резервы товара 1 на полках'
        )
        tap.eq_ok(
            {shelf['shelf_id']: shelf['is_components'] for shelf in shelves},
            {
                shelf1.shelf_id: True,
            },
            'Правильно посчитаны is_components'
        )

        await t.post_ok('api_admin_stocks_product',
                        json={'store_id': store.store_id,
                              'product_id': product2.product_id,
                              'shelf_type': 'kitchen_components'})
        t.status_is(200, diag=True)
        t.json_has('stocks')
        shelves = t.res['json']['stocks']
        tap.eq_ok(
            {shelf['shelf_id']: shelf['count'] for shelf in shelves},
            {
                shelf1.shelf_id: 33,
            },
            'Правильно посчитаны остатки товара 2 на полках'
        )
        tap.eq_ok(
            {shelf['shelf_id']: shelf['reserve'] for shelf in shelves},
            {
                shelf1.shelf_id: 13,
            },
            'Правильно посчитаны резервы товара 2 на полках'
        )
        tap.eq_ok(
            {shelf['shelf_id']: shelf['is_components'] for shelf in shelves},
            {
                shelf1.shelf_id: True,
            },
            'Правильно посчитаны is_components'
        )

        await t.post_ok('api_admin_stocks_product',
                        json={'store_id': store.store_id,
                              'product_id': product3.product_id,
                              'shelf_type': 'kitchen_components'})
        t.status_is(200, diag=True)
        t.json_has('stocks')
        shelves = t.res['json']['stocks']
        tap.eq_ok(
            {shelf['shelf_id']: shelf['count'] for shelf in shelves},
            {
                shelf1.shelf_id: 15,
            },
            'Правильно посчитаны остатки товара 3 на полках'
        )
        tap.eq_ok(
            {shelf['shelf_id']: shelf['reserve'] for shelf in shelves},
            {
                shelf1.shelf_id: 5,
            },
            'Правильно посчитаны резервы товара 3 на полках'
        )
        tap.eq_ok(
            {shelf['shelf_id']: shelf['is_components'] for shelf in shelves},
            {
                shelf1.shelf_id: True,
            },
            'Правильно посчитаны is_components'
        )

        await t.post_ok('api_admin_stocks_product',
                        json={'store_id': store.store_id,
                              'product_id': [product1.product_id,
                                             product2.product_id,
                                             product3.product_id,
                                             product4.product_id,
                                             ],
                              'shelf_type': 'office'})
        t.status_is(200, diag=True)
        t.json_has('stocks')
        shelves = t.res['json']['stocks']
        tap.eq_ok(
            {(shelf['shelf_id'], shelf['product_id']): shelf['count']
             for shelf in shelves},
            {
                (shelf2.shelf_id, product4.product_id): 16,
            },
            'Правильно посчитаны остатки товаров 1, 2, 3 и 4 на полках'
        )
        tap.eq_ok(
            {(shelf['shelf_id'], shelf['product_id']): shelf['reserve']
             for shelf in shelves},
            {
                (shelf2.shelf_id, product4.product_id): 6,
            },
            'Правильно посчитаны резервы товаров 1, 2, 3 и 4 на полках'
        )
        tap.eq_ok(
            {(shelf['shelf_id'], shelf['product_id']): shelf['is_components']
             for shelf in shelves},
            {
                (shelf2.shelf_id, product4.product_id): False,
            },
            'Правильно посчитаны is_components'
        )
        tap.eq_ok(
            {(shelf['shelf_id'], shelf['product_id']): shelf['quants']
             for shelf in shelves},
            {
                (shelf2.shelf_id, product4.product_id): 21,
            },
            'Правильно посчитаны quants'
        )
