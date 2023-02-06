from datetime import timedelta
import libstall.util


async def test_force_run_common(tap, dataset, api):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)
        schet = await dataset.schet_task(
            user=user,
            schedule_draft={
                'interval': {'hours': 1},
                'start_time': libstall.util.now() + timedelta(hours=2)
            }
        )
        await schet.approve('__approved_by__')
        await schet.start()

        tap.ok(not schet.should_run(), 'should not run yet')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_force_run',
            json={'schet_task_id': schet.schet_task_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('schet')
        t.json_is('schet.schet_task_id', schet.schet_task_id)
        t.json_is('schet.status', 'pending')

        await schet.reload()

        tap.ok(schet.should_run(), 'should run because of force_run')


async def test_force_run_not_approved(tap, dataset, api):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)
        schet = await dataset.schet_task(
            user=user,
            schedule_draft={
                'interval': {'hours': 1},
                'start_time': libstall.util.now() + timedelta(hours=2)
            }
        )

        tap.is_ok(schet.schedule, None, 'not approved')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_force_run',
            json={'schet_task_id': schet.schet_task_id},
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SCHET_SCHEDULE_EMPTY')


async def test_force_run_delayed(tap, dataset, api, job, push_events_cache):
    with tap.plan(15, 'запускать можно только незапущенный таск'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        schet = await dataset.schet_task(user=user)
        await schet.approve('__approved_by__')
        await schet.start()

        tap.ok(schet.should_run(), 'should run')

        await schet.delay()

        tap.eq(schet.status, 'delayed', 'task delayed')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_force_run',
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

        tap.eq(schet.status, 'pending', 'task delayed')
        tap.ok(not schet.should_run(), 'should not run')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_force_run',
            json={'schet_task_id': schet.schet_task_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('schet')
        t.json_is('schet.schet_task_id', schet.schet_task_id)
        t.json_is('schet.status', 'pending')

        await schet.reload()

        tap.ok(schet.should_run(), 'should run because of force_run')
