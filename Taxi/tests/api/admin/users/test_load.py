import pytest


@pytest.mark.parametrize('role', ['admin', 'admin_ro'])
async def test_load(tap, api, dataset, role, uuid):
    with tap.plan(9, 'Загрузка пользователя'):
        user = await dataset.user(
            role=role,
            email_pd_id=uuid(),
            phone_pd_id=uuid(),
        )

        t = await api(user=user)
        await t.post_ok('api_admin_users_load',
                        json={'user_id': user.user_id})

        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_is('user.user_id', user.user_id)
        t.json_is('user.role', user.role)
        t.json_is('user.email_pd_id', user.email_pd_id)
        t.json_hasnt('user.email_hash')
        t.json_is('user.phone_pd_id', user.phone_pd_id)
        t.json_hasnt('user.phone_hash')


@pytest.mark.parametrize('role', ['admin', 'admin_ro'])
async def test_load_by_list(tap, api, dataset, role):
    with tap.plan(12):
        t = await api()

        user = await dataset.user(role=role)
        user1 = await dataset.user(role=role)
        user2 = await dataset.user(role=role)
        users = {user1.user_id: user1, user2.user_id: user2}
        tap.ok(user, 'пользователь создан')
        t.set_user(user)

        await t.post_ok('api_admin_users_load',
                        json={'user_id': [user1.user_id, user2.user_id]})

        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'код')
        t.json_has('user', 'Получены пользователи')
        received_users = t.res['json']['user']
        tap.eq_ok(len(received_users), 2, 'Пользователей пришло, сколько надо')
        ids = [u['user_id'] for u in received_users]
        tap.ok(user1.user_id in ids, 'Первый пользователь получен')
        tap.ok(user2.user_id in ids, 'Второй пользователь получен')

        for u in received_users:
            tap.eq_ok(u['role'], users[u['user_id']].role, 'Роль')
            tap.eq_ok(u['device'][0], users[u['user_id']].device[0], 'Уст-во')


async def test_load_over_sub(tap, api, dataset):
    with tap.plan(11, 'Загрузка только для подчиненных'):
        t = await api()

        store = await dataset.store()

        user = await dataset.user(store=store, role='store_admin')
        t.set_user(user)

        tap.note('Получаем сами себя')
        await t.post_ok('api_admin_users_load',
                        json={'user_id': user.user_id})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'код')
        t.json_is('message', 'Access denied')

        executer = await dataset.user(role='executer', store=store)
        tap.in_ok(executer.role.name,
                  user.permit('sub'),
                  'в списке ролей доступных')

        tap.note('Получаем подчиненного')
        await t.post_ok('api_admin_users_load',
                        json={'user_id': executer.user_id})
        t.status_is(200, diag=True)

        t.json_is('code', 'OK', 'код')
        t.json_is('user.user_id',
                  executer.user_id,
                  'идентификатор пользователя')
        t.json_is('user.role',
                  executer.role,
                  'роль пользователя')
        t.json_is('user.device.0',
                  executer.device[0],
                  'устройство пользователя')


async def test_over_permit_out_store(tap, api, dataset):
    with tap.plan(7, 'Чужая лавка'):
        company1 = await dataset.company()

        store1 = await dataset.store(company=company1)
        store2 = await dataset.store(company=company1)

        user = await dataset.user(role='admin', store=store1)
        executor = await dataset.user(role='executer', store=store2)

        t = await api(user=user)
        with user.role as role:
            role.remove_permit('out_of_store')

            await t.post_ok('api_admin_users_load',
                            json={'user_id': executor.user_id})
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

        with user.role:
            await t.post_ok('api_admin_users_load',
                            json={'user_id': executor.user_id})
            t.status_is(200, diag=True)
            t.json_is('code', 'OK', 'код')
            t.json_is('user.user_id', executor.user_id, 'идентификатор')


async def test_over_permit_out_company(tap, api, dataset):
    with tap.plan(10, 'Чужая компания'):
        store1 = await dataset.store()
        store2 = await dataset.store()

        user = await dataset.user(role='admin', company=store1)
        executor = await dataset.user(role='executer', store=store2)

        t = await api(user=user)
        with user.role as role:
            role.remove_permit('out_of_store')
            role.remove_permit('out_of_company')

            await t.post_ok('api_admin_users_load',
                            json={'user_id': executor.user_id})
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

        with user.role as role:
            role.remove_permit('out_of_company')

            await t.post_ok('api_admin_users_load',
                            json={'user_id': executor.user_id})
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

        with user.role:
            await t.post_ok('api_admin_users_load',
                            json={'user_id': executor.user_id})
            t.status_is(200, diag=True)
            t.json_is('code', 'OK', 'код')
            t.json_is('user.user_id', executor.user_id, 'идентификатор')


async def test_load_over_store_id(tap, api, dataset):
    with tap.plan(14):
        t = await api()

        user = await dataset.user(role='store_admin')
        tap.ok(user, 'пользователь создан')
        tap.ok(user.store_id, 'У пользователя есть склад')
        tap.eq(user.role, 'store_admin', 'роль')
        t.set_user(user)

        executer = await dataset.user(role='executer')
        tap.ok(executer, 'работник создан')
        tap.ne(executer.store_id, user.store_id, 'на ДРУГОМ складе')
        tap.in_ok(executer.role.name,
                  user.permit('sub'),
                  'в списке ролей доступных')

        await t.post_ok('api_admin_users_load',
                        json={'user_id': executer.user_id})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'код')
        t.json_is('message', 'Access denied')

        await t.post_ok('api_admin_users_load',
                        json={'user_id': executer.user_id})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'код')
        t.json_is('message', 'Access denied')


async def test_load_non_existent(tap, api, dataset):
    with tap.plan(4):
        t = await api()

        user = await dataset.user(role='admin')
        tap.ok(user, 'пользователь создан')
        t.set_user(user)

        await t.post_ok('api_admin_users_load',
                        json={'user_id': 'broken_id'})

        t.status_is(403, diag=True)

        t.json_is('code', 'ER_ACCESS', 'код')


async def test_load_by_disabled_admin(tap, api, dataset):
    with tap.plan(6):
        t = await api()

        user = await dataset.user(role='admin', status='disabled')
        tap.ok(user, 'пользователь создан')
        tap.eq(user.status, 'disabled', 'Пользователь отключен')
        tap.ok(user.is_disabled, 'проперть об отключении')
        t.set_user(user)

        await t.post_ok('api_admin_users_load',
                        json={'user_id': user.user_id})

        t.status_is(401, diag=True)

        t.json_is('code', 'ER_AUTH', 'код')


async def test_qr_bar_codes(tap, api, dataset):
    with tap.plan(18):
        store = await dataset.store()
        admin = await dataset.user(role='admin')
        support = await dataset.user(role='support', store=store)
        executer = await dataset.user(role='executer', store=store)

        t = await api(user=admin)
        await t.post_ok('api_admin_users_load',
                        json={'user_id': admin.user_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_is('user.user_id',
                  admin.user_id,
                  'идентификатор пользователя')
        t.json_is('user.role',
                  admin.role,
                  'роль пользователя')
        t.json_has('user.qrcode', 'qrcode есть')

        t = await api(user=support)
        await t.post_ok('api_admin_users_load',
                        json={'user_id': support.user_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_is('user.user_id',
                  support.user_id,
                  'идентификатор пользователя')
        t.json_is('user.role',
                  support.role,
                  'роль пользователя')
        t.json_hasnt('user.qrcode', 'qrcode нет')

        await t.post_ok('api_admin_users_load',
                        json={'user_id': executer.user_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_is('user.user_id',
                  executer.user_id,
                  'идентификатор пользователя')
        t.json_is('user.role',
                  executer.role,
                  'роль пользователя')
        t.json_has('user.qrcode', 'qrcode есть')


async def test_role_editable(tap, api, dataset):
    with tap.plan(10):
        t = await api(role='admin')

        user_ya = await dataset.user(provider='yandex-team')

        user_fr = await dataset.user(provider='yandex')

        await t.post_ok('api_admin_users_load',
                        json={'user_id': user_ya.user_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_is('user.user_id', user_ya.user_id,
                  'идентификатор пользователя')
        t.json_is('user.role_editable', False, 'нельзя менять роль')

        await t.post_ok('api_admin_users_load',
                        json={'user_id': user_fr.user_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код')
        t.json_is('user.user_id', user_fr.user_id,
                  'идентификатор пользователя')
        t.json_is('user.role_editable', True, 'можно менять роль')
