async def test_list_empty(api, tap, uuid):
    with tap.plan(4):
        t = await api(role='admin')

        await t.post_ok('api_admin_companies_list', json={'title': uuid()})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('companies', [])


async def test_list_nonempty(api, dataset, tap, uuid):
    with tap.plan(7):
        title = uuid()

        companies = [
            await dataset.company(title=f'{i} - {title}') for i in range(0, 5)
        ]
        tap.ok(companies, 'объекты созданы')

        t = await api(role='admin')

        await t.post_ok('api_admin_companies_list', json={'title': title})
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('companies')
        t.json_has('companies.4')
        t.json_hasnt('companies.5')
