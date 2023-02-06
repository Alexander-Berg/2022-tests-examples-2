async def test_options(tap, cfg, dataset):
    with tap.plan(7, 'Опции склада'):

        cfg.set('business.store.options', {'test': 'abc'})

        with await dataset.store() as store:
            tap.eq(store.options, {'test': 'abc'}, 'Значние по умолчанию')

        with await dataset.Store.load(store.store_id) as store:
            store.rehash(options={'test2': 'xyz'})
            tap.ok(await store.save(), 'Обновляем')
            tap.eq(
                store.options,
                {'test': 'abc', 'test2': 'xyz'},
                'Значние добавлено'
            )

        with await dataset.Store.load(store.store_id) as store:
            store.rehash(options={'test': '123', 'test2': 'xyz'})
            tap.ok(await store.save(), 'Обновляем')
            tap.eq(
                store.options,
                {'test': '123', 'test2': 'xyz'},
                'Значние изменено'
            )

        with await dataset.Store.load(store.store_id) as store:
            store.rehash(options={'test': 'qwe'})
            tap.ok(await store.save(), 'Обновляем')
            tap.eq(
                store.options,
                {'test': 'qwe'},
                'Значние удалено'
            )
