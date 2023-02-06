async def test_load(api, dataset, tap):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)
        schet = await dataset.schet_task(user=user)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_load',
            json={'schet_task_id': schet.schet_task_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('schet')
        t.json_is('schet.schet_task_id', schet.schet_task_id)


async def test_load_many(api, dataset, tap):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)
        schet_1 = await dataset.schet_task(user=user)
        schet_2 = await dataset.schet_task(user=user)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_load',
            json={'schet_task_id': [
                schet_1.schet_task_id,
                schet_2.schet_task_id,
            ]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('schet')

        res = t.res['json']['schet']
        tap.eq_ok(
            sorted([x.get('schet_task_id') for x in res]),
            sorted([schet_1.schet_task_id, schet_2.schet_task_id]),
            'Записи получены'
        )


async def test_not_found(tap, api, dataset, uuid):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)

        t = await api(user=user)

        with tap.subtest(None, 'Одна запись'):
            await t.post_ok(
                'api_admin_schets_load',
                json={'schet_task_id': [uuid()]},
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')

        with tap.subtest(None, 'Список'):
            schet = await dataset.schet_task(user=user)
            await t.post_ok(
                'api_admin_schets_load',
                json={'schet_task_id': [schet.schet_task_id, uuid()]},
            )
            t.status_is(403, diag=True)
            t.json_is('code', 'ER_ACCESS')
