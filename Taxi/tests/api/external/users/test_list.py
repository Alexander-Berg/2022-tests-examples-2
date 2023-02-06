async def test_empty(tap, dataset, api):
    with tap.plan(8, 'пустой список пользователей'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_list',
                        json={'cursor': None})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('cursor', None)
        t.json_has('users')
        t.json_hasnt('users.0')


async def test_one(tap, dataset, api, uuid):
    with tap.plan(27, 'по одному пользователю на компанию'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        user = await dataset.user(
            company=company,
            provider='internal',
            role='executer',
            nick='Masorubka_1',
            phone_pd_id=uuid(),
        )
        tap.ok(user, 'user created')

        company_2 = await dataset.company()
        tap.ok(company_2, 'company_2 created')

        user_2 = await dataset.user(company=company_2,
                                    provider='internal',
                                    role='executer',
                                    nick='Masorubka_2')
        tap.ok(user_2, 'user_2 created')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_list',
                        json={'cursor': None})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('cursor', None)
        t.json_has('users')
        t.json_has('users.0')
        t.json_is('users.0.user_id', user.user_id)
        t.json_is('users.0.company_id', company.company_id)
        t.json_is('users.0.nick', user.nick)
        t.json_is('users.0.phone_pd_id', user.phone_pd_id)
        t.json_hasnt('users.1')

        t = await api(token=company_2.token)
        await t.post_ok('api_external_users_list',
                        json={'cursor': None})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('cursor', None)
        t.json_has('users')
        t.json_has('users.0')
        t.json_is('users.0.user_id', user_2.user_id)
        t.json_is('users.0.company_id', company_2.company_id)
        t.json_is('users.0.nick', user_2.nick)
        t.json_hasnt('users.1')


async def test_many(tap, dataset, api):
    with tap.plan(27, 'несколько пользователей у компании'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        user = await dataset.user(company=company,
                                  provider='internal', role='executer')
        tap.ok(user, 'user created')

        company_2 = await dataset.company()
        tap.ok(company_2, 'company_2 created')

        user_2 = await dataset.user(company=company_2,
                                    provider='internal', role='executer')
        tap.ok(user_2, 'user_2 created')

        user_3 = await dataset.user(company=company,
                                    provider='internal', role='executer')
        tap.ok(user_3, 'user_3 created')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_list',
                        json={'cursor': None})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('cursor', None)
        t.json_has('users')
        t.json_has('users.0')
        t.json_is('users.0.company_id', company.company_id)
        t.json_has('users.1')
        t.json_is('users.1.company_id', company.company_id)
        t.json_hasnt('users.2')

        tap.eq({
            t.res['json']['users'][0]['user_id'],
            t.res['json']['users'][1]['user_id'],
        }, {
            user.user_id, user_3.user_id
        }, 'returned company users')

        t = await api(token=company_2.token)
        await t.post_ok('api_external_users_list',
                        json={'cursor': None})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('cursor', None)
        t.json_has('users')
        t.json_has('users.0')
        t.json_is('users.0.user_id', user_2.user_id)
        t.json_is('users.0.company_id', company_2.company_id)
        t.json_hasnt('users.1')


async def test_subscribe(tap, dataset, api):
    with tap.plan(11, 'подписка на лист'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        user = await dataset.user(company=company,
                                  provider='internal', role='executer')
        tap.ok(user, 'user created')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_list',
                        json={'cursor': None, 'subscribe': True})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_isnt('cursor', None)
        t.json_has('users')
        t.json_has('users.0')
        t.json_is('users.0.user_id', user.user_id)
        t.json_is('users.0.company_id', company.company_id)


# pylint: disable=too-many-statements
async def test_role_filter(tap, dataset, api):
    with tap.plan(55, 'фильтр по роли. '
                      'возвращаем только если provider=internal'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        user = await dataset.user(company=company,
                                  provider='internal', role='executer')
        tap.ok(user, 'user created')

        user_2 = await dataset.user(company=company,
                                    provider='internal', role='courier')
        tap.ok(user_2, 'courier created')

        user_3 = await dataset.user(company=company,
                                    provider='test', role='executer')
        tap.ok(user_3, 'with test provider created')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_list',
                        json={'cursor': None, 'role': ['executer']})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('cursor', None)
        t.json_has('users')
        t.json_has('users.0')
        t.json_is('users.0.user_id', user.user_id)
        t.json_is('users.0.company_id', company.company_id)
        t.json_hasnt('users.1')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_list',
                        json={'cursor': None, 'role': ['courier']})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('cursor', None)
        t.json_has('users')
        t.json_has('users.0')
        t.json_is('users.0.user_id', user_2.user_id)
        t.json_is('users.0.company_id', company.company_id)
        t.json_hasnt('users.1')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_list',
                        json={'cursor': None, 'role': ['stocktaker']})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('cursor', None)
        t.json_has('users')
        t.json_hasnt('users.0')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_list',
                        json={'cursor': None, 'role': ['executer', 'courier']})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('cursor', None)
        t.json_has('users')
        t.json_has('users.0')
        t.json_is('users.0.company_id', company.company_id)
        t.json_has('users.1')
        t.json_is('users.1.company_id', company.company_id)
        t.json_hasnt('users.2')

        tap.eq({
            t.res['json']['users'][0]['user_id'],
            t.res['json']['users'][1]['user_id'],
        }, {
            user.user_id, user_2.user_id
        }, 'returned both users')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_list',
                        json={'cursor': None})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('cursor', None)
        t.json_has('users')
        t.json_has('users.0')
        t.json_is('users.0.company_id', company.company_id)
        t.json_has('users.1')
        t.json_is('users.1.company_id', company.company_id)
        t.json_hasnt('users.2')

        tap.eq({
            t.res['json']['users'][0]['user_id'],
            t.res['json']['users'][1]['user_id'],
        }, {
            user.user_id, user_2.user_id
        }, 'returned all users')



async def test_wrong_token(tap, dataset, api, uuid):
    with tap.plan(12, 'авторизация только по токену компании'):
        t = await api(token=uuid())
        await t.post_ok('api_external_users_list',
                        json={'cursor': None, 'subscribe': True})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        t = await api(role='executer')
        await t.post_ok('api_external_users_list',
                        json={'cursor': None, 'subscribe': True})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        user = await dataset.user()
        t = await api(user=user)
        await t.post_ok('api_external_users_list',
                        json={'cursor': None, 'subscribe': True})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        t = await api(role='token:web.external.tokens.0')
        await t.post_ok('api_external_users_list',
                        json={'cursor': None, 'subscribe': True})
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_COMPANY_TOKEN')


async def test_store_admin(tap, dataset, api):
    with tap.plan(32, 'store_admin и vice_store_admin'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        user = await dataset.user(company=company,
                                  provider='internal', role='store_admin')
        tap.ok(user, 'store_admin created')

        user_2 = await dataset.user(company=company, nick='фея флора',
                                    provider='internal', role='courier')
        tap.ok(user_2, 'courier created')

        user_3 = await dataset.user(company=company, nick='фея стелла',
                                    provider='test', role='vice_store_admin')
        tap.ok(user_3, 'vice_store_admin created')

        user_4 = await dataset.user(company=company,
                                    provider='test', role='courier')
        tap.ok(user_4, 'courier created')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_list',
                        json={'cursor': None})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('cursor', None)
        t.json_has('users')
        t.json_has('users.0')
        t.json_has('users.1')
        t.json_has('users.2')
        t.json_is('users.0.company_id', company.company_id)
        t.json_is('users.1.company_id', company.company_id)
        t.json_is('users.2.company_id', company.company_id)
        t.json_hasnt('users.3')

        tap.eq({
            t.res['json']['users'][0]['user_id'],
            t.res['json']['users'][1]['user_id'],
            t.res['json']['users'][2]['user_id']
        }, {
            user.user_id, user_2.user_id, user_3.user_id
        }, 'returned suitable users')

        t = await api(token=company.token)
        await t.post_ok('api_external_users_list',
                        json={'cursor': None,
                              'role': ['courier', 'vice_store_admin']})

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('cursor')
        t.json_is('cursor', None)
        t.json_has('users')
        t.json_has('users.0')
        t.json_has('users.1')
        t.json_is('users.0.company_id', company.company_id)
        t.json_is('users.1.company_id', company.company_id)
        t.json_hasnt('users.2')

        tap.eq({
            t.res['json']['users'][0]['user_id'],
            t.res['json']['users'][1]['user_id'],
        }, {
            user_2.user_id, user_3.user_id
        }, 'returned suitable users')

        tap.eq({
            t.res['json']['users'][0]['nick'],
            t.res['json']['users'][1]['nick'],
        }, {
            user_2.nick, user_3.nick
        }, 'returned right nicks')
