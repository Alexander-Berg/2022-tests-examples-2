async def test_success(tap, dataset, api):
    with tap.plan(4, 'Загрузка таски'):
        store = await dataset.store()
        task = await dataset.repair_task(
            store_id=store.store_id, company_id=store.company_id)
        user = await dataset.user(store=store, role='executer')
        t = await api(user=user)

        await t.post_ok(
            'api_tsd_repair_task_load',
            json={
                'external_id': task.external_id,
                'source': task.source,
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('repair_task.task_id', task.task_id)


async def test_wrong_store(tap, dataset, api):
    with tap.plan(3, 'Не тот склад'):
        store = await dataset.store()
        task = await dataset.repair_task(
            store_id=store.store_id, company_id=store.company_id)
        user = await dataset.user(role='executer')
        t = await api(user=user)

        await t.post_ok(
            'api_tsd_repair_task_load',
            json={
                'external_id': task.external_id,
                'source': task.source,
            }
        )
        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS')
