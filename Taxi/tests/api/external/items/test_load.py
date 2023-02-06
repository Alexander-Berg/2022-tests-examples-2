async def test_load_success(tap, api, dataset):
    with tap.plan(9, 'Загрузка деталей экземпляра'):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()
        item = await dataset.item(store=store)
        tap.ok(item, 'Создан экземпляр')

        stock = await dataset.stock(item=item, store=store)
        tap.ok(stock, 'Экземпляр на складе')

        await t.post_ok(
            'api_external_items_load',
            json={
                'item_id': item.item_id
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('item.item_id', item.item_id, 'Искомый ID образца')
        t.json_is('item.store_id', store.store_id, 'Правильный склад')
        t.json_is('item.count', 1, 'Правильное количество товара')
        t.json_is('item.reserve', 0, 'Нет резерва')


async def test_load_not_found_item(tap, api):
    with tap.plan(3, 'Экземплар не найден'):
        t = await api(role='token:web.external.tokens.0')

        fake_item_id = 44 * '0'

        await t.post_ok(
            'api_external_items_load',
            json={
                'item_id': fake_item_id
            }
        )
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_ITEM_NOT_FOUND')


async def test_load_not_found_stocks(tap, api, dataset):
    with tap.plan(6, 'Нет на складе'):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()
        item = await dataset.item(store=store)

        await t.post_ok(
            'api_external_items_load',
            json={
                'item_id': item.item_id
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('item.item_id', item.item_id, 'Искомый ID образца')
        t.json_is('item.store_id', store.store_id, 'Правильный склад')
        t.json_is('item.count', 0, 'Нет на складе')


async def test_load_multiple_items(tap, api, dataset):
    with tap:
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()
        item = await dataset.item(store=store)
        tap.ok(item, 'Создан экземпляр')

        stock = await dataset.stock(item=item, store=store)
        tap.ok(stock, 'Экземпляр на складе')
        stock = await dataset.stock(item=item, store=store)
        tap.ok(stock, 'Еще раз тот же экземпляр на складе')

        await t.post_ok(
            'api_external_items_load',
            json={
                'item_id': item.item_id
            }
        )
        t.status_is(500, diag=True)
