import pytest


async def test_draft(tap, dataset, api, job, now):
    with tap.plan(16, 'Сохранять из draft можно только в draft и processing'):
        company = await dataset.company()
        store = await dataset.store(company=company)
        schedule = await dataset.courier_shift_schedule(
            store=store,
            status='draft',
            schedule=[
                {'tags': ['test1'], 'time': now()},
                {'tags': ['test2'], 'time': now()},
            ],
        )
        shift = await dataset.courier_shift(
            status='template',
            store=store,
            courier_shift_schedule=schedule,
        )
        user = await dataset.user(store=store)

        t = await api(user=user)

        await t.post_ok(
            'api_admin_courier_shift_schedules_save',
            json={
                'courier_shift_schedule_id': schedule.courier_shift_schedule_id,
                'status': 'draft',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await t.post_ok(
            'api_admin_courier_shift_schedules_save',
            json={
                'courier_shift_schedule_id': schedule.courier_shift_schedule_id,
                'status': 'complete',
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')

        await t.post_ok(
            'api_admin_courier_shift_schedules_save',
            json={
                'courier_shift_schedule_id': schedule.courier_shift_schedule_id,
                'status': 'processing',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'\S+')

        t.json_is('courier_shift_schedule.courier_shift_schedule_id',
                  schedule.courier_shift_schedule_id)
        t.json_is('courier_shift_schedule.status', 'processing')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        tap.ok(await shift.reload(), 'получили смену')
        tap.eq(shift.status, 'request', 'status')
        tap.eq(shift.schedule, schedule.schedule, 'schedule')

async def test_processing(tap, dataset, api):
    with tap.plan(9, 'Редактировать уже обрабатываемое запрещено'):
        company = await dataset.company()
        store = await dataset.store(company=company)
        user = await dataset.user(store=store)

        schedule = await dataset.courier_shift_schedule(
            store=store,
            status='processing',
        )

        t = await api(user=user)

        await t.post_ok(
            'api_admin_courier_shift_schedules_save',
            json={
                'courier_shift_schedule_id': schedule.courier_shift_schedule_id,
                'status': 'draft',
            },
        )
        t.status_is(429, diag=True)
        t.json_is('code', 'ER_ALREADY_PROCESSING')

        await t.post_ok(
            'api_admin_courier_shift_schedules_save',
            json={
                'courier_shift_schedule_id': schedule.courier_shift_schedule_id,
                'status': 'processing',
            },
        )
        t.status_is(429, diag=True)
        t.json_is('code', 'ER_ALREADY_PROCESSING')

        await t.post_ok(
            'api_admin_courier_shift_schedules_save',
            json={
                'courier_shift_schedule_id': schedule.courier_shift_schedule_id,
                'status': 'complete',
            },
        )
        t.status_is(429, diag=True)
        t.json_is('code', 'ER_ALREADY_PROCESSING')

async def test_complete(tap, dataset, api):
    with tap.plan(10, 'Сохранять из complete можно только в processing'):
        company = await dataset.company()
        store = await dataset.store(company=company)
        user = await dataset.user(store=store)

        schedule = await dataset.courier_shift_schedule(
            store=store,
            status='complete',
        )

        t = await api(user=user)

        await t.post_ok(
            'api_admin_courier_shift_schedules_save',
            json={
                'courier_shift_schedule_id': schedule.courier_shift_schedule_id,
                'status': 'draft',
            },
        )
        t.status_is(400, diag=True)
        t.json_is('code', 'ER_BAD_REQUEST')

        await t.post_ok(
            'api_admin_courier_shift_schedules_save',
            json={
                'courier_shift_schedule_id': schedule.courier_shift_schedule_id,
                'status': 'complete',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        await t.post_ok(
            'api_admin_courier_shift_schedules_save',
            json={
                'courier_shift_schedule_id': schedule.courier_shift_schedule_id,
                'status': 'processing',
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'\S+')


@pytest.mark.parametrize('status_from', ['draft', 'complete'])
async def test_expired(tap, dataset, api, now, status_from):
    with tap.plan(3, 'Время для редактирования истекло'):
        company = await dataset.company()
        store = await dataset.store(company=company)
        user = await dataset.user(store=store)

        schedule = await dataset.courier_shift_schedule(
            store=store,
            status=status_from,
            time_till=now()
        )

        t = await api(user=user)

        await t.post_ok(
            'api_admin_courier_shift_schedules_save',
            json={
                'courier_shift_schedule_id': schedule.courier_shift_schedule_id,
                'status': 'processing',
            },
        )

        t.status_is(408, diag=True)
        t.json_is('code', 'ER_EXPIRED')


async def test_cancelling_expired(tap, dataset, api, job, now):
    with tap.plan(23, 'Время для редактирования истекло, но это не проблема'):
        company = await dataset.company()
        store = await dataset.store(company=company)
        schedule = await dataset.courier_shift_schedule(
            store=store,
            status='complete',
            time_till=now(),
        )
        shifts_target = [await dataset.courier_shift(
            status=s,
            store=store,
            courier_shift_schedule=schedule,
        ) for s in ('template', 'request', 'waiting')]

        shifts_ignored = [await dataset.courier_shift(
            status=s,
            store=store,
            courier_shift_schedule=schedule,
        ) for s in ('processing', 'complete', 'leave', 'absent', 'closed')]
        user = await dataset.user(store=store)

        t = await api(user=user)

        await t.post_ok(
            'api_admin_courier_shift_schedules_save',
            json={
                'courier_shift_schedule_id': schedule.courier_shift_schedule_id,
                'status': 'cancelling',
            },
        )

        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'\S+')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        with tap.subtest(None, 'Проверяем отменились ли смены') as _tap:
            for shift in shifts_target:
                tap.ok(await shift.reload(), 'получили смену')
                tap.eq(shift.status, 'cancelled', 'status')

        with tap.subtest(None, 'Проверяем не изменились ли смены') as _tap:
            for shift in shifts_ignored:
                tap.ok(await shift.reload(), 'получили смену')
                tap.ne(shift.status, 'cancelled', 'status')


@pytest.mark.parametrize(
    'status_from,status_to,status_complete,shift_status_from,shift_status_to',
    [
        ['draft', 'draft', 'draft', 'template', 'template'],
        ['draft', 'draft', 'draft', 'request', 'request'],
        ['draft', 'processing', 'complete', 'template', 'request'],
        ['draft', 'processing', 'complete', 'request', 'request'],
        ['draft', 'cancelling', 'cancelled', 'template', 'cancelled'],
        ['draft', 'cancelling', 'cancelled', 'request', 'cancelled'],

        # 'processing' - изменение обслуживаемого расписания невозможно.
        #                Только сам и только в complete.

        ['complete', 'processing', 'complete', 'template', 'request'],
        ['complete', 'processing', 'complete', 'request', 'request'],
        ['complete', 'cancelling', 'cancelled', 'template', 'cancelled'],
        ['complete', 'cancelling', 'cancelled', 'request', 'cancelled'],

        # 'cancelling' - изменение отменяемого расписания невозможно.
        #                Только сам и только в cancelled.

        # 'cancelling' - не редактируемое состояние расписания.
    ]
)
async def test_available_switching(     # pylint: disable=too-many-arguments,too-many-locals
        tap,
        dataset,
        api,
        job,
        now,
        status_from,
        status_to,
        status_complete,
        shift_status_from,
        shift_status_to,
):
    with tap.plan(12, f'Сохранение из {status_from} в {status_to}'):
        store = await dataset.store()
        schedule = await dataset.courier_shift_schedule(
            store=store,
            status=status_from,
            schedule=[
                {'tags': ['test1'], 'time': now()},
                {'tags': ['test2'], 'time': now()},
            ],
        )
        shift = await dataset.courier_shift(
            status=shift_status_from,
            store=store,
            courier_shift_schedule=schedule,
        )
        user = await dataset.user(store=store)

        t = await api(user=user)

        await t.post_ok(
            'api_admin_courier_shift_schedules_save',
            json={
                'courier_shift_schedule_id': schedule.courier_shift_schedule_id,
                'status': status_to,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')

        t.json_is('courier_shift_schedule.courier_shift_schedule_id',
                  schedule.courier_shift_schedule_id)
        t.json_is('courier_shift_schedule.status', status_to)

        if status_to == 'processing':
            t.json_like('job_id', r'\S+')
            tap.ok(await job.call(await job.take()), 'Задание выполнено')
            expected_schedule_items = schedule.schedule
        elif status_to == 'cancelling':
            t.json_like('job_id', r'\S+')
            tap.ok(await job.call(await job.take()), 'Задание выполнено')
            expected_schedule_items = shift.schedule
        else:
            t.json_is('job_id', None)
            t.json_is('job_id', None)
            expected_schedule_items = shift.schedule

        tap.ok(await shift.reload(), 'получили смену')
        tap.eq(shift.schedule, expected_schedule_items, 'schedule items')
        tap.eq(shift.status, shift_status_to, 'shift status')
        tap.ok(await schedule.reload(), 'получили schedule')
        tap.eq(schedule.status, status_complete, 'schedule status')


@pytest.mark.parametrize(
    'err_code,status_from,status_to',
    [
        [400, 'draft', 'complete'],
        [400, 'draft', 'cancelled'],

        [429, 'processing', 'draft'],       # 429, хотя переход невозможен
        [429, 'processing', 'processing'],  # задача уже запущена
        [429, 'processing', 'complete'],    # попытка завершить не дожидаясь job
        [429, 'processing', 'cancelling'],  # задача уже запущена
        [400, 'processing', 'cancelled'],

        [400, 'complete', 'draft'],
        [400, 'complete', 'cancelled'],

        [429, 'cancelling', 'draft'],       # 429, хотя переход невозможен
        [429, 'cancelling', 'processing'],  # задача уже запущена
        [429, 'cancelling', 'complete'],
        [429, 'cancelling', 'cancelling'],  # задача уже запущена
        [400, 'cancelling', 'cancelled'],   # попытка завершить не дожидаясь job

        [400, 'cancelled', 'draft'],
        [400, 'cancelled', 'processing'],
        [400, 'cancelled', 'complete'],
        [400, 'cancelled', 'cancelling'],
        [400, 'cancelled', 'cancelled'],
    ]
)
async def test_unavailable_switching(
        tap, dataset, api, now, err_code, status_from, status_to
):
    with tap.plan(6, 'Проверка недопустимых переключений между состояниями'):
        company = await dataset.company()
        store = await dataset.store(company=company)
        schedule = await dataset.courier_shift_schedule(
            store=store,
            status=status_from,
            schedule=[
                {'tags': ['test1'], 'time': now()},
                {'tags': ['test2'], 'time': now()},
            ],
        )
        shift = await dataset.courier_shift(
            status='template',
            store=store,
            courier_shift_schedule=schedule,
        )
        user = await dataset.user(store=store)

        t = await api(user=user)

        await t.post_ok(
            'api_admin_courier_shift_schedules_save',
            json={
                'courier_shift_schedule_id': schedule.courier_shift_schedule_id,
                'status': status_to,
            },
        )
        t.status_is(err_code, diag=True)

        tap.ok(await shift.reload(), 'получили смену')
        tap.eq(shift.status, 'template', 'status')
        tap.ok(await schedule.reload(), 'получили schedule')
        tap.eq(shift.schedule, shift.schedule, 'schedule')


async def test_update_schedules(
        tap, dataset, api, job, now,
):
    with tap.plan(20, 'обновляем график всех смен при изменении графика пачки'):
        company = await dataset.company()
        store = await dataset.store(company=company)
        schedule = await dataset.courier_shift_schedule(
            store=store,
            status='complete',
        )
        shift_1 = await dataset.courier_shift(
            status='template',
            store=store,
            courier_shift_schedule=schedule,
            schedule=[
                {'tags': ['test1'], 'time': now()},
            ]
        )
        shift_2 = await dataset.courier_shift(
            status='request',
            store=store,
            courier_shift_schedule=schedule,
            schedule=[
                {'tags': ['test2'], 'time': now()},
            ]
        )
        shift_3 = await dataset.courier_shift(
            status='waiting',
            store=store,
            courier_shift_schedule=schedule,
            schedule=[
                {'tags': ['test3'], 'time': now()},
            ]
        )

        new_schedule = [
            {'tags': ['test4'], 'time': now()},
            {'tags': ['test5'], 'time': now()},
        ]

        user = await dataset.user(store=store)
        t = await api(user=user)

        await t.post_ok(
            'api_admin_courier_shift_schedules_save',
            json={
                'courier_shift_schedule_id': schedule.courier_shift_schedule_id,
                'status': 'complete',
                'schedule': new_schedule,
            },
        )
        t.status_is(200, diag=True)
        t.json_is('code', 'OK')
        t.json_like('job_id', r'\S+')

        t.json_is('courier_shift_schedule.courier_shift_schedule_id',
                  schedule.courier_shift_schedule_id)
        t.json_is('courier_shift_schedule.status', 'processing')

        await schedule.reload()

        tap.isnt_ok(schedule.schedule, [], 'schedule.schedule updated')

        tap.eq(shift_1.status, 'template', 'shift_1.status = template')
        tap.ne(schedule.schedule, shift_1.schedule,
               'schedule.schedule != shift_1.schedule')

        tap.eq(shift_2.status, 'request', 'shift_2.status = request')
        tap.ne(schedule.schedule, shift_2.schedule,
               'schedule.schedule != shift_2.schedule')

        tap.eq(shift_3.status, 'waiting', 'shift_2.status = waiting')
        tap.ne(schedule.schedule, shift_3.schedule,
               'schedule.schedule != shift_2.schedule')

        tap.ok(await job.call(await job.take()), 'Задание выполнено')

        await shift_1.reload()
        tap.eq(shift_1.status, 'request', 'shift_1.status = request')
        tap.eq(shift_1.schedule, schedule.schedule,
               'schedule.schedule = shift_1.schedule')

        await shift_2.reload()
        tap.eq(shift_2.status, 'request', 'shift_2.status = request')
        tap.eq(shift_2.schedule, schedule.schedule,
               'schedule.schedule = shift_2.schedule')

        await shift_3.reload()
        tap.eq(shift_3.status, 'waiting', 'shift_3.status = waiting')
        tap.ne(shift_3.schedule, schedule.schedule,
               'schedule.schedule != shift_3.schedule')
