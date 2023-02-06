import pytest

from stall.model.courier_shift_schedule import COURIER_SHIFT_SCHEDULE_STATUS


async def test_load_nf(tap, api, uuid):
    with tap.plan(4, 'Неизвестный идентификатор'):
        t = await api(role='admin')

        await t.post_ok('api_admin_courier_shift_schedules_load',
                        json={'courier_shift_schedule_id': uuid()})

        t.status_is(403, diag=True)
        t.json_is('code', 'ER_ACCESS', 'нет доступа')
        t.json_is('message', 'Access denied', 'текст')


@pytest.mark.parametrize('status', COURIER_SHIFT_SCHEDULE_STATUS)
async def test_load(tap, api, dataset, status):
    with tap.plan(15, 'Успешная загрузка'):

        store = await dataset.store()
        schedule = await dataset.courier_shift_schedule(
            store=store,
            status=status,
        )

        t = await api(role='admin')

        await t.post_ok(
            'api_admin_courier_shift_schedules_load',
            json={
                'courier_shift_schedule_id': schedule.courier_shift_schedule_id,
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'получен')

        t.json_is('courier_shift_schedule.courier_shift_schedule_id',
                  schedule.courier_shift_schedule_id)

        t.json_has('courier_shift_schedule.courier_shift_schedule_id')
        t.json_has('courier_shift_schedule.external_id')
        t.json_has('courier_shift_schedule.company_id')
        t.json_has('courier_shift_schedule.store_id')
        t.json_is('courier_shift_schedule.status', status, 'status')
        t.json_has('courier_shift_schedule.schedule')
        t.json_has('courier_shift_schedule.time_till')
        t.json_has('courier_shift_schedule.created')
        t.json_has('courier_shift_schedule.updated')
        t.json_has('courier_shift_schedule.vars')
        t.json_has('courier_shift_schedule.user_id')


@pytest.mark.parametrize('role', ['admin'])
async def test_load_multiple(tap, api, dataset, role):
    with tap.plan(5, 'Успешная загрузка списка'):
        t = await api(role=role)

        store1 = await dataset.store()
        store2 = await dataset.store()

        schedule1 = await dataset.courier_shift_schedule(store=store1)
        schedule2 = await dataset.courier_shift_schedule(store=store2)

        await t.post_ok(
            'api_admin_courier_shift_schedules_load',
            json={
                'courier_shift_schedule_id': [
                    schedule1.courier_shift_schedule_id,
                    schedule2.courier_shift_schedule_id,
                ]
            }
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK', 'код успеха')
        t.json_has('courier_shift_schedule', 'есть в выдаче')
        res = t.res['json']['courier_shift_schedule']
        tap.eq_ok(
            sorted([res[0]['courier_shift_schedule_id'],
                    res[1]['courier_shift_schedule_id']]),
            sorted([schedule1.courier_shift_schedule_id,
                    schedule2.courier_shift_schedule_id]),
            'Пришли правильные объекты'
        )


@pytest.mark.parametrize('role', ['admin'])
async def test_load_multiple_fail(tap, api, dataset, uuid, role):
    with tap.plan(2, 'Неизвестные идентификаторы в списке'):
        t = await api(role=role)

        store = await dataset.store()
        schedule = await dataset.courier_shift_schedule(store=store)

        await t.post_ok(
            'api_admin_courier_shift_schedules_load',
            json={
                'courier_shift_schedule_id': [
                    schedule.courier_shift_schedule_id,
                    uuid()
                ],
            }
        )
        t.status_is(403, diag=True)
