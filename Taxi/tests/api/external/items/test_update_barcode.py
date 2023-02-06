async def test_update_barcode(tap, api, dataset, uuid):
    with tap.plan(25, 'Функции установки/переустановки без ошибок'):
        t = await api(role='token:web.external.tokens.0')

        item = await dataset.item(barcode=[])
        tap.ok(item, 'экземпляр создан')
        tap.eq(item.barcode, [], 'ШК нет')

        await t.post_ok(
            'api_external_items_update_barcode',
            json={
                'store_id': item.store_id,
                'external_id': item.external_id,
                'barcode': [],
            },
            desc='Установка пусто при пусто',
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        barcode = uuid()
        for attempt in (1, 2):
            await t.post_ok(
                'api_external_items_update_barcode',
                json={
                    'store_id': item.store_id,
                    'external_id': item.external_id,
                    'barcode': [barcode],
                },
                desc=f'Установка ШК при пусто попытка {attempt}',
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            tap.ok(await item.reload(), 'перегружен')
            tap.eq(item.barcode, [barcode], 'Установлено')


        await t.post_ok(
            'api_external_items_update_barcode',
            json={
                'store_id': item.store_id,
                'external_id': item.external_id,
                'barcode': [uuid()],
            },
            desc='Установка ШК при непустом',
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.ok(await item.reload(), 'перегружен')
        tap.ne(item.barcode, [barcode], 'Установлено')

        await t.post_ok(
            'api_external_items_update_barcode',
            json={
                'store_id': item.store_id,
                'external_id': item.external_id,
                'barcode': [],
            },
            desc='Установка пусто при непусто',
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.ok(await item.reload(), 'перегружен')
        tap.eq(item.barcode, [], 'Установлено')


async def test_update_barcode_errors(tap, api, dataset, uuid):
    with tap.plan(15, 'Конфликты'):
        t = await api(role='token:web.external.tokens.0')

        item1 = await dataset.item(barcode=[uuid()])
        tap.ok(item1, 'экземпляр создан')
        item2 = await dataset.item(barcode=[uuid(), uuid()],
                                   store_id=item1.store_id)
        tap.eq(item2.store_id, item1.store_id, 'Ещё экземпляр')

        for bk in item2.barcode + [item2.barcode]:
            if isinstance(bk, str):
                bk = [bk]
            await t.post_ok(
                'api_external_items_update_barcode',
                json={
                    'store_id': item1.store_id,
                    'external_id': item1.external_id,
                    'barcode': bk,
                },
                desc=f'Попытка установки {bk}',
            )
            t.status_is(409, diag=True)
            t.json_is('code', 'ER_CONFLICT')

        item1.status = 'inactive'
        tap.ok(await item1.save(), 'Сброшен статус')

        await t.post_ok(
            'api_external_items_update_barcode',
            json={
                'store_id': item1.store_id,
                'external_id': item1.external_id,
                'barcode': [uuid()],
            },
            desc='Запрос при некативном экземпляре',
        )
        t.status_is(410, diag=True)
        t.json_is('code', 'ER_GONE')

async def test_update_barcode_not_found(tap, api, dataset, uuid):
    with tap.plan(5, 'Не найдено'):
        t = await api(role='token:web.external.tokens.0')

        store = await dataset.store()
        tap.ok(store, 'склад есть')

        await t.post_ok(
            'api_external_items_update_barcode',
            json={
                'store_id': store.store_id,
                'external_id': uuid(),
                'barcode': [uuid()],
            },
            desc='Попытка установки',
        )
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')
        t.json_is('message', 'Item(s) not found')


async def test_update_barcode_bulk(tap, api, dataset, uuid):
    with tap.plan(25, 'Функции установки/переустановки без ошибок'):
        t = await api(role='token:web.external.tokens.0')

        item = await dataset.item(barcode=[])
        tap.ok(item, 'экземпляр создан')
        tap.eq(item.barcode, [], 'ШК нет')

        await t.post_ok(
            'api_external_items_update_barcode',
            json={
                'store_id': item.store_id,
                'external_id': item.external_id,
                'barcode': [],
            },
            desc='Установка пусто при пусто',
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        barcode = uuid()
        for attempt in (1, 2):
            await t.post_ok(
                'api_external_items_update_barcode',
                json={
                    'store_id': item.store_id,
                    'items': [
                        {
                            'external_id': item.external_id,
                            'barcode': [barcode],
                        }
                    ]
                },
                desc=f'Установка ШК при пусто попытка {attempt}',
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            tap.ok(await item.reload(), 'перегружен')
            tap.eq(item.barcode, [barcode], 'Установлено')


        await t.post_ok(
            'api_external_items_update_barcode',
            json={
                'store_id': item.store_id,
                'items': [
                    {
                        'external_id': item.external_id,
                        'barcode': [uuid()],
                    }
                ]
            },
            desc='Установка ШК при непустом',
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.ok(await item.reload(), 'перегружен')
        tap.ne(item.barcode, [barcode], 'Установлено')

        await t.post_ok(
            'api_external_items_update_barcode',
            json={
                'store_id': item.store_id,
                'items': [
                    {
                        'external_id': item.external_id,
                        'barcode': [],
                    }
                ]
            },
            desc='Установка пусто при непусто',
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        tap.ok(await item.reload(), 'перегружен')
        tap.eq(item.barcode, [], 'Установлено')
