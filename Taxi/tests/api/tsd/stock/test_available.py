async def test_list(tap, dataset, api, uuid):
    # pylint: disable=too-many-statements
    with tap.plan(50, 'Запрос с выдачей и фильтрами'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store)
        shelf2 = await dataset.shelf(store=store, type='repacking')
        user = await dataset.user(
            store=store,
            role='executer',
            force_role='barcode_executer',
        )

        product1 = await dataset.product()
        product2 = await dataset.product()
        product3 = await dataset.product()
        product4 = await dataset.product()
        product5 = await dataset.product()

        await dataset.stock(
            shelf=shelf,
            product=product1,
            count=10,
            valid='2020-01-01',
            lot=uuid(),
        )
        await dataset.stock(
            shelf=shelf,
            product=product2,
            count=20,
            lot=uuid(),
        )
        await dataset.stock(
            shelf=shelf,
            product=product1,
            count=30,
            valid='2020-01-03',
            lot=uuid(),
        )
        await dataset.stock(
            shelf=shelf,
            product=product4,
            count=0,
            valid='2020-01-01',
            lot=uuid(),
        )
        await dataset.stock(
            shelf=shelf2,
            product=product5,
            count=3,
            valid='2020-01-01',
            lot=uuid(),
        )

        t = await api(user=user)

        tap.note('Продукт 1')
        await t.post_ok('api_tsd_stock_available', json={
            'product_id': [product1.product_id],
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('found')
        t.json_is('found.0.product_id', product1.product_id)
        t.json_is('found.0.shelf_id', shelf.shelf_id)
        t.json_is('found.0.shelf_type', shelf.type)
        t.json_is('found.0.count', 40)
        t.json_is('found.0.reserved', 0)
        t.json_is('found.0.valid', '2020-01-01')
        t.json_hasnt('found.1')
        t.json_is('has_stocks', True)

        tap.note('Продукт 2')
        await t.post_ok('api_tsd_stock_available', json={
            'shelf_id': shelf.shelf_id,
            'product_id': product2.product_id,
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('found')
        t.json_is('found.0.product_id', product2.product_id)
        t.json_is('found.0.shelf_id', shelf.shelf_id)
        t.json_is('found.0.shelf_type', shelf.type)
        t.json_is('found.0.count', 20)
        t.json_is('found.0.reserved', 0)
        t.json_is('found.0.valid', None)
        t.json_hasnt('found.1')
        t.json_is('has_stocks', True)

        tap.note('Продукт 3')
        await t.post_ok('api_tsd_stock_available', json={
            'shelf_id': shelf.shelf_id,
            'product_id': product3.product_id,
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('found')
        t.json_hasnt('found.0')
        t.json_is('has_stocks', False)

        tap.note('Продукт 4')
        await t.post_ok('api_tsd_stock_available', json={
            'product_id': product4.product_id,
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('found')
        t.json_hasnt('found.0')
        t.json_is('has_stocks', True)

        tap.note('Продукт 5')
        await t.post_ok('api_tsd_stock_available', json={
            'product_id': product5.product_id,
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('found')
        t.json_is('found.0.count', 3)
        t.json_is('found.0.reserved', 0)
        t.json_is('has_stocks', True)

        tap.note('Пустой фильтр')
        await t.post_ok('api_tsd_stock_available', json={
            'shelf_id': shelf.shelf_id,
            'product_id': [],
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('found')
        t.json_has('found.0')
        t.json_has('found.1')
        t.json_is('has_stocks', True)


async def test_list_by_item_id(tap, dataset, api, uuid):
    with tap.plan(31, 'Запрос посылок с фильтрами'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='parcel')
        user = await dataset.user(
            store=store,
            role='executer',
            force_role='barcode_executer',
        )

        item1 = await dataset.item()
        item2 = await dataset.item()

        await dataset.stock(
            shelf=shelf,
            product=item1,
            count=1,
            valid='2020-01-01',
            lot=uuid(),
            shelf_type='parcel',
        )
        await dataset.stock(
            shelf=shelf,
            product=item2,
            count=1,
            lot=uuid(),
            shelf_type='parcel',
        )

        t = await api(user=user)

        tap.note('Посылка 1')
        await t.post_ok('api_tsd_stock_available', json={
            'item_id': [item1.item_id],
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('found')
        t.json_is('found.0.product_id', item1.item_id)
        t.json_is('found.0.shelf_id', shelf.shelf_id)
        t.json_is('found.0.shelf_type', shelf.type)
        t.json_is('found.0.count', 1)
        t.json_is('found.0.reserved', 0)
        t.json_is('found.0.valid', '2020-01-01')
        t.json_hasnt('found.1')
        t.json_is('has_stocks', True)

        tap.note('Посылка 2')
        await t.post_ok('api_tsd_stock_available', json={
            'shelf_id': shelf.shelf_id,
            'item_id': item2.item_id,
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('found')
        t.json_is('found.0.product_id', item2.item_id)
        t.json_is('found.0.shelf_id', shelf.shelf_id)
        t.json_is('found.0.shelf_type', shelf.type)
        t.json_is('found.0.count', 1)
        t.json_is('found.0.reserved', 0)
        t.json_is('found.0.valid', None)
        t.json_hasnt('found.1')
        t.json_is('has_stocks', True)

        tap.note('Пустой фильтр')
        await t.post_ok('api_tsd_stock_available', json={
            'shelf_id': shelf.shelf_id,
            'item_id': [],
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('found')
        t.json_has('found.0')
        t.json_has('found.1')
        t.json_is('has_stocks', True)


async def test_list_trash(tap, dataset, api, uuid):
    with tap.plan(23, 'Поиск на полке trash'):
        store = await dataset.store()
        shelf = await dataset.shelf(store=store, type='trash')
        user = await dataset.user(
            store=store,
            role='executer',
            force_role='barcode_executer',
        )

        product1 = await dataset.product()

        await dataset.stock(
            shelf=shelf,
            product=product1,
            count=10,
            valid='2020-01-01',
            lot=uuid(),
            shelf_type='trash',
        )

        t = await api(user=user)

        await t.post_ok('api_tsd_stock_available', json={
            'product_id': [product1.product_id],
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('found')
        t.json_hasnt('found.0')

        await t.post_ok('api_tsd_stock_available', json={
            'shelf_id': shelf.shelf_id,
            'product_id': product1.product_id,
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('found')
        t.json_is('found.0.product_id', product1.product_id)
        t.json_is('found.0.shelf_id', shelf.shelf_id)
        t.json_is('found.0.shelf_type', shelf.type)
        t.json_is('found.0.count', 10)
        t.json_is('found.0.reserved', 0)

        await t.post_ok('api_tsd_stock_available', json={
            'shelf_id': shelf.shelf_id,
        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('found')
        t.json_is('found.0.product_id', product1.product_id)
        t.json_is('found.0.shelf_id', shelf.shelf_id)
        t.json_is('found.0.shelf_type', shelf.type)
        t.json_is('found.0.count', 10)
        t.json_is('found.0.reserved', 0)
