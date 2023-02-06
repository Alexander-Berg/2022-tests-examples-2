# pylint: disable=


async def test_load(api, dataset, tap):
    with tap.plan(4, 'Список складов'):

        store1 = await dataset.store()
        store3 = await dataset.store()

        provider = await dataset.provider(
            stores=[store1.store_id, store3.store_id]
        )
        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_provider_stores_load',
            json={'store_id': store1.store_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('store.store_id', store1.store_id)


async def test_load_multiple(api, dataset, tap):
    with tap.plan(5, 'Список складов'):

        store1 = await dataset.store()
        store3 = await dataset.store()

        provider = await dataset.provider(
            stores=[store1.store_id, store3.store_id]
        )
        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_provider_stores_load',
            json={'store_id': [store1.store_id]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('store.0.store_id', store1.store_id)
        t.json_hasnt('store.1', 'Только запрошенные склады')


async def test_load_not_found(api, dataset, tap, uuid):
    with tap.plan(3, 'Нет такого склада'):

        provider = await dataset.provider()
        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_provider_stores_load',
            json={'store_id': uuid()},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_status(api, dataset, tap):
    with tap.plan(3, 'Склад отключен'):

        store1 = await dataset.store(status='closed')
        store3 = await dataset.store()

        provider = await dataset.provider(
            stores=[store1.store_id, store3.store_id]
        )
        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_provider_stores_load',
            json={'store_id': store1.store_id},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_status_multiple(api, dataset, tap):
    with tap.plan(5, 'Склад отключен'):

        store1 = await dataset.store(status='closed')
        store3 = await dataset.store()

        provider = await dataset.provider(
            stores=[store1.store_id, store3.store_id]
        )
        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_provider_stores_load',
            json={'store_id': [store1.store_id, store3.store_id]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('store.0.store_id', store3.store_id)
        t.json_hasnt('store.1', 'Только активные склады')


async def test_status_multiple_fail(api, dataset, tap):
    with tap.plan(4, 'Пустой список если складов нет'):

        store1 = await dataset.store(status='closed')
        store3 = await dataset.store(status='closed')

        provider = await dataset.provider(
            stores=[store1.store_id, store3.store_id]
        )
        user = await dataset.user(
            provider=provider,
            store_id=None,
            role='provider',
        )

        t = await api(user=user)
        await t.post_ok(
            'api_provider_stores_load',
            json={'store_id': [store1.store_id, store3.store_id]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_hasnt('store.0', 'Не ошибка, а просто пустой список')
