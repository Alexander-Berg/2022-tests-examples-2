import pytest

from stall.model.user import User


@pytest.mark.parametrize(
    'role',
    [
        'authen_guest', 'executer', 'barcode_executer', 'store_admin',
        'supervisor', 'expansioner', 'expansioner_ro', 'category_manager',
        'support', 'support_ro', 'city_head', 'admin_ro', 'admin', 'provider',
        'dc_admin', 'support_it',  'courier',
    ]
)
async def test_mutate_no_store(tap, api, dataset, role):
    with tap.plan(12):
        user = await dataset.user(role=role, super_role='admin', store_id=None)

        t = await api(user=user)

        await t.post_ok('api_admin_users_mutate_role',
                        json={
                            'role': 'category_manager',
                        })
        t.status_is(200, diag=True, desc='Сохранили новую роль')
        t.json_is('code', 'OK')
        t.json_has('user', 'пользователь в ответе')
        t.json_is('user.role', 'category_manager')

        loaded = await User.load(user.user_id)
        tap.ok(loaded, 'Загрузили')
        tap.eq(loaded.role, 'category_manager', 'роль в БД поменялась')
        tap.eq(loaded.store_id, None, 'Склад пока не назначен')

        await t.post_ok('api_admin_users_mutate_role',
                        json={
                            'role': 'store_admin',
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'store_id for role store_admin is required')


@pytest.mark.parametrize(
    'role',
    [
        'authen_guest', 'executer', 'barcode_executer', 'store_admin',
        'supervisor', 'expansioner', 'expansioner_ro', 'category_manager',
        'support', 'support_ro', 'city_head', 'admin_ro', 'admin', 'provider',
        'dc_admin', 'support_it', 'courier',
    ]
)
async def test_mutate_with_store(tap, api, dataset, role):
    with tap.plan(15):
        store = await dataset.store()
        user = await dataset.user(role=role, super_role='admin', store_id=None)

        t = await api(user=user)

        await t.post_ok('api_admin_users_mutate_role',
                        json={
                            'role': 'store_admin',
                            'store_id': store.store_id,
                        })
        t.status_is(200, diag=True, desc='Сохранили новую роль')
        t.json_is('code', 'OK')
        t.json_has('user', 'пользователь в ответе')
        t.json_is('user.role', 'store_admin')

        loaded = await User.load(user.user_id)
        tap.ok(loaded, 'Загрузили')
        tap.eq(loaded.role, 'store_admin', 'роль в БД store_admin')
        tap.eq(loaded.store_id, store.store_id, 'Склад назначен')

        user = await dataset.user(role=role, super_role='admin', store=store)
        t = await api(user=user)
        await t.post_ok('api_admin_users_mutate_role',
                        json={
                            'role': 'store_admin',
                        })
        t.json_is('code', 'OK')
        t.json_has('user', 'пользователь в ответе')
        t.json_is('user.role', 'store_admin')

        loaded = await User.load(user.user_id)
        tap.ok(loaded, 'Загрузили')
        tap.eq(loaded.role, 'store_admin', 'роль в БД store_admin')
        tap.eq(loaded.store_id, store.store_id, 'Склад назначен')


async def test_access_denied(tap, api, dataset):
    with tap.plan(4):
        user = await dataset.user(role='admin', super_role='support')

        t = await api(user=user)

        await t.post_ok('api_admin_users_mutate_role',
                        json={
                            'role': 'category_manager',
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'support cannot become category_manager')


async def test_not_found(tap, api, dataset, uuid):
    with tap.plan(4):
        user = await dataset.user(role='admin', super_role='admin')

        t = await api(user=user)

        await t.post_ok('api_admin_users_mutate_role',
                        json={
                            'role': 'category_manager',
                            'store_id': uuid(),
                        })
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')
        t.json_is('message', 'store not found')


async def test_no_super_role(tap, api, dataset):
    with tap.plan(4):
        user = await dataset.user(role='admin', super_role=None)

        t = await api(user=user)

        await t.post_ok('api_admin_users_mutate_role',
                        json={
                            'role': 'category_manager',
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'super_role is not set')
