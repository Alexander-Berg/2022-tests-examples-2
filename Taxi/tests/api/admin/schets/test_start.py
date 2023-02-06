async def test_start_common(tap, dataset, api):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)
        schet = await dataset.schet_task(user=user)
        await schet.approve('__approved_by__')

        tap.eq(schet.status, 'paused', 'schet paused')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_start',
            json={'schet_task_id': schet.schet_task_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('schet')
        t.json_is('schet.schet_task_id', schet.schet_task_id)
        t.json_is('schet.status', 'pending')

        await schet.reload()

        tap.eq(schet.status, 'pending', 'schet started')


async def test_start_started(tap, dataset, api):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)
        schet = await dataset.schet_task(user=user)
        await schet.approve('__approved_by__')
        await schet.start()

        tap.eq(schet.status, 'pending', 'schet started')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_start',
            json={'schet_task_id': schet.schet_task_id},
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SCHET_STATUS_NOT_PAUSED')

        await schet.reload()

        tap.eq(schet.status, 'pending', 'schet still started')


async def test_start_not_approved(tap, dataset, api):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)
        schet = await dataset.schet_task(user=user)

        tap.eq(schet.status, 'paused', 'schet started')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_start',
            json={'schet_task_id': schet.schet_task_id},
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SCHET_SCHEDULE_EMPTY')

        await schet.reload()

        tap.eq(schet.status, 'paused', 'schet still paused')
