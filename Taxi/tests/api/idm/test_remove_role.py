from urllib.parse import quote


async def test_bad_requests(tap, api):
    with tap.plan(28):
        t = await api(role='token:web.idm.tokens.0')

        await t.post_ok('/api/idm/remove-role/', form={})
        t.status_is(200, diag=True)
        t.json_is('code', 400)
        t.json_is('error', 'login is not specified')

        await t.post_ok('/api/idm/remove-role/', form={
            'login': 'login1',
        })
        t.status_is(200, diag=True)
        t.json_is('code', 400)
        t.json_is('error', 'uid is not specified')

        await t.post_ok('/api/idm/remove-role/', form={
            'login': 'login1',
            'uid': '534535345342',
        })
        t.status_is(200, diag=True)
        t.json_is('code', 400)
        t.json_is('error', 'role is not specified')

        await t.post_ok('/api/idm/remove-role/', form={
            'login': 'login1',
            'uid': '534535345342',
            'role': '{"role": "store_admin"}',
        })
        t.status_is(200, diag=True)
        t.json_is('code', 400)
        t.json_is('error', 'path is not specified')

        await t.post_ok('/api/idm/remove-role/', form={
            'login': 'login1',
            'uid': '534535345342',
            'role': 'abrakadbra',
            'path': quote('/role/abrakadabra/', safe=''),
        })
        t.status_is(200, diag=True)
        t.json_is('code', 400)
        t.json_is('error', 'Bad role')

        await t.post_ok('/api/idm/remove-role/', form={
            'login': 'login1',
            'uid': '534535345342',
            'role': '{"hello": "world"}',
            'path': quote('/hello/world/', safe=''),
        })
        t.status_is(200, diag=True)
        t.json_is('code', 400)
        t.json_is('error', 'Bad role')

        await t.post_ok('/api/idm/remove-role/', form={
            'login': 'login1',
            'uid': '534535345342',
            'role': '{"role": "emperor_of_the_universe"}',
            'path': quote('/role/emperor_of_the_universe/', safe=''),
        })
        t.status_is(200, diag=True)
        t.json_is('code', 400)
        t.json_is('error', 'Bad role')


async def test_remove_role(tap, api, dataset):
    with tap.plan(6):
        t = await api(role='token:web.idm.tokens.0')

        company = await dataset.company(ownership='yandex')
        user = await dataset.user(role='store_admin',
                                  provider='yandex-team',
                                  company_id=company.company_id)

        await t.post_ok('/api/idm/remove-role/', form={
            'login': 'login1',
            'uid': user.provider_user_id,
            'role': '{"role": "store_admin"}',
            'path': quote('/role/store_admin/', safe=''),
        })
        t.status_is(200, diag=True)
        t.json_is('code', 0)

        await user.reload()

        tap.eq(user.role.name, 'authen_guest', 'Роль поменялась')
        tap.eq(user.company_id, None, 'Нет компании')
        tap.eq(user.store_id, None, 'Нет склада')


async def test_remove_non_existent_role(tap, api, dataset):
    with tap.plan(6):
        t = await api(role='token:web.idm.tokens.0')

        company = await dataset.company(ownership='yandex')
        store = await dataset.store(company_id=company.company_id)
        user = await dataset.user(role='store_admin',
                                  provider='yandex-team',
                                  store_id=store.store_id,
                                  company_id=company.company_id)

        await t.post_ok('/api/idm/remove-role/', form={
            'login': 'login1',
            'uid': user.provider_user_id,
            'role': '{"role": "vice_store_admin"}',
            'path': quote('/role/vice_store_admin/', safe=''),
        })
        t.status_is(200, diag=True)
        t.json_is('code', 0)

        await user.reload()

        tap.eq(user.role.name, 'store_admin', 'Роль не поменялась')
        tap.eq(user.company_id, company.company_id, 'компания не поменялась')
        tap.eq(user.store_id, store.store_id, 'склад не поменялся')


async def test_user_not_found(tap, api, uuid):
    with tap.plan(4):
        t = await api(role='token:web.idm.tokens.0')

        await t.post_ok('/api/idm/remove-role/', form={
            'login': 'login1',
            'uid': uuid(),
            'role': '{"role": "store_admin"}',
            'path': quote('/role/store_admin/', safe=''),
        })
        t.status_is(200, diag=True)
        t.json_is('code', 404)
        t.json_is('error', 'User not found')
