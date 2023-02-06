async def test_load(tap, dataset, api):
    with tap.plan(10, 'загрузка экземпляров'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.ok(user, 'пользователь создан')

        item = await dataset.item(
            store=store,
            data={'height': 100, 'weight': 25},
        )
        tap.ok(item, 'экземпляр создан')

        t = await api(user=user)

        await t.post_ok('api_admin_items_load',
                        json={'item_id': item.item_id})
        t.status_is(200, diag=True)
        t.json_is('item.item_id', item.item_id)

        await t.post_ok('api_admin_items_load',
                        json={'item_id': [item.item_id]})
        t.status_is(200, diag=True)
        t.json_is('item.0.item_id', item.item_id)
        t.json_is('item.0.data', {'height': 100, 'weight': 25})


async def test_load_some_absent(tap, dataset, api):
    with tap.plan(8, 'загрузка экземпляров'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store)
        tap.ok(user, 'пользователь создан')

        item = await dataset.item(store=store)
        item2 = await dataset.item(store=store)
        tap.ok(item, 'экземпляр создан')

        t = await api(user=user)

        await t.post_ok('api_admin_items_load',
                        json={'item_id': [item.item_id,
                                          item2.item_id,
                                          'abrakadbra']})
        t.status_is(203, diag=True)
        t.json_is('item.0.item_id', item.item_id)
        t.json_is('item.1.item_id', item2.item_id)
        t.json_hasnt('item.2')


async def test_load_outside_item(tap, dataset, api):
    with tap.plan(7, 'загрузка экземпляров'):
        store = await dataset.store()
        store2 = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='store_admin')
        tap.ok(user, 'пользователь создан')

        item = await dataset.item(store=store)
        item2 = await dataset.item(store=store2)
        tap.ok(item, 'экземпляр создан')

        t = await api(user=user)

        await t.post_ok('api_admin_items_load',
                        json={'item_id': [item.item_id,
                                          item2.item_id,
                                          'abrakadbra']})
        t.status_is(203, diag=True)
        t.json_is('item.0.item_id', item.item_id)
        t.json_hasnt('item.1')
