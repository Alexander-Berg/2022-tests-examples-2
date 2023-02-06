async def test_save(tap, dataset, api, uuid):
    with tap.plan(20, 'Сохранение'):
        user = await dataset.user(role='admin')

        t = await api(user=user)

        external_id = uuid()

        await t.post_ok(
            'api_admin_companies_save',
            json={
                'external_id': external_id,
                'title': 'привет',
                'products_scope': ['russia'],
                'instance_erp': 'fr',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_has('company.updated')
        t.json_has('company.created')
        t.json_has('company.company_id')
        t.json_is('company.external_id', external_id)
        t.json_is('company.user_id', user.user_id)
        t.json_is('company.title', 'привет')
        t.json_is('company.products_scope', ['russia'])
        t.json_is('company.instance_erp', 'fr')

        company = await dataset.Company.load(
            t.res['json']['company']['company_id'])
        tap.ok(company, 'Объект создан')

        await t.post_ok(
            'api_admin_companies_save',
            json={
                'company_id': company.company_id,
                'title': 'медвед',
                'products_scope': ['israel'],
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('company.company_id', company.company_id)
        t.json_is('company.external_id', external_id)
        t.json_is('company.user_id', user.user_id)
        t.json_is('company.title', 'медвед')
        t.json_is('company.products_scope', ['israel'])


async def test_required(tap, dataset, api, uuid):
    with tap.plan(3, 'Обязательные поля'):
        user = await dataset.user(role='admin')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_companies_save',
            json={
                'external_id': uuid(),
                'title': 'привет',
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')


async def test_users_manage(api, dataset, tap):
    with tap.plan(14, 'изменяем поле users_manage'):
        company = await dataset.company()
        tap.ok(company, 'company created')

        tap.eq(company.users_manage, 'internal', 'internal')

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_companies_save',
            json={
                'company_id': company.company_id,
                'users_manage': 'external',
                'title': company.title,
                'products_scope': company.products_scope,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await company.reload()
        tap.eq(company.users_manage, 'external', 'external')

        await t.post_ok(
            'api_admin_companies_save',
            json={
                'company_id': company.company_id,
                'users_manage': 'internal',
                'title': company.title,
                'products_scope': company.products_scope,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await company.reload()
        tap.eq(company.users_manage, 'internal', 'internal')

        await t.post_ok(
            'api_admin_companies_save',
            json={
                'company_id': company.company_id,
                'users_manage': None,
                'title': company.title,
                'products_scope': company.products_scope,
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'BAD_REQUEST')

        await company.reload()
        tap.eq(company.users_manage, 'internal', 'internal')
