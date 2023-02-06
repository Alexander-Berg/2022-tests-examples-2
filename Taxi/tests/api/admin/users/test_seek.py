# pylint: disable=unused-variable

import pytest


async def test_seek(tap, api, uuid, dataset):
    with tap.plan(36):
        store = await dataset.store()
        tap.ok(store, 'Склад создан')

        users = []

        for _ in range(5):
            user = await dataset.user(role='store_admin',
                                      nick=uuid(),
                                      email='%s@mail.ru' % uuid(),
                                      store=store)
            tap.ok(user, 'Пользователь создан')
            tap.ok(user.email, 'мыло есть')
            tap.ok(user.nick, 'ник есть')
            tap.eq(user.role, 'store_admin', 'Роль')
            tap.eq(user.store_id, store.store_id, 'Склад')
            users.append(user)

        t = await api(role='admin')

        await t.post_ok('api_admin_users_seek',
                        json={'store_id': store.store_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_is('cursor', None, 'Пустой курсор поскольку больше выдачи нет')

        await t.post_ok('api_admin_users_seek',
                        json={'store_id': store.store_id, 'limit': 2})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_isnt('cursor', None, 'При запросе с лимитом - курсор не пустой')


@pytest.mark.parametrize('role', ['admin', 'admin_ro'])
async def test_seek_access(tap, api, uuid, dataset, role):
    with tap.plan(5):
        store = await dataset.store()
        users = [
            await dataset.user(role='store_admin',
                               nick=uuid(),
                               email='%s@mail.ru' % uuid(),
                               store=store)
            for _ in range(5)
        ]
        t = await api(role=role)
        await t.post_ok('api_admin_users_seek',
                        json={'store_id': store.store_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('users', 'Пользователи получены')
        res_users = t.res['json']['users']
        tap.eq_ok(
            sorted([u['user_id'] for u in res_users]),
            sorted([u.user_id for u in users]),
            'Получены'
        )


async def test_seek_access_company(tap, api, dataset):
    with tap.plan(6, 'Доступ только в своей компании'):
        company1 = await dataset.company()
        company2 = await dataset.company()

        store1 = await dataset.store(company=company1)
        store2 = await dataset.store(company=company2)

        user1 = await dataset.user(store=store1, role='store_admin')
        user2 = await dataset.user(store=store2, role='store_admin')

        director = await dataset.user(company=company1, store_id=None)
        with director.role as role:
            role.remove_permit('out_of_company')
            role.add_permit('out_of_store', True)

            t = await api(user=director)

            await t.post_ok(
                'api_admin_users_seek',
                json={'store_id': store1.store_id}
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('users')
            t.json_is('users.0.user_id', user1.user_id)
            t.json_hasnt('users.1')


async def test_seek_by_status(tap, api, uuid, dataset):
    with tap.plan(15, 'Получение пользователей с фильтром по статусу'):
        store = await dataset.store()
        users = [
            await dataset.user(role='store_admin',
                               nick=uuid(),
                               email='%s@mail.ru' % uuid(),
                               store=store)
            for _ in range(5)
        ]
        users.append(
            await dataset.user(role='store_admin',
                               nick=uuid(),
                               email='%s@mail.ru' % uuid(),
                               store=store,
                               status='disabled')
        )
        t = await api(role='admin')
        await t.post_ok('api_admin_users_seek',
                        json={'store_id': store.store_id})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('users', 'Пользователи получены')
        res_users = t.res['json']['users']
        tap.eq_ok(
            sorted([u['user_id'] for u in res_users]),
            sorted([u.user_id for u in users]),
            'Получены'
        )

        for status in ('disabled', 'active'):
            await t.post_ok('api_admin_users_seek',
                            json={
                                'store_id': store.store_id,
                                'status': status,
                            },
                            desc=f'Получаем с фильтром {status}')
            t.status_is(200, diag=True)
            t.json_is('code', 'OK', 'код ответа')
            t.json_has('users', 'Пользователи получены')
            res_users = t.res['json']['users']
            tap.eq_ok(
                sorted([u['user_id'] for u in res_users]),
                sorted([u.user_id for u in users if u.status == status]),
                'Получены'
            )


async def test_seek_stores_allow(tap, api, dataset):
    with tap.plan(6, 'показываем пользователей только из разрешенных лавок'):
        store1 = await dataset.store()
        store1_user = await dataset.user(store=store1, role='store_admin')

        store2 = await dataset.store()
        store2_user = await dataset.user(store=store2, role='executer')

        await dataset.user()

        supervisor = await dataset.user(
            role='supervisor',
            store_id=store1.store_id,
            stores_allow=[store1.store_id, store2.store_id],
        )
        tap.eq_ok(
            supervisor.stores_allow,
            [store1.store_id, store2.store_id],
            'лавка заданы',
        )

        t = await api()
        t.set_user(supervisor)

        await t.post_ok('api_admin_users_seek', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('users', 'пользователи получены')
        tap.eq_ok(
            {i['user_id'] for i in t.res['json']['users']},
            {store1_user.user_id, store2_user.user_id},
            'видим пользователей только из разрешенных лавок',
        )


async def test_qr_bar_codes(tap, api, dataset):
    with tap.plan(13):
        store = await dataset.store()
        tap.ok(store, 'Склад создан')
        store = await dataset.store()
        admin = await dataset.user(role='admin', store=store)
        support = await dataset.user(role='support', store=store)
        await dataset.user(role='executer', store=store)

        t = await api(user=admin)

        await t.post_ok('api_admin_users_seek',
                        json={'store_id': store.store_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_is('cursor', None, 'Пустой курсор поскольку больше выдачи нет')

        users = t.res['json']['users']
        with tap.subtest() as taps:
            for u in users:
                taps.ok(u.get('qrcode'), 'есть qrcode')

        t = await api(user=support)
        await t.post_ok('api_admin_users_seek',
                        json={'store_id': store.store_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('cursor', 'Курсор присутствует')
        t.json_is('cursor', None, 'Пустой курсор поскольку больше выдачи нет')

        users = t.res['json']['users']
        with tap.subtest() as taps:
            for u in users:
                if u['role'] != 'support':
                    taps.ok(u.get('qrcode'), 'есть qrcode')
                else:
                    taps.ok(not u.get('qrcode'), 'нет qrcode')


async def test_providers(tap, api, dataset):
    with tap.plan(
            7,
            'показываем пользователей только из разрешенных поставщиков'
    ):
        provider1 = await dataset.provider()
        user1 = await dataset.user(
            store_id=None, provider=provider1, role='provider')

        provider2 = await dataset.provider()
        user2 = await dataset.user(
            store_id=None, provider=provider2, role='provider')

        user = await dataset.user(
            store_id=None, provider=provider1, role='provider')

        t = await api(user=user)

        await t.post_ok('api_admin_users_seek', json={})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('users', 'пользователи получены')
        t.json_hasnt('users.2', 'только подходящие')

        users = t.res['json']['users']
        users = dict((x['user_id'], x) for x in users)

        tap.ok(users[user1.user_id], 'Пользователь выбранного поставщика')
        tap.ok(users[user.user_id], 'Себя тоже видит')


async def test_provider_id(tap, api, dataset):
    with tap.plan(6, 'фильтр поставщика'):
        provider1 = await dataset.provider()
        user1 = await dataset.user(
            store_id=None, provider=provider1, role='provider')

        provider2 = await dataset.provider()
        user2 = await dataset.user(
            store_id=None, provider=provider2, role='provider')

        user = await dataset.user(role='admin')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_users_seek',
            json={'provider_id': provider1.provider_id}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('users', 'пользователи получены')

        users = t.res['json']['users']
        tap.eq(len(users), 1, 'Только нужные')

        tap.eq(users[0]['user_id'], user1.user_id,
               'Пользователь выбранного поставщика')
