async def test_task_list_unauth(tap, api, uuid):
    with tap.plan(4):
        t = await api(spec='doc/api/print-client.yaml')

        await t.post_ok('api_print_client_task_list',
                        json={},
                        headers={'Authorization': f'token {uuid()}'})
        t.status_is(403, diag=True)

        t.json_is('code', 'ER_ACCESS')
        t.json_is('message', 'Access denied')


async def test_task_list_empty(tap, api, dataset):
    with tap.plan(5):
        t = await api(spec='doc/api/print-client.yaml')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        await t.post_ok('api_print_client_task_list',
                        json={},
                        headers={
                            'Authorization': f'token {store.printer_token}'
                        })
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_is('tasks', [], 'нет задач')


async def test_task_list_noempty(tap, api, dataset):
    with tap.plan(12, 'Непустой список без done-тасок'):
        t = await api(spec='doc/api/print-client.yaml')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        tasks = []
        for _ in range(5):
            task = await dataset.printer_task(payload='hello',
                                              store_id=store.store_id)
            tap.ok(task, f'задание создано шард {task.shardno}')
            tasks.append(task)

        tap.ok(tasks, 'таски созданы')

        done_task = await dataset.printer_task(payload='hello',
                                               status='done',
                                               store_id=store.store_id)
        tap.eq(done_task.status, 'done', 'завершённая таска создана')


        await t.post_ok('api_print_client_task_list',
                        json={},
                        headers={
                            'Authorization': f'token {store.printer_token}'
                        })
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_is('tasks', [t.task_id for t in tasks], 'список задач')

