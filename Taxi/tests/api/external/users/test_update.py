import pytest

from stall.client.personal import client as personal


async def test_common(tap, dataset, api, ext_api, uuid):
    with tap.plan(23, 'для обновления пользователя '
                      'сначала отвязываем от склада'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        store = await dataset.store(company=company)
        tap.ok(store, 'store created')

        user = await dataset.user(store=store,
                                  provider='internal', role='executer')
        tap.ok(user, 'user created')

        new_store = await dataset.store(company=company)
        tap.ok(new_store, 'new store created')

        # pylint: disable=unused-argument
        async def bulk_store(request):
            return {
                'items': [
                    {'id': uuid()},
                ],
            }

        async with await ext_api(personal, bulk_store):

            t = await api(token=company.token)

            await t.post_ok('api_external_users_update',
                            json={'user_id': user.user_id,
                                'store_id': new_store.store_id,
                                'phone': '88005553535'})

            t.status_is(400, diag=True)
            t.json_is('code', 'ER_USER_STORE_ALREADY_SET')

            await user.reload()
            tap.eq(user.store_id, store.store_id, 'user store still old')
            tap.is_ok(user.phone, None, 'phone still empty')

            await t.post_ok('api_external_users_eject',
                            json={'user_id': user.user_id})

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')

            await user.reload()
            tap.is_ok(user.store_id, None, 'user store is empty')
            tap.is_ok(user.phone, None, 'phone still empty')

            await t.post_ok('api_external_users_update',
                            json={'user_id': user.user_id,
                                'store_id': new_store.store_id,
                                'phone': '88005553535'})

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('user')
            t.json_is('user.user_id', user.user_id)
            t.json_is('user.store_id', new_store.store_id)
            t.json_is('user.phone', '88005553535')

            await user.reload()
            tap.eq(user.store_id, new_store.store_id, 'store_id changed')
            tap.eq(user.phone, '88005553535', 'phone changed')


async def test_foreign_user(tap, dataset, api, ext_api, uuid):
    with tap.plan(8, 'попытка изменить чужого пользователя'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        store = await dataset.store(company=company)
        tap.ok(store, 'store created')

        user = await dataset.user(provider='internal', role='executer')
        tap.ok(user, 'user created')
        tap.is_ok(user.phone, None, 'user phone empty')

        # pylint: disable=unused-argument
        async def bulk_store(request):
            return {
                'items': [
                    {'id': uuid()},
                ],
            }

        async with await ext_api(personal, bulk_store):

            t = await api(token=company.token)
            await t.post_ok('api_external_users_update',
                            json={'user_id': user.user_id,
                                'phone': '88005553535'})

            t.status_is(403, diag=True)
            t.json_is('code', 'ER_USER_ACCESS')

            await user.reload()
            tap.is_ok(user.phone, None, 'user phone still empty')


async def test_unknown_user(tap, dataset, api, uuid):
    with tap.plan(4, 'попытка изменить несуществующего пользователя'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_update',
                        json={'user_id': uuid(),
                              'phone': '88005553535'})

        t.status_is(404, diag=True)
        t.json_is('code', 'ER_USER_NOT_FOUND')


async def test_foreign_store(tap, dataset, api):
    with tap.plan(8, 'попытка проставить чужой склад'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        store = await dataset.store(company=company)
        tap.ok(store, 'store created')

        user = await dataset.user(store=store,
                                  provider='internal', role='executer')
        tap.ok(user, 'user created')

        new_store = await dataset.store()
        tap.ok(new_store, 'new store created')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_update',
                        json={'user_id': user.user_id,
                              'store_id': new_store.store_id})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_STORE_ACCESS')

        await user.reload()
        tap.eq(user.store_id, store.store_id, 'user store not changed')


async def test_unknown_store(tap, dataset, api, uuid):
    with tap.plan(7, 'попытка проставить несуществующий склад'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        store = await dataset.store(company=company)
        tap.ok(store, 'store created')

        user = await dataset.user(store=store,
                                  provider='internal', role='executer')
        tap.ok(user, 'user created')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_update',
                        json={'user_id': user.user_id,
                              'store_id': uuid()})

        t.status_is(404, diag=True)
        t.json_is('code', 'ER_STORE_NOT_FOUND')

        await user.reload()
        tap.eq(user.store_id, store.store_id, 'user store not changed')


@pytest.mark.parametrize('store_id_value', [None, ''])
async def test_empty_store(tap, dataset, api, store_id_value):
    with tap.plan(7, 'попытка сбросить склад'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        store = await dataset.store(company=company)
        tap.ok(store, 'store created')

        user = await dataset.user(store=store,
                                  provider='internal', role='executer')
        tap.ok(user, 'user created')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_update',
                        json={'user_id': user.user_id,
                              'store_id': store_id_value})

        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')

        await user.reload()
        tap.eq(user.store_id, store.store_id, 'user store not changed')


async def test_provider_check(tap, dataset, api):
    with tap.plan(7, 'позволяем изменять только internal'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        store = await dataset.store(company=company)
        tap.ok(store, 'store created')

        user = await dataset.user(store=store)
        tap.ok(user, 'user created')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_update',
                        json={'user_id': user.user_id,
                              'phone': '88005553535'})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_USER_NOT_INTERNAL')

        await user.reload()
        tap.is_ok(user.phone, None, 'phone not changed')


async def test_wrong_token(tap, dataset, api, uuid):
    with tap.plan(12, 'авторизация только по токену компании'):
        t = await api(token=uuid())
        await t.post_ok('api_external_users_update',
                        json={'user_id': 'asdfasdf'})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        t = await api(role='executer')
        await t.post_ok('api_external_users_update',
                        json={'user_id': 'asdfasdf'})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        user = await dataset.user()
        t = await api(user=user)
        await t.post_ok('api_external_users_update',
                        json={'user_id': 'asdfasdf'})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_users_update',
                        json={'user_id': 'asdfasdf'})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_COMPANY_TOKEN')

async def test_pd(tap, dataset, api, uuid, unique_phone, ext_api):
    with tap.plan(6, 'Проверка работы с ПД'):
        company = await dataset.company()
        store = await dataset.store(company=company)
        user = await dataset.user(
            store=store,
            provider='internal',
            role='executer',
            phone_pd_id=uuid(),
        )

        new_phone_pd_id = uuid()

        # pylint: disable=unused-argument
        async def bulk_store(request):
            return {
                'items': [
                    {'id': new_phone_pd_id},
                ],
            }

        async with await ext_api(personal, bulk_store):

            t = await api(token=company.token)
            await t.post_ok(
                'api_external_users_update',
                json={
                    'user_id': user.user_id,
                    'phone': unique_phone(),
                }
            )

            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('user')
            t.json_is('user.user_id', user.user_id)
            t.json_is('user.phone_pd_id', new_phone_pd_id)

async def test_pd_fail(tap, dataset, api, uuid, unique_phone, ext_api):
    with tap.plan(2, 'Проверка работы с недоступным сервером ПД'):
        company = await dataset.company()
        store = await dataset.store(company=company)
        user = await dataset.user(
            store=store,
            provider='internal',
            role='executer',
            phone_pd_id=uuid(),
        )

        # pylint: disable=unused-argument
        async def bulk_store(request):
            return 500, ''

        async with await ext_api(personal, bulk_store):

            t = await api(token=company.token)
            await t.post_ok(
                'api_external_users_update',
                json={
                    'user_id': user.user_id,
                    'phone': unique_phone(),
                }
            )

            t.status_is(424, diag=True)
