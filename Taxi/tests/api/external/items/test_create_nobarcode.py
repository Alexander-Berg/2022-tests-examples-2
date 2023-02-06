async def test_create(tap, dataset, api, uuid, now):
    with tap.plan(45, 'запрос на создание без ШК'):
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
                },
                'barcode': [],
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

        item = await dataset.Item.load(t.res['json']['items'][0]['item_id'])

        await t.post_ok(
            'api_external_items_create',
            json={
                'items': [{
                    **items[0],
                    **{'barcode': [uuid()]},
                }]
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        item.status = 'inactive'
        tap.ok(await item.save(), 'деактивируем экземпляр')

        item.status = 'inactive'
        tap.ok(await item.save(), 'деактивируем экземпляр')

        await t.post_ok(
            'api_external_items_create',
            json={
                'items': [items[0]]
            },
            desc=desc,
        )
        t.status_is(409, diag=True)
        t.json_is('code', 'ER_CONFLICT')
        t.json_is('message', 'Item has already inactive')
