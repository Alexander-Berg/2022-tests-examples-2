async def test_change_eid(tap, api, dataset, uuid):
    with tap.plan(14, 'Изменение external_id'):
        store = await dataset.store()
        tap.ok(store, 'склад создан')


        new_eid = uuid()

        t = await api(role='admin')

        await t.post_ok('api_admin_stores_change_external_id',
                        json={
                            'store_id': store.store_id,
                            'new_external_id': new_eid,
                        })
        t.status_is(200, diag=True)
        t.json_is('store.store_id', store.store_id)
        t.json_is('store.external_id', new_eid)

        tap.ok(await store.reload(), 'Перегружен')
        tap.eq(store.external_id, new_eid, 'Новый id в базе')

        await t.post_ok('api_admin_stores_change_external_id',
                        json={
                            'store_id': store.store_id,
                            'new_external_id': new_eid,
                        })
        t.status_is(200, diag=True, desc='Повторный запрос вернул 200')


        store2 = await dataset.store()
        tap.ok(store2, 'Второй склад сгенерирован')

        await t.post_ok('api_admin_stores_change_external_id',
                        json={
                            'store_id': store2.store_id,
                            'new_external_id': new_eid,
                        })
        t.status_is(410, diag=True)

        t.json_is('code', 'ER_STORE_EXISTS')
        t.json_is('details.store_id', store.store_id)
