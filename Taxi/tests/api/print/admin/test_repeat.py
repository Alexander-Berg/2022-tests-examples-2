import pytest


@pytest.mark.parametrize('status', ['processing', 'done'])
async def test_repeat(tap, api, dataset, status):
    with tap.plan(9, 'возврат таски на выполнение'):
        admin = await dataset.user()
        tap.ok(admin.store_id, 'админ создан')

        task = await dataset.printer_task(store_id=admin.store_id,
                                          status=status)
        tap.eq(task.store_id, admin.store_id, 'таск создан')
        tap.eq(task.status, status, 'статус созданной таски')

        t = await api(user=admin)
        await t.post_ok('api_print_admin_repeat',
                        json={'task_id': task.task_id})
        t.status_is(200, diag=True)

        t.json_is('code', 'OK')

        t.json_is('task.task_id', task.task_id)
        t.json_is('task.external_id', task.external_id)
        t.json_is('task.status', 'processing')
