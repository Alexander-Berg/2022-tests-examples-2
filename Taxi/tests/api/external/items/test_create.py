async def test_bulk_create(tap, dataset, api, uuid, now):
    with tap.plan(55, 'балковый апдейт'):
        t = await api(role='token:web.external.tokens.0')
        store1 = await dataset.store()
        store2 = await dataset.store()
        items = [
            {
                'type': 'parcel',
                'store_id': store_id,
                'external_id': uuid(),
                'title': uuid(),
                'description': None,
                'data': {
                    'delivery': now().strftime('%F'),
                    'height': 2,
                },
                'barcode': [uuid()],
            }
            for store_id in [store1.store_id, store1.store_id, store2.store_id]
        ]

        for desc in ('первый запрос', 'повтор'):
            await t.post_ok(
                'api_external_items_create',
                json={'items': items},
                desc=desc,
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            for i, item in enumerate(items):
                t.json_is(f'items.{i}.barcode', item['barcode'])
                t.json_is(f'items.{i}.store_id', item['store_id'])
                t.json_is(f'items.{i}.title', item['title'])
                t.json_has(f'items.{i}.item_id', 'item_id present')
                t.json_is(f'items.{i}.external_id', item['external_id'],
                          'correct external_id')
                t.json_is(f'items.{i}.data.height', 2, 'height attr')

        item = await dataset.Item.load(t.res['json']['items'][0]['item_id'])

        await t.post_ok(
            'api_external_items_create',
            json={
                'items': [{
                    **items[0],
                    **{'barcode': [uuid()]},
                }]
            },
            desc='Изменяем посылке 0 - barcode',
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        item = await dataset.Item.load(t.res['json']['items'][0]['item_id'])

        tap.ne(items[0]['barcode'], item.barcode, 'barcode поменялся')

        item.status = 'inactive'
        tap.ok(await item.save(), 'деактивируем экземпляр')

        await t.post_ok(
            'api_external_items_create',
            json={
                'items': [{
                    **items[0],
                    **{'external_id': uuid()}
                }]
            },
            desc='Изменяем посылке 0 - external_id',
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        item.status = 'inactive'
        tap.ok(await item.save(), 'деактивируем экземпляр')

        await t.post_ok(
            'api_external_items_create',
            json={
                'items': [{
                    **items[0],
                    **{'external_id': item.external_id,
                       'barcode': item.barcode}
                }]
            },
        )
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'Item has already inactive')


async def test_bad_store(tap, api, uuid, now):
    with tap.plan(4, 'Некорректный склад'):
        t = await api(role='token:web.external.tokens.0')

        await t.post_ok(
            'api_external_items_create',
            json={
                'items': [{
                    'type': 'parcel',
                    'store_id': uuid(),
                    'external_id': uuid(),
                    'title': 'Тест',
                    'description': None,
                    'data': {
                        'delivery': now().strftime('%F'),
                    },
                    'barcode': [uuid()],
                }]
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'wrong store_id')


async def test_create_update(tap, dataset, api, uuid, now):
    with tap.plan(33, 'Обновление повторным запросом'):
        t = await api(role='token:web.external.tokens.0')
        store = await dataset.store()
        items = [
            {
                'type': 'parcel',
                'store_id': store_id,
                'external_id': uuid(),
                'title': uuid(),
                'description': None,
                'data': {
                    'delivery': now().strftime('%F'),
                },
                'barcode': [uuid()],
            }
            for store_id in [store.store_id, store.store_id, store.store_id]
        ]

        await t.post_ok(
            'api_external_items_create',
            json={'items': items},
            desc='create запрос',
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        for i, item in enumerate(items):
            t.json_is(f'items.{i}.barcode', item['barcode'])
            t.json_is(f'items.{i}.store_id', item['store_id'])
            t.json_is(f'items.{i}.title', item['title'])
            t.json_has(f'items.{i}.item_id', 'item_id present')
            t.json_is(f'items.{i}.external_id', item['external_id'],
                      'correct external_id')

        for i in items:
            i['data']['hello'] = 'world'
            i['data']['weight'] = 223
            i['barcode'] = [uuid()]

        await t.post_ok(
            'api_external_items_create',
            json={'items': items},
            desc='update запрос',
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        for i in items:
            item = await dataset.Item.load(
                [store.store_id, i['external_id']],
                by='external'
            )
            tap.ok(item, 'Загружен экземпляр')
            tap.eq(item.data['hello'], 'world', 'обновление произошло')
            tap.eq(item.data['weight'], 223, 'обновление произошло')
            tap.eq(
                item.barcode,
                i['barcode'],
                'обновление ШК произошло')
