import pytest

from stall.model.user import User


async def test_save(tap, api, dataset):
    with tap.plan(30):
        guest = await dataset.user(role='authen_guest', store_id=None)
        tap.ok(guest, 'пользователь создан')
        tap.eq(guest.company_id, None, 'Организации нет')
        tap.eq(guest.store_id, None, 'Склада нет')

        admin = await dataset.user(role='admin')
        tap.ok(admin, 'админ создан')
        tap.eq(admin.role, 'admin', 'роль')
        tap.ok(admin.company_id, 'организация назначена')
        tap.ok(admin.store_id, 'склад назначен')

        t = await api()

        await t.post_ok('api_admin_users_save',
                        json={
                            'user_id': guest.user_id,
                            'role': 'admin',
                        })
        t.status_is(401, diag=True, desc='Неавторизованному нельзя')

        t.set_user(admin)

        await t.post_ok('api_admin_users_save',
                        json={
                            'user_id': guest.user_id,
                            'role': 'admin',
                            'lang': 'fr_FR',
                        })
        t.status_is(200, diag=True, desc='Сохранили новую роль')
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('user', 'пользователь в ответе')

        t.json_is('user.role', 'admin', 'он теперь админ')
        t.json_is('user.lang', 'fr_FR')

        loaded = await User.load(guest.user_id)
        tap.ok(loaded, 'Загрузили')
        tap.eq(loaded.role, 'admin', 'роль в БД поменялась')
        tap.eq(loaded.company_id, admin.company_id, 'Организация назначена')
        tap.eq(loaded.store_id, None, 'Склад пока не назначен')

        await t.post_ok('api_admin_users_save',
                        json={
                            'user_id': guest.user_id,
                            'store_id': admin.store_id,
                            'role': 'admin',
                        })
        t.status_is(200, diag=True, desc='Сохранили новую роль')
        t.json_is('code', 'OK', 'код ответа')
        t.json_has('user', 'пользователь в ответе')

        t.json_is('user.company_id', admin.company_id, 'Организация назначена')
        t.json_is('user.store_id', admin.store_id, 'Склад назначен')

        loaded = await User.load(guest.user_id)
        tap.ok(loaded, 'Загрузили')
        tap.eq(loaded.role, 'admin', 'роль в БД поменялась')
        tap.ok(loaded.store_id, 'Склад есть')
        tap.eq(loaded.company_id, admin.company_id, 'Он тот что назначили')
        tap.eq(loaded.store_id, admin.store_id, 'Он тот что назначили')


async def test_save_guest(tap, api, dataset):
    with tap.plan(19):
        guest = await dataset.user(store_id=None, role='authen_guest')
        tap.ok(guest, 'гость создан')
        tap.eq(guest.store_id, None, 'вне склада')

        user = await dataset.user(role='store_admin')
        tap.ok(user, 'пользователь создан')
        tap.ok(user.store_id, 'склад есть')
        tap.eq(user.role, 'store_admin', 'админ склада')

        t = await api()
        t.set_user(user)

        await t.post_ok('api_admin_users_save',
                        json={
                            'user_id': guest.user_id,
                            'role': 'admin',
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'нельзя создать админа')
        t.json_is('message', 'Access denied', 'сообщение об ошибке')
        # TODO подумать о ролях
        await t.post_ok('api_admin_users_save',
                        json={
                            'user_id': guest.user_id,
                            'role': 'vice_store_admin',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'А роль из sub можно')
        t.json_is('user.role', 'vice_store_admin', 'новая роль пользователя')
        t.json_is('user.user_id', guest.user_id, 'идентификатор')
        t.json_is('user.store_id', user.store_id, 'назначился склад')

        other = await dataset.user(role='store_admin')
        tap.ok(other, 'другой админ склада')
        t.set_user(other)

        await t.post_ok('api_admin_users_save',
                        json={
                            'user_id': guest.user_id,
                            'role': 'vice_store_admin',
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'Другой админ потерял право')


async def test_update_guest(tap, api, dataset):
    with tap:
        guest = await dataset.user(store_id=None, role='authen_guest')
        tap.ok(guest, 'гость создан')
        tap.eq(guest.store_id, None, 'вне склада')

        user = await dataset.user(role='admin')
        tap.ok(user, 'пользователь создан')
        tap.ok(user.store_id, 'склад есть')
        tap.eq(user.role, 'admin', 'админ склада')

        t = await api()
        t.set_user(user)

        # TODO подумать о ролях
        await t.post_ok('api_admin_users_save',
                        json={
                            'user_id': guest.user_id,
                            'role': 'supervisor',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'А роль из sub можно')
        t.json_is('user.role', 'supervisor', 'новая роль пользователя')
        t.json_is('user.user_id', guest.user_id, 'идентификатор')
        t.json_is('user.store_id', None, 'склад не назначен')
        t.json_is('user.company_id', user.company_id, 'назначилась компания')

        other = await dataset.user(role='store_admin')
        tap.ok(other, 'другой админ склада')
        t.set_user(other)

        await t.post_ok('api_admin_users_save',
                        json={
                            'user_id': guest.user_id,
                            'role': 'executer',
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'Другой админ потерял право')


async def test_change_barcode(tap, api, dataset):
    with tap.plan(7):
        guest = await dataset.user(role='authen_guest', store_id=None)
        tap.ok(guest, 'пользователь создан')
        tap.eq(guest.store_id, None, 'Склада нет')
        t = await api(role='admin')

        await t.post_ok('api_admin_users_save',
                        json={
                            'user_id': guest.user_id,
                            'change_barcode': True,
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_isnt('user.qrcode', guest.qrcode, 'qrcode поменялся')
        t.json_isnt('user.pin', guest.pin, 'pin поменялся')


@pytest.mark.parametrize('role', ['store_admin', 'admin'])
async def test_create_internal_user(tap, api, dataset, role, uuid):
    with tap.plan(14, 'Создание локального пользователя'):
        store = await dataset.store()
        user = await dataset.user(role=role, store=store)

        email_pd_id = uuid()
        phone_pd_id = uuid()

        t = await api(user=user)
        await t.post_ok('api_admin_users_save',
                        json={
                            'role': 'executer',
                            'email': 'vasya@yandex.ru',
                            'email_pd_id': email_pd_id,
                            'phone': '+79091234567',
                            'phone_pd_id': phone_pd_id,
                            'nick': 'vasya',
                            'fullname': 'Василий Задов',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('user.provider', 'internal')
        t.json_is('user.store_id', store.store_id)
        t.json_is('user.user_assign', user.user_id)
        t.json_is('user.email', 'vasya@yandex.ru')
        t.json_is('user.phone', '+79091234567')
        t.json_is('user.email_pd_id', email_pd_id)
        t.json_is('user.phone_pd_id', phone_pd_id)

        new_user_id = t.res['json']['user']['user_id']
        await t.post_ok('api_admin_users_save',
                        json={
                            'user_id': new_user_id,
                            'fullname': 'Пётр Тракторенко',
                            'user_assign': 'hello',
                        })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('user.user_assign', user.user_id)


async def test_fail_create(tap, api, dataset, uuid):
    with tap.plan(6, 'Ошибка создания'):
        store = await dataset.store()
        user = await dataset.user(role='admin', store=store)

        t = await api(user=user)
        await t.post_ok('api_admin_users_save',
                        json={
                            'role': 'expansioner_ro',
                            'email': 'vasya@yandex.ru',
                            'email_pd_id': uuid(),
                            'nick': 'vasya',
                            'fullname': 'Василий Задов',
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        user2 = await dataset.user(role='admin_ro', store=store)
        t = await api(user=user2)
        await t.post_ok('api_admin_users_save',
                        json={
                            'role': 'executer',
                            'email': 'vasya@yandex.ru',
                            'email_pd_id': uuid(),
                            'nick': 'vasya',
                            'fullname': 'Василий Задов',
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_unknown_store(tap, api, dataset, uuid):
    with tap.plan(3):
        user = await dataset.user(role='admin')
        t = await api(role='admin')

        await t.post_ok('api_admin_users_save',
                        json={
                            'user_id': user.user_id,
                            'nick': 'vasya',
                            'fullname': 'Василий Задов',
                            'store_id': uuid(),
                        })
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')


async def test_fail_change_store(tap, api, dataset):
    store = await dataset.store()
    store2 = await dataset.store()
    user = await dataset.user(
        role='executer', store=store, provider='internal')
    t = await api(role='admin')
    with tap.plan(3):
        await t.post_ok('api_admin_users_save',
                        json={
                            'user_id': user.user_id,
                            'nick': 'vasya',
                            'fullname': 'Василий Задов',
                            'store_id': store2.store_id
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


async def test_stores_allow(tap, api, dataset, uuid):
    with tap.plan(5, 'админ может назначить разрешенные лавки'):
        user = await dataset.user(role='supervisor')

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_users_save',
            json={
                'user_id': user.user_id,
                'stores_allow': [uuid(), uuid()],
            })
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('user.stores_allow.0')
        t.json_has('user.stores_allow.1')


async def test_clusters_allow(tap, api, uuid, dataset):
    with tap.plan(9, 'теряем доступ к стору из-за кластеров'):
        cluster1_name = uuid()
        cluster2_name = uuid()
        store = await dataset.store(cluster=cluster1_name)

        user = await dataset.user(
            role='supervisor',
            clusters_allow=[cluster1_name, cluster2_name, uuid()],
            store_id=None,
        )
        await user.reload()
        tap.ok(not user.store_id, 'юзер не привязан к стору')

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_users_save',
            json={
                'user_id': user.user_id,
                'clusters_allow': [cluster1_name, cluster2_name],
            },
        )
        t.status_is(200, diag=True)

        await t.post_ok(
            'api_admin_users_save',
            json={'user_id': user.user_id, 'store_id': store.store_id},
        )

        t.status_is(200, diag=True)
        t.json_is('user.store_id', store.store_id)

        await t.post_ok(
            'api_admin_users_save',
            json={'user_id': user.user_id, 'clusters_allow': [cluster2_name]},
        )
        t.status_is(200, diag=True)
        t.json_is('user.store_id', None)


async def test_set_authen_guest(tap, api, dataset, uuid):
    with tap:
        user = await dataset.user(
            role='admin',
            clusters_allow=[uuid()],
            stores_allow=[uuid()],
        )
        tap.ok(user, 'user created')
        tap.ok(user.company_id, 'user has company')
        tap.ok(user.store_id, 'user has store')
        tap.ok(user.clusters_allow, 'user has clusters_allow')
        tap.ok(user.stores_allow, 'user has stores_allow')

        t = await api(role='admin')
        await t.post_ok('api_admin_users_save',
                        json={
                            'user_id': user.user_id,
                            'role': 'authen_guest',
                        })

        t.status_is(200, diag=True, desc='Сохранили новую роль')
        t.json_is('code', 'OK')
        t.json_has('user', 'пользователь в ответе')
        t.json_is('user.role', 'authen_guest')

        await user.reload()
        tap.ok(not user.company_id, 'user has not company')
        tap.ok(not user.store_id, 'user has not store')
        tap.ok(not user.clusters_allow, 'user has not clusters_allow')
        tap.ok(not user.stores_allow, 'user has not stores_allow')


async def test_change_super_role(tap, api, dataset):
    with tap.plan(11):
        user = await dataset.user(role='admin')
        t = await api(role='admin')

        await t.post_ok('api_admin_users_save',
                        json={
                            'user_id': user.user_id,
                            'super_role': 'store_admin',
                        })

        t.status_is(200, diag=True, desc='Сохранили новую роль')
        t.json_is('code', 'OK')
        t.json_has('user', 'пользователь в ответе')
        t.json_is('user.super_role', 'store_admin')

        loaded = await User.load(user.user_id)
        tap.ok(loaded, 'Загрузили')
        tap.eq(loaded.super_role, 'store_admin', 'роль в БД поменялась')

        t = await api(role='support')
        await t.post_ok('api_admin_users_save',
                        json={
                            'user_id': user.user_id,
                            'super_role': 'store_admin',
                        })
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_has('message', 'Permission required to change super_role')


@pytest.mark.parametrize('provider', ['yandex-team', 'yandex'])
async def test_set_role(tap, api, dataset, provider):
    with tap:
        user = await dataset.user(role='authen_guest', provider=provider)
        t = await api(role='admin')

        await t.post_ok('api_admin_users_save',
                        json={
                            'user_id': user.user_id,
                            'role': 'store_admin',
                        })

        loaded = await User.load(user.user_id)
        tap.ok(loaded, 'Загрузили пользователя')

        if provider == 'yandex':
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_is('user.role', 'store_admin',
                      'Выставили роль (не Yandex-Team)')

            tap.eq(loaded.role, 'store_admin',
                   'в БД новая роль (не Yandex-Team)')
        else:
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

            tap.eq(loaded.role, 'authen_guest',
                   'роль в БД не поменялась (Yandex-Team)')


async def test_store_company_ya_team(tap, api, dataset):
    with tap:
        store1 = await dataset.store()
        store2 = await dataset.store()
        user = await dataset.user(role='store_admin', provider='yandex-team',
                                  store_id=store1.store_id,
                                  company_id=store1.company_id)
        t = await api(role='admin')

        await t.post_ok('api_admin_users_save',
                        json={
                            'user_id': user.user_id,
                            'store_id': store2.store_id,
                            'company_id': store2.company_id,
                        })

        loaded = await User.load(user.user_id)
        tap.ok(loaded, 'Загрузили пользователя')

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        tap.eq_ok(loaded.store_id, store1.store_id, 'Склад не поменялся')
        tap.eq_ok(loaded.company_id, store1.company_id,
                  'Компания не поменялась')


# pylint: disable=too-many-statements,too-many-locals
@pytest.mark.parametrize(
    ['company_users_manage', 'store_users_manage', 'expected_ok'], [
        (None, None, True),
        (None, 'external', False),
        (None, 'internal', True),
        ('external', None, False),
        ('external', 'external', False),
        ('external', 'internal', True),
        ('internal', None, True),
        ('internal', 'external', False),
        ('internal', 'internal', True),
    ]
)
async def test_users_manage_create(
        tap, api, dataset, uuid,
        company_users_manage, store_users_manage, expected_ok,
):
    with tap:
        company = await dataset.company()
        tap.ok(company, 'company created')

        if company_users_manage:
            company.users_manage = company_users_manage
            await company.save()

        store = await dataset.store(company=company)
        tap.ok(store, 'store created')

        if store_users_manage:
            store.users_manage = store_users_manage
            await store.save()

        user = await dataset.user(store=store, role='store_admin')
        tap.ok(user, 'store_admin created')

        c_user = await dataset.user(store=store, role='company_admin')
        tap.ok(c_user, 'company_admin created')

        t = await api(user=user)
        c_t = await api(user=c_user)

        # Пытаемся создать пользователя директором лавки
        #
        await t.post_ok(
            'api_admin_users_save',
            json={
                'role': 'stocktaker',
                'email': 'test@yandex-team.ru',
                'email_pd_id': uuid(),
                'nick': 'user-1',
                'fullname': 'Пользователь 1',
            }
        )

        if expected_ok:
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('user')

            user_id = t.res['json']['user']['user_id']
        else:
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

            # Если не смогли от директора лавки,
            # создаём директором компании
            #
            await c_t.post_ok(
                'api_admin_users_save',
                json={
                    'role': 'stocktaker',
                    'email': 'test@yandex-team.ru',
                    'email_pd_id': uuid(),
                    'nick': 'user-1',
                    'fullname': 'Пользователь 1',
                }
            )

            c_t.status_is(200, diag=True)
            c_t.json_is('code', 'OK')
            c_t.json_has('user')

            user_id = c_t.res['json']['user']['user_id']

        # Пытаемся изменить юзера директором лавки
        #
        await t.post_ok(
            'api_admin_users_save',
            json={
                'user_id': user_id,
                'phone': '88005553535',
            }
        )

        if expected_ok:
            t.status_is(200, diag=True, desc='update request')
            t.json_is('code', 'OK')
            t.json_has('user')
            t.json_is('user.user_id', user_id)
        else:
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

            # Если не смогли от директора лавки,
            # пытаемся изменить директором компании
            #
            await c_t.post_ok(
                'api_admin_users_save',
                json={
                    'user_id': user_id,
                    'phone': '88005553535',
                }
            )

            c_t.status_is(200, diag=True)
            c_t.json_is('code', 'OK')
            c_t.json_has('user')
            c_t.json_is('user.user_id', user_id)

        # Изменить статус может каждый
        #
        await t.post_ok(
            'api_admin_users_save',
            json={
                'user_id': user_id,
                'status': 'disabled',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('user')
        t.json_is('user.user_id', user_id)
        t.json_is('user.status', 'disabled')

        # Менять ничего тоже может каждый
        #
        await t.post_ok(
            'api_admin_users_save',
            json={'user_id': user_id}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('user')
        t.json_is('user.user_id', user_id)


async def test_set_store(tap, dataset, api):
    with tap.plan(23, 'Прикрепление юзера к складу'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        store = await dataset.store(company=company, users_manage='external')
        tap.ok(store, 'store created')

        admin = await dataset.user(store=store, role='store_admin')
        tap.ok(admin, 'store_admin created')

        t = await api(user=admin)

        # can set store to internal user without store
        #
        user = await dataset.user(company_id=company.company_id,
                                  store_id=None,
                                  provider='internal',
                                  role='executer')
        tap.ok(user, 'user created')
        tap.is_ok(user.store_id, None, 'user has not store')

        await t.post_ok(
            'api_admin_users_save',
            json={'user_id': user.user_id}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('user')
        t.json_is('user.store_id', admin.store_id)

        await user.reload()
        tap.eq(user.store_id, admin.store_id, 'store set')

        # cannot set store to user from foreign company
        #
        foreign_user = await dataset.user(store_id=None,
                                          provider='internal',
                                          role='executer')
        tap.ok(foreign_user, 'foreign user created')
        tap.ne(foreign_user.company_id, company.company_id,
               'user from foreign company')

        await t.post_ok(
            'api_admin_users_save',
            json={'user_id': foreign_user.user_id}
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        await user.reload()
        tap.is_ok(foreign_user.store_id, None, 'store still not set')

        # cannot set store to user from foreign store
        #
        user_with_store = await dataset.user(company_id=company.company_id,
                                             provider='internal',
                                             role='executer')
        tap.ok(user_with_store, 'user with store_created')
        tap.ne(user_with_store.store_id, store.store_id,
               'user from foreign store')

        foreign_store_id = user_with_store.store_id

        await t.post_ok(
            'api_admin_users_save',
            json={'user_id': user_with_store.user_id}
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        await user.reload()
        tap.eq(user_with_store.store_id, foreign_store_id,
               'store not changed')


async def test_set_store_admin(tap, dataset, api):
    with tap.plan(14, 'прикрепляем пользователя к складу '
                      'если склада ещё нет'):
        store = await dataset.store()
        tap.ok(store, 'store created')

        store_2 = await dataset.store(company_id=store.company_id)
        tap.ok(store_2, 'store_2 created')

        user = await dataset.user(store_id=store.store_id,
                                  company_id=store.company_id,
                                  role='executer',
                                  provider='internal')
        tap.ok(user, 'user created')

        user_2 = await dataset.user(store_id=None,
                                    company_id=store.company_id,
                                    role='executer',
                                    provider='internal')
        tap.ok(user, 'user_2 created')

        admin = await dataset.user(store_id=store.store_id,
                                   company_id=store.company_id,
                                   role='admin')
        tap.ok(admin, 'admin created')

        t = await api(user=admin)
        await t.post_ok('api_admin_users_save', json={
            'user_id': user.user_id,
            'store_id': store_2.store_id,
        })

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        await user.reload()

        tap.eq(user.store_id, store.store_id, 'store_id not changed')

        await t.post_ok('api_admin_users_save', json={
            'user_id': user_2.user_id,
            'store_id': store_2.store_id,
        })

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('user.store_id', store_2.store_id)

        await user_2.reload()

        tap.eq(user_2.store_id, store_2.store_id, 'store_id changed')


async def test_activate_user(tap, dataset, api):
    with tap.plan(22, 'Работа пермита активации и смены ролей'):
        store = await dataset.store()
        admin = await dataset.user(store=store, role='admin')
        t = await api(user=admin)
        user = await dataset.user(
            company_id=store.company_id,
            store_id=None,
            provider='internal',
            role='executer',
            status='disabled'
        )
        vice_store = await dataset.user(
            company_id=store.company_id,
            store_id=None,
            provider='internal',
            role='vice_store_admin',
            status='disabled'
        )
        admin.role.add_permit('sub_exclude_activate', ['executer'])
        await t.post_ok(
            'api_admin_users_save',
            json={
                'user_id': user.user_id,
                'status': 'active'
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
        t.json_hasnt('user')

        await t.post_ok(
            'api_admin_users_save',
            json={
                'user_id': user.user_id,
                'role': 'vice_store_admin'
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        await t.post_ok(
            'api_admin_users_save',
            json={
                'user_id': vice_store.user_id,
                'role': 'executer'
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        await user.reload()
        tap.eq(user.status, 'disabled', 'Все еще выключен')
        tap.eq(user.role, 'executer', 'Все еще кладовщик')
        admin.role.remove_permit('sub_exclude_activate')

        await t.post_ok(
            'api_admin_users_save',
            json={
                'user_id': user.user_id,
                'status': 'active',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await user.reload()
        tap.eq(user.status, 'active', 'Теперь активный')

        admin.role.remove_permit('users_activate')
        await t.post_ok(
            'api_admin_users_save',
            json={
                'user_id': user.user_id,
                'status': 'active',
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await t.post_ok(
            'api_admin_users_save',
            json={
                'user_id': vice_store.user_id,
                'role': 'executer'
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
