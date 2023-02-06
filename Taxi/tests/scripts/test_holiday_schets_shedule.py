from datetime import timedelta
from libstall.json_pp import dumps as json

from stall.model import schet_handler, schet_task
from stall.model.schedule import Schedule
from stall.scripts.holiday_schet_schedule import set_schedule, \
    restore_schedule, HOLIDAY_TIMEDELTA


# pylint: disable=too-many-statements,too-many-locals
async def test_set_restore_schedule(tap, dataset, time_mock):
    start_time = time_mock.now() + timedelta(days=1)
    schedule = Schedule({'interval': {'hours': 1},
                         'start_time': start_time})

    company = await dataset.company()
    store1 = await dataset.store(
        cluster='Москва',
        company=company,
    )
    task11 = schet_task.SchetTask(
        handler=schet_handler.SchetHandler('dummy_cron'),
        schedule_draft=schedule,
        created_by='__created_by__',
        store_id=store1.store_id,
        next_run_at=schedule.start_time
    )
    await task11.approve('first_approver')
    task12 = schet_task.SchetTask(
        handler=schet_handler.SchetHandler('dummy_cron'),
        schedule_draft=schedule,
        created_by='__created_by__',
        store_id=store1.store_id,
        next_run_at=schedule.start_time,
        vars={'holiday_original_schedule': True}
    )
    await task12.approve('first_approver')
    task13 = schet_task.SchetTask(
        handler=schet_handler.SchetHandler('dummy_cron'),
        schedule_draft=schedule,
        created_by='__created_by__',
        store_id=store1.store_id,
        next_run_at=schedule.start_time
    )
    await task13.save()

    store2 = await dataset.store(
        cluster='Нижний Новгород',
        company=company,
    )
    task2 = schet_task.SchetTask(
        handler=schet_handler.SchetHandler('dummy_cron'),
        schedule_draft=schedule,
        created_by='__created_by__',
        store_id=store2.store_id,
        next_run_at=schedule.start_time
    )
    await task2.approve('first_approver')

    store_israel = await dataset.store(
        cluster='Тель-Авив',
        company=company,
    )
    task_israel = schet_task.SchetTask(
        handler=schet_handler.SchetHandler('dummy_cron'),
        schedule_draft=schedule,
        created_by='__created_by__',
        store_id=store_israel.store_id,
        next_run_at=schedule.start_time
    )
    await task_israel.approve('first_approver')

    with tap.plan(54, 'расписание заданий для КСГ устанавливается верно'):
        with tap.subtest(None, 'Проверка, что расписание КСГ устанавливается '
                               'верно при нескольких запусках'):
            for _ in range(2):
                await set_schedule(company_id=company.company_id)

                await task11.reload()
                await task12.reload()
                await task13.reload()
                await task2.reload()
                await task_israel.reload()

                expected_schedule = schedule.pure_python()
                expected_schedule['start_time'] -= timedelta(
                    hours=HOLIDAY_TIMEDELTA
                )

                tap.eq_ok(
                    json(
                        task11.schedule.pure_python(),
                        sort_keys=True
                    ),
                    json(expected_schedule, sort_keys=True),
                    'Holiday schedule is set'
                )
                tap.eq_ok(task11.next_run_at, expected_schedule['start_time'],
                          'next_run_at is set')
                tap.eq_ok(task11.vars('holiday_original_schedule', None),
                          schedule,
                          'holiday_original_schedule is set')

                tap.eq_ok(
                    json(
                        task12.schedule.pure_python(),
                        sort_keys=True
                    ),
                    json(schedule.pure_python(), sort_keys=True),
                    'Schedule with holiday_original_schedule is not changed'
                )
                tap.eq_ok(task12.next_run_at, schedule.start_time,
                          'next_run_at is not changed')

                # tap.eq_ok(task13.schedule, None, 'Schedule is not changed')
                # tap.eq_ok(task13.next_run_at, None,
                #           'next_run_at is not changed')

                tap.eq_ok(
                    json(
                        task2.schedule.pure_python(),
                        sort_keys=True
                    ),
                    json(expected_schedule, sort_keys=True),
                    'Holiday schedule is set'
                )
                tap.eq_ok(task2.next_run_at, expected_schedule['start_time'],
                          'next_run_at is set')
                tap.eq_ok(task2.vars('holiday_original_schedule', None),
                          schedule,
                          'holiday_original_schedule is set')

                tap.eq_ok(
                    json(
                        task_israel.schedule.pure_python(),
                        sort_keys=True
                    ),
                    json(schedule.pure_python(), sort_keys=True),
                    'Israel timetable is not changed'
                )
                tap.eq_ok(task_israel.next_run_at, schedule.start_time,
                          'Israel next_run_at is not changed')
                tap.eq_ok('holiday_original_schedule' in task_israel.vars,
                          False,
                          'holiday_original_schedule is not set')

        del task12.vars['holiday_original_schedule']
        await task12.save()

        with tap.subtest(None, 'Проверка, что расписание КСГ востанавливается '
                               'верно при нескольких запусках'):
            for _ in range(2):
                await restore_schedule(company_id=company.company_id)

                await task11.reload()
                await task12.reload()
                await task2.reload()
                await task_israel.reload()

                tap.eq_ok(
                    json(
                        task11.schedule.pure_python(),
                        sort_keys=True
                    ),
                    json(schedule.pure_python(), sort_keys=True),
                    'Old schedule is restored'
                )
                tap.eq_ok(task11.next_run_at, schedule.start_time,
                          'Old next_run_at is restored')
                tap.eq_ok('holiday_original_schedule' in task11.vars, False,
                          'holiday_original_schedule is deleted')
                tap.eq_ok(task11.approved_by, 'first_approver',
                          'approver is not changed')

                tap.eq_ok(
                    json(
                        task12.schedule.pure_python(),
                        sort_keys=True
                    ),
                    json(schedule.pure_python(), sort_keys=True),
                    'Schedule without holiday_original_schedule '
                    'is not restored'
                )
                tap.eq_ok(task12.next_run_at, schedule.start_time,
                          'next_run_at is not restored')
                tap.eq_ok('holiday_original_schedule' in task12.vars, False,
                          'holiday_original_schedule is deleted')
                tap.eq_ok(task12.approved_by, 'first_approver',
                          'approver is not changed')

                tap.eq_ok(
                    json(
                        task2.schedule.pure_python(),
                        sort_keys=True
                    ),
                    json(schedule.pure_python(), sort_keys=True),
                    'Old schedule is restored'
                )
                tap.eq_ok(task2.next_run_at, schedule.start_time,
                          'Old next_run_at is restored')
                tap.eq_ok('holiday_original_schedule' in task2.vars, False,
                          'holiday_original_schedule is deleted')
                tap.eq_ok(task2.approved_by, 'first_approver',
                          'approver is not changed')

                tap.eq_ok(
                    json(
                        task_israel.schedule.pure_python(),
                        sort_keys=True
                    ),
                    json(schedule.pure_python(), sort_keys=True),
                    'Israel timetable is not changed'
                )
                tap.eq_ok(task_israel.next_run_at, schedule.start_time,
                          'Israel next_run_at is not changed')
                tap.eq_ok(task_israel.approved_by, 'first_approver',
                          'approver is not changed')


