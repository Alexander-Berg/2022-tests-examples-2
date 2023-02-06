import pytest


async def test_save_exists(tap, dataset, api):
    with tap.plan(14):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        provider = await dataset.provider(title='медвед')
        tap.ok(provider, 'полка создана')
        tap.eq(provider.stores, [], 'не привязан')
        tap.eq(provider.title, 'медвед', 'название')

        user = await dataset.user(store=store, role='admin')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.store_id, store.store_id, 'на складе')

        t = await api()
        t.set_user(user)

        await t.post_ok('api_admin_providers_save',
                        json={
                            'provider_id': provider.provider_id,
                            'title': 'привет',
                            'cluster': 'Москва',
                            'stores': [store.store_id],
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('provider.updated', 'updated')
        t.json_has('provider.created', 'created')
        t.json_is('provider.title', 'привет', 'title')
        t.json_is('provider.cluster', 'Москва', 'cluster')
        t.json_is('provider.stores', [store.store_id], 'stores')


async def test_save_unexists(tap, dataset, api, uuid):
    with tap.plan(14):
        store = await dataset.store()
        tap.ok(store, 'склад создан')

        user = await dataset.user(store=store, role='admin')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.store_id, store.store_id, 'на складе')

        t = await api()
        t.set_user(user)

        external_id = uuid()

        await t.post_ok('api_admin_providers_save',
                        json={
                            'external_id': external_id,
                            'title': 'привет',
                            'cluster': 'Москва',
                            'stores': [store.store_id],
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('provider.updated', 'updated')
        t.json_has('provider.created', 'created')
        t.json_is('provider.title', 'привет', 'title')
        t.json_is('provider.cluster', 'Москва', 'cluster')
        t.json_is('provider.stores', [store.store_id], 'stores')
        t.json_is('provider.external_id', external_id, 'идентификатор')
        t.json_is('provider.status', 'active', 'статус "активный"')
        t.json_is('provider.user_id', user.user_id)


@pytest.mark.parametrize('role', ['store_admin'])
async def test_save_prohibited(tap, dataset, api, role):
    with tap.plan(3):
        store = await dataset.store()
        provider = await dataset.provider()

        t = await api(role=role)

        await t.post_ok('api_admin_providers_save',
                        json={
                            'provider_id': provider.provider_id,
                            'title': 'привет',
                            'cluster': 'Москва',
                            'stores': [store.store_id],
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_save_user_id(tap, dataset, api):
    with tap:
        provider = await dataset.provider()

        t = await api(role='admin')

        await t.post_ok('api_admin_providers_save',
                        json={
                            'provider_id': provider.provider_id,
                            'title': 'привет',
                            'user_id': 'hello',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_isnt('provider.user_id', 'hello')
