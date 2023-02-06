async def test_wrong_provider(api, tap, uuid):
    with tap.plan(3):

        t = await api(role='admin')

        await t.post_ok('api_admin_providers_join',
                        json={'provider_id': uuid()})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'code')


async def test_join(api, tap, dataset):
    with tap.plan(8):

        user = await dataset.user(role='admin')
        tap.ok(user, 'пользователь создан')

        t = await api()
        t.set_user(user)

        provider = await dataset.provider()
        tap.ok(provider, 'поставщик создан')

        tap.eq(user.provider_id, None, 'пользователь не присоединен')

        await t.post_ok('api_admin_providers_join',
                        json={'provider_id': provider.provider_id})
        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'code')
        t.json_is(
            'message', f'joined provider {provider.provider_id}', 'message')

        user = await user.load(user.user_id)

        tap.eq(user.provider_id,
               provider.provider_id,
               'пользователь присоединен к поставщику')


async def test_providers_allow(api, tap, dataset):
    with tap.plan(8, 'прикрепляемся к разрешенным поставщикам'):

        store1 = await dataset.store()
        store2 = await dataset.store()

        provider1 = await dataset.provider(stores=[store1.store_id])
        provider2 = await dataset.provider(stores=[store2.store_id])

        user = await dataset.user(
            store=store1,
            role='admin',
            stores_allow = [store1.store_id],
        )
        tap.ok(user.has_permit('join_provider'), 'может прилепляться')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_providers_join',
            json={'provider_id': provider1.provider_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await user.reload()
        tap.eq_ok(user.provider_id, provider1.provider_id,
                  'прилепился к поставщику 1')

        await t.post_ok(
            'api_admin_providers_join',
            json={'provider_id': provider2.provider_id},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
