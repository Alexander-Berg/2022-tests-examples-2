async def test_task_raw(api, dataset, tap):
    with tap.plan(11):
        t = await api(spec='doc/api/print-client.yaml')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        task = await dataset.printer_task(payload='hello',
                                          target='sticker',
                                          store_id=store.store_id)
        tap.ok(task, 'задача создана')
        tap.eq(task.target, 'sticker', 'стикер')

        await t.post_ok('api_print_client_task_raw',
                        json={'task_id': task.task_id},
                        headers={
                            'Authorization': f'token {store.printer_token}'
                        })
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_is('task.task_id', task.task_id)
        t.json_is('task.target', task.target)
        t.json_is('task.type', task.type)
        t.json_is('task.target', task.target)
        t.json_is('task.document', 'hello')

