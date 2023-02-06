import pytest


@pytest.mark.parametrize('role',
                         ['executer', 'barcode_executer',
                          'store_admin', 'supervisor',
                          'category_manager', 'support',
                          'support_ro', 'admin_ro', 'admin'])
async def test_executors(tap, api, dataset, role):
    with tap.plan(13):
        store = await dataset.store()
        user = await dataset.user(role=role, store=store)
        user_to_load = await dataset.user()
        tap.ok(user, 'пользователь создан')
        t = await api(user=user)

        await t.post_ok('api_admin_users_executors',
                        json={'user_id': user_to_load.user_id})

        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'код')
        t.json_is('executors.0.user_id', user_to_load.user_id)
        t.json_is('executors.0.fullname', user_to_load.fullname)
        t.json_is('executors.0.nick', user_to_load.nick)

        await t.post_ok('api_admin_users_executors',
                        json={'user_id': [user_to_load.user_id]})

        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'код')
        t.json_is('executors.0.user_id', user_to_load.user_id)
        t.json_is('executors.0.fullname', user_to_load.fullname)
        t.json_is('executors.0.nick', user_to_load.nick)


@pytest.mark.parametrize('role',
                         ['executer', 'barcode_executer',
                          'store_admin', 'supervisor', 'expansioner',
                          'expansioner_ro', 'category_manager', 'support',
                          'support_ro', 'admin_ro', 'admin'])
async def test_executors_no_store(tap, api, dataset, role):
    with tap.plan(3):
        user = await dataset.user(role=role, store_id=None)
        user_to_load = await dataset.user()
        tap.ok(user, 'пользователь создан')
        t = await api(user=user)

        await t.post_ok('api_admin_users_executors',
                        json={'user_id': user_to_load.user_id})

        t.status_is(403, diag=True)
