async def test_save(tap, dataset, api, uuid):
    with tap.plan(26, 'создаём и изменяем таск'):
        store = await dataset.store()
        user = await dataset.user(store=store)
        user_2 = await dataset.user(store=store)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_save',
            json={
                'external_id': uuid(),
                'store_id': store.store_id,
                'handler': 'crons_healthcheck',
                'schedule': {
                    'interval': {'hours': 1}
                }
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('schet')

        t.json_has('schet.schet_task_id')
        t.json_is('schet.status', 'paused')
        t.json_is('schet.store_id', store.store_id)
        t.json_is('schet.company_id', store.company_id)
        t.json_is('schet.tz', store.tz)
        t.json_has('schet.schedule_draft')
        t.json_has('schet.schedule_draft.interval')
        t.json_has('schet.schedule_draft.start_time')
        t.json_is('schet.schedule_draft.interval', {'hours': 1})
        t.json_is('schet.schedule', None)
        t.json_is('schet.created_by', user.user_id)
        t.json_is('schet.handler', 'crons_healthcheck')

        schet_task_id = t.res['json']['schet']['schet_task_id']

        t = await api(user=user_2)
        await t.post_ok(
            'api_admin_schets_save',
            json={
                'schet_task_id': schet_task_id,
                'handler': 'crons_healthcheck',
                'schedule': {
                    'interval': {'minutes': 45}
                }
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('schet')

        t.json_is('schet.schet_task_id', schet_task_id)
        t.json_is('schet.store_id', store.store_id)
        t.json_is('schet.company_id', store.company_id)
        t.json_is('schet.schedule_draft.interval', {'minutes': 45})
        t.json_is('schet.handler', 'crons_healthcheck')
        t.json_is('schet.created_by', user_2.user_id)
