async def test_pause_common(tap, dataset, api):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)
        schet = await dataset.schet_task(user=user)
        await schet.approve('__approved_by__')
        await schet.start()

        tap.eq(schet.status, 'pending', 'schet started')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_pause',
            json={'schet_task_id': schet.schet_task_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('schet')
        t.json_is('schet.schet_task_id', schet.schet_task_id)
        t.json_is('schet.status', 'paused')

        await schet.reload()

        tap.eq(schet.status, 'paused', 'schet paused')


async def test_pause_paused(tap, dataset, api):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)
        schet = await dataset.schet_task(user=user)
        await schet.approve('__approved_by__')

        tap.eq(schet.status, 'paused', 'schet paused')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_pause',
            json={'schet_task_id': schet.schet_task_id},
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SCHET_STATUS_NOT_PENDING')

        await schet.reload()

        tap.eq(schet.status, 'paused', 'schet still paused')


async def test_pause_delayed(tap, dataset, api, job, push_events_cache):
    with tap.plan(13, 'отключить можно только если таск не работает'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        schet = await dataset.schet_task(user=user)
        await schet.approve('__approved_by__')
        await schet.start()
        await schet.delay()

        tap.eq(schet.status, 'delayed', 'schet delayed')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_pause',
            json={'schet_task_id': schet.schet_task_id},
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SCHET_STATUS_NOT_PENDING')

        await push_events_cache(schet, 'run')
        task = await job.take()
        tap.ok(task, 'task taken from queue')
        await job.call(task)
        await job.ack(task)

        await schet.reload()

        tap.eq(schet.status, 'pending', 'schet proceeded')

        await t.post_ok(
            'api_admin_schets_pause',
            json={'schet_task_id': schet.schet_task_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('schet')
        t.json_is('schet.schet_task_id', schet.schet_task_id)
        t.json_is('schet.status', 'paused')

        await schet.reload()

        tap.eq(schet.status, 'paused', 'schet paused')
