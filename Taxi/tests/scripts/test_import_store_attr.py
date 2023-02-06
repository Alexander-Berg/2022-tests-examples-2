from stall.scripts.store_attr import import_attr


async def test_import_correct_csv(tap, dataset, make_csv_str, uuid):
    stores_count = 5
    with tap:
        stores = [
            await dataset.store(external_id=uuid(), attr={'a': 'hello'})
            for _ in range(stores_count)
        ]

        csv_str = make_csv_str(
            ['external_id', 'telephone', 'telegram', 'email', 'directions'],
            [
                {
                    'external_id': store.external_id,
                    'telephone': f'{i}' * 8,
                    'telegram': f'some_telegram_id_{i}',
                    'email': f'some.email.{i}@example.com',
                    'directions': 'foo bar spam',
                }
                for i, store in enumerate(stores)
            ]
        )
        await import_attr(csv_str, write=True)

        for i, store in enumerate(stores):
            await store.reload()
            tap.eq_ok(store.attr['telephone'], f'{i}' * 8, 'phone')
            tap.eq_ok(store.attr['telegram'], f'some_telegram_id_{i}', 'tg')
            tap.eq_ok(
                store.attr['email'], f'some.email.{i}@example.com', 'email',
            )
            tap.eq_ok(store.attr['directions'], 'foo bar spam', 'directions')
            tap.eq_ok(store.attr.get('a'), 'hello', 'old data unchanged')


async def test_import_bad_csv(tap, dataset, make_csv_str, uuid):
    with tap:
        store = await dataset.store()
        tap.eq(store.attr, {}, 'пустой аттр')

        csv_str = make_csv_str(
            ['external_id', 'telephone', 'telegram'],
            [
                {
                    'external_id': uuid(),
                    'telephone': 'foo',
                    'telegram': 'bar',
                },
            ],
        )
        await import_attr(csv_str, write=True)

        await store.reload()
        tap.eq(store.attr, {}, 'нет такой лавки')

        csv_str = make_csv_str(
            ['external_id', 'telephone', 'trash'],
            [
                {
                    'external_id': uuid(),
                    'telephone': 'foo',
                    'trash': 'bar',
                },
            ],
        )
        await import_attr(csv_str, write=True)

        await store.reload()
        tap.eq(store.attr, {}, 'некорректные поля')

