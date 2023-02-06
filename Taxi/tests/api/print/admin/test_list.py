import pytest


@pytest.mark.parametrize('done', [True, False])
async def test_list(tap, api, dataset, done):
    with tap.plan(9, 'Запрос тасков при отсутствии в БД удалённых'):
        admin = await dataset.user()
        tap.ok(admin.store_id, 'админ создан')

        task = await dataset.printer_task(store_id=admin.store_id)
        tap.eq(task.store_id, admin.store_id, 'таск создан')

        t = await api(user=admin)
        await t.post_ok('api_print_admin_tasks',
                        json={'store_id': admin.store_id, 'done': done})
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_has('tasks.0')
        t.json_hasnt('tasks.1')

        t.json_is('tasks.0.task_id', task.task_id)
        t.json_is('tasks.0.external_id', task.external_id)


@pytest.mark.parametrize('done', [False, True])
async def test_list_with_rm(tap, api, dataset, done):
    with tap.plan(14 + (1 if done else 0),
                  'Запрос тасков при наличии в БД удалённых'):
        admin = await dataset.user()
        tap.ok(admin.store_id, 'админ создан')

        task = await dataset.printer_task(store_id=admin.store_id)
        tap.eq(task.store_id, admin.store_id, 'таск создан')
        tap.eq(task.status, 'processing', 'статус')


        taskrm = await dataset.printer_task(store_id=admin.store_id,
                                            status='done')
        tap.eq(taskrm.store_id, admin.store_id, 'таск создан')
        tap.eq(taskrm.status, 'done', 'статус')

        t = await api(user=admin)
        await t.post_ok('api_print_admin_tasks',
                        json={'store_id': admin.store_id, 'done': done})
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')
        t.json_has('tasks.0')

        t.json_is('tasks.0.task_id', task.task_id)
        t.json_is('tasks.0.external_id', task.external_id)
        t.json_is('tasks.0.status', 'processing')
        t.json_hasnt('tasks.2')

        if done:
            t.json_is('tasks.1.task_id', taskrm.task_id)
            t.json_is('tasks.1.status', 'done')
        else:
            t.json_hasnt('tasks.1')
