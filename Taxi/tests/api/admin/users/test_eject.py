async def test_common(tap, dataset, api):
    with tap.plan(10, 'открепление пользователя от склада'):
        admin = await dataset.user(role='store_admin')
        tap.ok(admin, 'admin created')

        user = await dataset.user(company_id=admin.company_id,
                                  store_id=admin.store_id,
                                  provider='internal',
                                  role='executer')
        tap.ok(user, 'user created')
        tap.eq(user.store_id, admin.store_id, 'user has store')

        t = await api(user=admin)
        await t.post_ok(
            'api_admin_users_eject',
            json={'user_id': user.user_id}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('user')
        t.json_is('user.user_id', user.user_id)
        t.json_is('user.store_id', None)

        await user.reload()
        tap.is_ok(user.store_id, None, 'user ejected')


async def test_foreign_user(tap, dataset, api):
    with tap.plan(8, 'нельзя открепить чужого пользователя'):
        admin = await dataset.user(role='store_admin')
        tap.ok(admin, 'admin created')

        user = await dataset.user(company_id=admin.company_id,
                                  provider='internal',
                                  role='executer')
        tap.ok(user, 'user created')
        tap.ok(user.store_id, 'user has store')
        tap.ne(user.store_id, admin.store_id, 'user has foreign store')

        old_store_id = user.store_id

        t = await api(user=admin)
        await t.post_ok(
            'api_admin_users_eject',
            json={'user_id': user.user_id}
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        await user.reload()
        tap.eq(user.store_id, old_store_id, 'store not changed')


async def test_not_internal_user(tap, dataset, api):
    with tap.plan(7, 'нельзя открепить не-internal юзера'):
        admin = await dataset.user(role='store_admin')
        tap.ok(admin, 'admin created')

        user = await dataset.user(company_id=admin.company_id,
                                  store_id=admin.store_id,
                                  provider='test', role='executer')
        tap.ok(user, 'user created')
        tap.eq(user.store_id, admin.store_id, 'user has store')

        t = await api(user=admin)
        await t.post_ok(
            'api_admin_users_eject',
            json={'user_id': user.user_id}
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_USER_NOT_INTERNAL')

        await user.reload()
        tap.eq(user.store_id, admin.store_id, 'store not changed')


async def test_user_with_order(tap, dataset, api):
    with tap.plan(12, 'нельзя открепить пользователя с активным заказом.'
                      'но можно, если передать force=True'):
        admin = await dataset.user(role='store_admin')
        tap.ok(admin, 'admin created')

        user = await dataset.user(store_id=admin.store_id,
                                  provider='internal', role='executer')
        tap.ok(user, 'user created')

        await dataset.order(company_id=user.company_id,
                            store_id=user.store_id,
                            users=[user.user_id])

        t = await api(user=admin)

        await t.post_ok(
            'api_admin_users_eject',
            json={'user_id': user.user_id}
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_USER_HAS_ACTIVE_ORDER')

        await t.post_ok(
            'api_admin_users_eject',
            json={'user_id': user.user_id, 'force': True}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('user')
        t.json_is('user.user_id', user.user_id)
        t.json_is('user.store_id', None)

        await user.reload()
        tap.is_ok(user.store_id, None, 'user ejected')


async def test_user_order_complete(tap, dataset, api):
    with tap.plan(9, 'открепляем пользователя с неактивным заказом'):
        admin = await dataset.user(role='store_admin')
        tap.ok(admin, 'admin created')

        user = await dataset.user(store_id=admin.store_id,
                                  provider='internal', role='executer')
        tap.ok(user, 'user created')

        await dataset.order(company_id=user.company_id,
                            store_id=user.store_id,
                            users=[user.user_id],
                            status='complete')

        t = await api(user=admin)
        await t.post_ok(
            'api_admin_users_eject',
            json={'user_id': user.user_id}
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('user')
        t.json_is('user.user_id', user.user_id)
        t.json_is('user.store_id', None)

        await user.reload()
        tap.is_ok(user.store_id, None, 'user ejected')


async def test_user_order_many_users(tap, dataset, api):
    with tap.plan(7, 'не отвязываем даже если у активного заказа '
                     'есть другие пользователи'):
        admin = await dataset.user(role='store_admin')
        tap.ok(admin, 'admin created')

        user = await dataset.user(store_id=admin.store_id,
                                  provider='internal', role='executer')
        tap.ok(user, 'user created')

        user_2 = await dataset.user(store_id=admin.store_id,
                                    provider='internal', role='executer')
        tap.ok(user, 'user_2 created')

        await dataset.order(company_id=user.company_id,
                            store_id=user.store_id,
                            users=[user.user_id, user_2.user_id])

        t = await api(user=admin)
        await t.post_ok(
            'api_admin_users_eject',
            json={'user_id': user.user_id}
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_USER_HAS_ACTIVE_ORDER')

        await user.reload()
        tap.eq(user.store_id, admin.store_id, 'user not ejected')


async def test_unknown_user(tap, dataset, api, uuid):
    with tap.plan(4, 'несуществующий пользователь'):
        admin = await dataset.user(role='store_admin')
        tap.ok(admin, 'admin created')

        t = await api(user=admin)
        await t.post_ok(
            'api_admin_users_eject',
            json={'user_id': uuid()}
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
