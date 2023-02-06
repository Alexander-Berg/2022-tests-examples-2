from stall.model.printer_task import PrinterTask

async def test_task_remove(api, dataset, tap):
    with tap.plan(10):
        t = await api(spec='doc/api/print-client.yaml')

        store = await dataset.store()
        tap.ok(store, 'склад создан')

        task = await dataset.printer_task(payload='hello',
                                          target='sticker',
                                          store_id=store.store_id)
        tap.ok(task, 'задача создана')
        tap.eq(task.target, 'sticker', 'стикер')

        await t.post_ok('api_print_client_task_rm',
                        json={'task_id': task.task_id},
                        headers={
                            'Authorization': f'token {store.printer_token}'
                        },
                        desc='Первый запрос на удаление')
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        loaded = await PrinterTask.load(task.task_id)
        tap.eq(loaded.status, 'done', 'в БД помечено как удалённое')


        await t.post_ok('api_print_client_task_rm',
                        json={'task_id': task.task_id},
                        headers={
                            'Authorization': f'token {store.printer_token}'
                        },
                        desc='Повторный запрос')
        t.status_is(404, diag=True)
        t.json_is('code', 'ER_NOT_FOUND')


