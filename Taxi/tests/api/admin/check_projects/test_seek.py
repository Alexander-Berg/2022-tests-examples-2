async def test_seek(tap, dataset, api, uuid):
    with tap.plan(28, 'тестим поиск'):
        user = await dataset.user(role='admin')
        cp = await dataset.check_project()

        t = await api(user=user)

        await t.post_ok(
            'api_admin_check_projects_seek',
            json={'title': cp.title, 'status': cp.status},
        )
        t.status_is(200)
        t.json_has('check_projects')
        js = t.res['json']
        tap.eq(
            js['check_projects'][0]['check_project_id'],
            cp.check_project_id,
            'нужный айди'
        )
        tap.eq(len(js['check_projects']), 1, 'один штука')

        await t.post_ok(
            'api_admin_check_projects_seek',
            json={'title': cp.title, 'status': [cp.status, 'draft']},
        )
        t.status_is(200)
        t.json_has('check_projects')
        js = t.res['json']
        tap.eq(
            js['check_projects'][0]['check_project_id'],
            cp.check_project_id,
            'нужный айди'
        )
        tap.eq(len(js['check_projects']), 1, 'один штука')

        await t.post_ok(
            'api_admin_check_projects_seek',
            json={'title': cp.title, 'status': []},
        )
        t.status_is(200)
        t.json_has('check_projects')
        js = t.res['json']
        tap.eq(
            js['check_projects'][0]['check_project_id'],
            cp.check_project_id,
            'нужный айди'
        )
        tap.eq(len(js['check_projects']), 1, 'один штука')

        await t.post_ok(
            'api_admin_check_projects_seek',
            json={'title': cp.title[7:-3]},
        )
        t.status_is(200)
        t.json_has('check_projects')
        js = t.res['json']
        tap.eq(
            js['check_projects'][0]['check_project_id'],
            cp.check_project_id,
            'нужный айди'
        )
        tap.eq(len(js['check_projects']), 1, 'один штука')

        await t.post_ok(
            'api_admin_check_projects_seek',
            json={'title': cp.title[7:-3], 'status': 'draft'},
        )
        t.status_is(200)
        t.json_has('check_projects')
        js = t.res['json']
        tap.eq(len(js['check_projects']), 0, 'ничего не нашли')

        await t.post_ok(
            'api_admin_check_projects_seek',
            json={'title': uuid()},
        )
        t.status_is(200)
        t.json_has('check_projects')
        js = t.res['json']
        tap.eq(len(js['check_projects']), 0, 'ничего не нашли')


async def test_seek_cursor(tap, dataset, api, uuid):
    with tap.plan(9, 'тестим курсор с лимитом'):
        user = await dataset.user(role='admin')
        title_prefix = uuid()
        cps = [
            await dataset.check_project(title=title_prefix+uuid())
            for _ in range(2)
        ]

        t = await api(user=user)

        await t.post_ok(
            'api_admin_check_projects_seek',
            json={'title': title_prefix, 'limit': 1},
        )
        t.status_is(200)
        t.json_has('check_projects')
        js = t.res['json']
        new_cursor = js['cursor']
        tap.eq(len(js['check_projects']), 1, 'один проект')
        cp1_id = js['check_projects'][0]['check_project_id']

        await t.post_ok(
            'api_admin_check_projects_seek',
            json={'title': title_prefix, 'limit': 1, 'cursor': new_cursor},
        )
        t.status_is(200)
        t.json_has('check_projects')
        js = t.res['json']
        tap.eq(len(js['check_projects']), 1, 'один проект')
        cp2_id = js['check_projects'][0]['check_project_id']

        tap.eq(
            {cp1_id, cp2_id},
            {cp.check_project_id for cp in cps},
            'вытащили все что надо'
        )
