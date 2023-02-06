from stall.client.print import PrintClient

async def test_ping(tap, server):
    with tap.plan(4):
        app = await server(spec='doc/api/print-client.yaml')
        tap.ok(app, 'сервер печати запущен')

        client = PrintClient(base_url =
                             f'http://localhost:{app.port}/api/print-client')

        tap.ok(client, 'клиент создан')
        tap.ok(client.base_url, 'Базовый урл назначен')

        res = await client.ping()
        tap.eq(res, {'code': 'OK', 'message': 'PONG'}, 'ответ сервера')

        await client.close()

async def test_task_api(dataset, tap, server):
    with tap.plan(11):
        app = await server(spec='doc/api/print-client.yaml')
        tap.ok(app, 'сервер печати запущен')


        store = await dataset.store()
        tap.ok(store, 'склад создан')

        client = PrintClient(base_url =
                             f'http://localhost:{app.port}/api/print-client',
                             auth=store.printer_token)

        tap.ok(client, 'клиент создан')
        tap.ok(client.base_url, 'Базовый урл назначен')

        res = await client.task_list()
        tap.eq(res, {'code': 'OK', 'tasks': []}, 'ответ сервера')


        task = await dataset.printer_task(payload='hello',
                                          store_id=store.store_id)
        tap.ok(task, 'задача создана')

        res = await client.task_list()
        tap.eq(res, {'code': 'OK', 'tasks': [task.task_id]}, 'ответ сервера')

        res = await client.task_raw(task.task_id)
        tap.eq(res['code'], 'OK', 'успешно получены данные')
        tap.eq(res['task'],
               {
                   'task_id': task.task_id,
                   'target': task.target,
                   'document': 'hello',
                   'type': task.type,
               }, 'Данные задачи')


        res = await client.task_rm(task.task_id)
        tap.eq(res['code'], 'OK', 'успешно удалено')

        res = await client.task_rm(task.task_id)
        tap.eq(res['code'], 'ER_NOT_FOUND', 'Повторно не удаляется')

        await client.close()
