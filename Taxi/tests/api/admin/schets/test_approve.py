async def test_approve_common(tap, dataset, api):
    with tap:
        store = await dataset.store()
        user_1 = await dataset.user(store=store)
        user_2 = await dataset.user(store=store)
        schet = await dataset.schet_task(user=user_1)

        tap.is_ok(schet.schedule, None, 'not approved yet')
        tap.is_ok(schet.approved_by, None, 'approved by nobody')
        tap.isnt_ok(schet.schedule_draft, None, 'draft exists')

        t = await api(user=user_2)
        await t.post_ok(
            'api_admin_schets_approve',
            json={'schet_task_id': schet.schet_task_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('schet')
        t.json_is('schet.schet_task_id', schet.schet_task_id)
        t.json_isnt('schet.schedule', None, 'schedule approved')
        t.json_is('schet.approved_by', user_2.user_id, 'approved by user_2')
        t.json_is('schet.schedule_draft', None, 'draft cleared')

        await schet.reload()

        tap.isnt_ok(schet.schedule, None, 'model approved')
        tap.eq_ok(schet.approved_by, user_2.user_id, 'model approved by user_2')
        tap.is_ok(schet.schedule_draft, None, 'model draft cleared')


async def test_approve_by_author(tap, dataset, api):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)
        schet = await dataset.schet_task(user=user)

        tap.is_ok(schet.schedule, None, 'not approved yet')
        tap.is_ok(schet.approved_by, None, 'approved by nobody')
        tap.isnt_ok(schet.schedule_draft, None, 'draft exists')

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_approve',
            json={'schet_task_id': schet.schet_task_id},
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_SCHET_CREATOR_APPROVE')

        await schet.reload()

        tap.is_ok(schet.schedule, None, 'not approved')
        tap.is_ok(schet.approved_by, None, 'approved by nobody')
        tap.isnt_ok(schet.schedule_draft, None, 'draft exists')


async def test_approve_without_draft(tap, dataset, api):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)
        user_2 = await dataset.user(store=store)
        schet = await dataset.schet_task(user=user, schedule_draft=None)

        tap.is_ok(schet.schedule, None, 'not approved yet')
        tap.is_ok(schet.approved_by, None, 'approved by nobody')
        tap.is_ok(schet.schedule_draft, None, 'draft not exists')

        t = await api(user=user_2)
        await t.post_ok(
            'api_admin_schets_approve',
            json={'schet_task_id': schet.schet_task_id},
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_SCHET_SCHEDULE_EMPTY')

        await schet.reload()

        tap.is_ok(schet.schedule, None, 'not approved')
        tap.is_ok(schet.approved_by, None, 'approved by nobody')
        tap.is_ok(schet.schedule_draft, None, 'draft not exists')
