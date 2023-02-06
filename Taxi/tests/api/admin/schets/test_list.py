# pylint: disable=unused-variable

async def test_list_empty(api, dataset, tap):
    with tap.plan(4):
        store = await dataset.store()
        user = await dataset.user(store=store)

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_list',
            json={'store_id': store.store_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_is('schets', [])


async def test_list_nonempty(api, dataset, tap):
    with tap:
        store = await dataset.store()
        user = await dataset.user(store=store)
        schet_task_1 = await dataset.schet_task(user=user, store=store)
        schet_task_2 = await dataset.schet_task(user=user, store=store)
        await dataset.schet_task(user=user)

        schet_task_1, schet_task_2 = sorted(
            [schet_task_1, schet_task_2],
            key=lambda it: it.schet_task_id,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_list',
            json={'store_id': store.store_id},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('schets')
        t.json_has('schets.0')
        t.json_is('schets.0.schet_task_id', schet_task_1.schet_task_id,
                  'сортировано')
        t.json_has('schets.1')
        t.json_is('schets.1.schet_task_id', schet_task_2.schet_task_id,
                  'сортировано')
        t.json_hasnt('schets.2', 'только свои')


async def test_list_many_stores(api, dataset, tap):
    with tap:
        store_1 = await dataset.store()
        store_2 = await dataset.store()
        user = await dataset.user(store=store_1)
        schet_task_1 = await dataset.schet_task(user=user, store=store_1)
        schet_task_2 = await dataset.schet_task(user=user, store=store_2)

        sorted_schet_task_1, sorted_schet_task_2 = sorted(
            [schet_task_1, schet_task_2],
            key=lambda it: it.schet_task_id,
        )

        t = await api(user=user)
        await t.post_ok(
            'api_admin_schets_list',
            json={'store_id': [store_1.store_id, store_2.store_id]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('schets')
        t.json_has('schets.0')
        t.json_is('schets.0.schet_task_id', sorted_schet_task_1.schet_task_id,
                  'сортировано')
        t.json_has('schets.1')
        t.json_is('schets.1.schet_task_id', sorted_schet_task_2.schet_task_id,
                  'сортировано')
        t.json_hasnt('schets.2', 'только свои')

        await t.post_ok(
            'api_admin_schets_list',
            json={'store_id': [store_1.store_id]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('schets')
        t.json_has('schets.0')
        t.json_is('schets.0.schet_task_id', schet_task_1.schet_task_id,
                  'сортировано')
        t.json_hasnt('schets.1', 'только свои')

        await t.post_ok(
            'api_admin_schets_list',
            json={'store_id': [store_2.store_id]},
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_has('schets')
        t.json_has('schets.0')
        t.json_is('schets.0.schet_task_id', schet_task_2.schet_task_id,
                  'сортировано')
        t.json_hasnt('schets.1', 'только свои')


async def test_full_list(api, dataset, tap):
    with tap:
        store = await dataset.store()
        store_2 = await dataset.store(company_id=store.company_id)
        user = await dataset.user(company_id=store.company_id,
                                  store_id=store.store_id)

        task_1 = await dataset.schet_task(user=user)
        task_2 = await dataset.schet_task(user=user, store_id=store_2.store_id)

        t = await api(user=user)

        remain_to_find = {task_1.schet_task_id,
                          task_2.schet_task_id}

        cursor_str = ''
        while True:
            await t.post_ok(
                'api_admin_schets_list',
                json={
                    'cursor': cursor_str,
                },
            )
            t.status_is(200, diag=True)
            t.json_is('code', 'OK')
            t.json_has('schets')

            schets = t.res['json']['schets']
            for schet in schets:
                remain_to_find.discard(schet['schet_task_id'])

            cursor = t.res['json']['cursor']
            if not cursor:
                break

        tap.eq(remain_to_find, set(), 'all tasks found')
