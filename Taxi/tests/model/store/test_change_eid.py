async def test_change_eid(tap, dataset, uuid):
    with tap.plan(5, 'Изменение external_id у склада'):
        store = await dataset.store()
        tap.ok(store, 'Склад создан')

        new_external_id = uuid()

        tap.ok(await store.update_external_id(new_external_id),
               'Идентификатор изменён')
        tap.eq(store.external_id, new_external_id, 'Новый идентификатор')
        tap.ok(await store.reload(), 'Склад перегружен')
        tap.eq(store.external_id, new_external_id, 'Новый идентификатор')

