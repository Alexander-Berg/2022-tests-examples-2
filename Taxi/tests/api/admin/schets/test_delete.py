async def test_delete_common(tap, dataset, api):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)
        schet = await dataset.schet_task(user=user)
        await schet.approve('__approved_by__')

        tap.eq(schet.status, 'paused', 'schet paused')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_delete',
            json={'schet_task_id': schet.schet_task_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('schet')
        t.json_is('schet.schet_task_id', schet.schet_task_id)
        t.json_is('schet.status', 'deleted')
        t.json_isnt('schet.deleted_at', None)

        await schet.reload()

        tap.eq(schet.status, 'deleted', 'schet deleted')


async def test_delete_started(tap, dataset, api):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)
        schet = await dataset.schet_task(user=user)
        await schet.approve('__approved_by__')
        await schet.start()

        tap.eq(schet.status, 'pending', 'schet started')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_delete',
            json={'schet_task_id': schet.schet_task_id},
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SCHET_STATUS_NOT_PAUSED')

        await schet.reload()

        tap.eq(schet.status, 'pending', 'schet still stared')
