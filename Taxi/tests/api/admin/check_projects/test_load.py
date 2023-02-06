async def test_load(tap, dataset, api):
    with tap.plan(12, 'тестим хеппи флоу'):
        user = await dataset.user(role='admin')
        cp = await dataset.check_project(title='zhopka')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_check_projects_load',
            json={'check_project_id': cp.check_project_id},
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('check_project.check_project_id', cp.check_project_id)
        t.json_is('check_project.external_id', cp.external_id)
        t.json_is('check_project.title', cp.title)
        t.json_is('check_project.status', cp.status)
        t.json_is('check_project.stores', cp.stores)
        t.json_is('check_project.products', cp.products)
        t.json_is('check_project.schedule', cp.schedule)
        t.json_is('check_project.shelf_types', cp.shelf_types)
        t.json_is('check_project.vars', cp.vars)


async def test_load_permit(tap, dataset, api):
    with tap.plan(3, 'проверяем использование пермита'):
        user = await dataset.user(role='admin')
        cp = await dataset.check_project(title='zhopka')

        with user.role as role:
            role.remove_permit('check_projects_load')

            t = await api(user=user)
            await t.post_ok(
                'api_admin_check_projects_load',
                json={'check_project_id': cp.check_project_id},
            )

            t.status_is(403)
            t.json_is('code', 'ER_ACCESS')


async def test_load_many(tap, dataset, api):
    with tap.plan(12, 'грузим несколько'):
        user = await dataset.user(role='admin')
        cps = [await dataset.check_project() for _ in range(3)]

        t = await api(user=user)
        for cnt in range(1, 4):
            await t.post_ok(
                'api_admin_check_projects_load',
                json={
                    'check_project_id': [
                        cp.check_project_id
                        for cp in cps[:cnt]
                    ]
                },
            )

            t.status_is(200)
            t.json_has('check_project')
            js = t.res['json']
            tap.eq(len(js['check_project']), cnt, f'{cnt} штук')


async def test_load_fail(tap, dataset, api, uuid, cfg):
    with tap.plan(12, 'ищем небывалые продукты/слишком много'):
        user = await dataset.user(role='admin')
        cp = await dataset.check_project(title='zhopka')

        t = await api(user=user)

        await t.post_ok(
            'api_admin_check_projects_load',
            json={'check_project_id': uuid()},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        await t.post_ok(
            'api_admin_check_projects_load',
            json={'check_project_id': [uuid()]},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        await t.post_ok(
            'api_admin_check_projects_load',
            json={'check_project_id': [cp.check_project_id, uuid()]},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')

        cfg.set('api.max_ids_length', 1)
        await t.post_ok(
            'api_admin_check_projects_load',
            json={
                'check_project_id': [cp.check_project_id, cp.check_project_id]
            },
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')


