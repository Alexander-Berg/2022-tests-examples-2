async def test_lsn(dataset, tap):
    with tap.plan(4, 'Тестирование lsn'):
        store = await dataset.store()
        tap.ok(store, 'Склад создан')
        lsn = store.lsn
        tap.ok(lsn, 'lsn назначен')

        tap.ok(await store.save(), 'склад сохранён')
        tap.ok(store.lsn > lsn, 'lsn увеличился')
