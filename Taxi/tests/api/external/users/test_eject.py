async def test_common(tap, dataset, api):
    with tap.plan(11, 'открепление от склада'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        store = await dataset.store(company=company)
        tap.ok(store, 'store created')

        user = await dataset.user(store=store,
                                  provider='internal', role='executer')
        tap.ok(user, 'user created')

        old_qr = user.qrcode

        t = await api(token=company.token)
        await t.post_ok('api_external_users_eject',
                        json={'user_id': user.user_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('user')
        t.json_is('user.user_id', user.user_id)
        t.json_is('user.store_id', None)

        await user.reload()
        tap.is_ok(user.store_id, None, 'ejected')
        tap.ne(user.qrcode, old_qr, 'qr code changed')


async def test_foreign_user(tap, dataset, api):
    with tap.plan(6, 'попытка отвязать чужого пользователя'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        user = await dataset.user(provider='internal', role='executer')
        tap.ok(user, 'user created')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_eject',
                        json={'user_id': user.user_id})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_USER_ACCESS')

        await user.reload()
        tap.ok(user.store_id, 'user has store')


async def test_unknown_user(tap, dataset, api, uuid):
    with tap.plan(4, 'попытка отвязать несуществующего пользователя'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_eject',
                        json={'user_id': uuid()})

        t.status_is(404, diag=True)
        t.json_is('code', 'ER_USER_NOT_FOUND')


async def test_order_exists(tap, dataset, api):
    with tap.plan(7, 'не отвязываем если есть активный заказ'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        store = await dataset.store(company=company)
        tap.ok(store, 'store created')

        user = await dataset.user(store=store,
                                  provider='internal', role='executer')
        tap.ok(user, 'user created')

        await dataset.order(company=company, store=store,
                            users=[user.user_id])

        t = await api(token=company.token)
        await t.post_ok('api_external_users_eject',
                        json={'user_id': user.user_id})

        t.status_is(403, diag='True')
        t.json_is('code', 'ER_USER_HAS_ACTIVE_ORDER')

        await user.reload()
        tap.eq(user.store_id, store.store_id, 'user store not changed')


async def test_order_exists_force(tap, dataset, api):
    with tap.plan(10, 'отвязываем с активным заказом если force'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        store = await dataset.store(company=company)
        tap.ok(store, 'store created')

        user = await dataset.user(store=store,
                                  provider='internal', role='executer')
        tap.ok(user, 'user created')

        await dataset.order(company=company, store=store,
                            users=[user.user_id])

        t = await api(token=company.token)
        await t.post_ok('api_external_users_eject',
                        json={'user_id': user.user_id, 'force': True})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('user')
        t.json_is('user.user_id', user.user_id)
        t.json_is('user.store_id', None)

        await user.reload()
        tap.is_ok(user.store_id, None, 'ejected')


async def test_order_complete(tap, dataset, api):
    with tap.plan(10, 'отвязываем если заказ уже неактивен'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        store = await dataset.store(company=company)
        tap.ok(store, 'store created')

        user = await dataset.user(store=store,
                                  provider='internal', role='executer')
        tap.ok(user, 'user created')

        await dataset.order(company=company, store=store,
                            users=[user.user_id],
                            status='complete')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_eject',
                        json={'user_id': user.user_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('user')
        t.json_is('user.user_id', user.user_id)
        t.json_is('user.store_id', None)

        await user.reload()
        tap.is_ok(user.store_id, None, 'ejected')


async def test_order_with_many_users(tap, dataset, api):
    with tap.plan(8, 'не отвязываем даже если у активного заказа '
                     'есть другие пользователи'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        store = await dataset.store(company=company)
        tap.ok(store, 'store created')

        user = await dataset.user(store=store,
                                  provider='internal', role='executer')
        tap.ok(user, 'user created')

        user_2 = await dataset.user(store=store,
                                    provider='internal', role='executer')
        tap.ok(user_2, 'user_2 created')

        await dataset.order(company=company, store=store,
                            users=[user.user_id, user_2.user_id])

        t = await api(token=company.token)
        await t.post_ok('api_external_users_eject',
                        json={'user_id': user.user_id})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_USER_HAS_ACTIVE_ORDER')

        await user.reload()
        tap.eq(user.store_id, store.store_id, 'not ejected')


async def test_provider_check(tap, dataset, api):
    with tap.plan(8, 'позволяем откреплять только internal'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        store = await dataset.store(company=company)
        tap.ok(store, 'store created')

        user = await dataset.user(store=store)
        tap.ok(user, 'user created')

        old_qr = user.qrcode

        t = await api(token=company.token)
        await t.post_ok('api_external_users_eject',
                        json={'user_id': user.user_id})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_USER_NOT_INTERNAL')

        await user.reload()
        tap.ok(user.store_id, 'not ejected')
        tap.eq(user.qrcode, old_qr, 'qr code changed')


async def test_wrong_token(tap, dataset, api, uuid):
    with tap.plan(12, 'авторизация только по токену компании'):
        t = await api(token=uuid())
        await t.post_ok('api_external_users_eject',
                        json={'user_id': 'asdfasdf'})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        t = await api(role='executer')
        await t.post_ok('api_external_users_eject',
                        json={'user_id': 'asdfasdf'})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        user = await dataset.user()
        t = await api(user=user)
        await t.post_ok('api_external_users_eject',
                        json={'user_id': 'asdfasdf'})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_users_eject',
                        json={'user_id': 'asdfasdf'})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_COMPANY_TOKEN')


async def test_pd(tap, dataset, api, uuid):
    with tap.plan(6, 'Проверка работы с ПД'):
        company = await dataset.company()
        store = await dataset.store(company=company)
        user = await dataset.user(
            store=store,
            provider='internal',
            role='executer',
            phone_pd_id=uuid(),
        )

        t = await api(token=company.token)
        await t.post_ok('api_external_users_eject',
                        json={'user_id': user.user_id})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('user')
        t.json_is('user.user_id', user.user_id)
        t.json_is('user.phone_pd_id', user.phone_pd_id)
