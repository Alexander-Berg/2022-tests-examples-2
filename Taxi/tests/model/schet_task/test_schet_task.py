# pylint: disable=unused-argument
import datetime

import pytest

import libstall.util
from libstall.model import coerces
from stall.model import schet_handler, schet_task
from stall.model.schedule import Schedule
from stall.model.schet_task import SchetTaskEr
from stall.model.schet_task import SchetTaskScheduleEmptyEr
from stall.model.schet_task import SchetTaskStatusNotPausedEr


async def test_statuses(tap):
    with tap.plan(13, 'смена статусов по вызову методов'):
        task = schet_task.SchetTask(
            handler=schet_handler.SchetHandler('dummy_cron'),
            schedule_draft=Schedule({'interval': {'hours': 1}}),
            created_by='__created_by__',
        )
        await task.save()
        tap.ok(task, 'task created')
        tap.eq(task.status, 'paused', 'initial status paused')

        tap.ok(task.schedule_draft, 'schedule draft exists')
        tap.ok(not task.schedule, 'schedule does not exist')
        with tap.raises(
                SchetTaskScheduleEmptyEr,
                'schedule is not approved yet'
        ):
            await task.start()

        await task.approve('__approved_by__')
        tap.ok(not task.schedule_draft, 'schedule draft cleaned')
        tap.ok(task.schedule, 'schedule exists')
        await task.start()
        tap.eq(task.status, 'pending', 'task started')

        await task.pause()
        tap.eq(task.status, 'paused', 'task paused')
        await task.start()
        tap.eq(task.status, 'pending', 'task started')

        with tap.raises(
                SchetTaskStatusNotPausedEr,
                'task must be paused for delete'
        ):
            await task.delete()

        await task.pause()
        tap.eq(task.status, 'paused', 'task paused')
        await task.delete()
        tap.eq(task.status, 'deleted', 'task deleted')


async def test_should_run(tap, push_events_cache, job, time_mock):
    with tap.plan(10, 'необходимость запуска спустя интервал времени'):
        task = schet_task.SchetTask(
            handler=schet_handler.SchetHandler('dummy_cron'),
            schedule_draft=Schedule({
                'interval': {'seconds': 10},
                'start_time': time_mock.now(),
            }),
            created_by='__created_by__',
        )
        await task.save()
        tap.ok(task, 'task created')

        tap.ok(not task.should_run(), 'not approved')
        await task.approve('__approved_by__')
        tap.ok(not task.should_run(), 'not started')
        await task.start()
        tap.ok(
            task.should_run(),
            f'time has come for the first time ('
            f'start_time={task.schedule.start_time}, '
            f'now={libstall.util.now(task.timezone)}'
            f')'
        )

        await task.delay()
        tap.eq(task.status, 'delayed', 'task delayed')

        await process_jobs(tap, push_events_cache, job, task)
        await task.reload()
        tap.eq(task.status, 'pending', 'task proceeded')

        tap.ok(
            not task.should_run(),
            f'time has not come ('
            f'start_time={task.schedule.start_time}, '
            f'now={libstall.util.now(task.timezone)}'
            f')'
        )
        time_mock.sleep(seconds=10)
        tap.ok(
            task.should_run(),
            f'time has come ('
            f'start_time={task.schedule.start_time}, '
            f'now={libstall.util.now(task.timezone)}'
            f')'
        )


@pytest.mark.parametrize(['current_time', 'start_time', 'expected'], [
    ('2021-03-27T02:00+01:00', '2021-03-27T03:00+01:00', False),
    ('2021-03-27T02:50+01:00', '2021-03-27T03:00+01:00', False),
    ('2021-03-27T03:00+01:00', '2021-03-27T03:00+01:00', True),

    ('2021-03-28T01:50+01:00', '2021-03-28T03:00+01:00', False),
    ('2021-03-28T02:00+01:00', '2021-03-28T03:00+01:00', True),
    ('2021-03-28T03:00+02:00', '2021-03-28T03:00+01:00', True),

    ('2021-10-30T01:50+02:00', '2021-10-30T03:00+01:00', False),
    ('2021-10-30T02:00+02:00', '2021-10-30T03:00+01:00', False),
    ('2021-10-30T03:00+02:00', '2021-10-30T03:00+01:00', True),

    ('2021-10-31T01:50+02:00', '2021-10-31T03:00+01:00', False),
    ('2021-10-31T02:00+02:00', '2021-10-31T03:00+01:00', False),
    ('2021-10-31T03:00+02:00', '2021-10-31T03:00+01:00', False),
    ('2021-10-31T02:00+01:00', '2021-10-31T03:00+01:00', False),
    ('2021-10-31T03:00+01:00', '2021-10-31T03:00+01:00', True),

    ('2021-03-27T02:00+01:00', '2021-03-27T02:30+01:00', False),
    ('2021-03-28T02:00+01:00', '2021-03-28T02:30+01:00', True),

    ('2021-10-31T02:00+02:00', '2021-10-31T02:30+01:00', False),
    ('2021-10-31T02:30+02:00', '2021-10-31T02:30+01:00', True),
    ('2021-10-31T03:00+02:00', '2021-10-31T02:30+01:00', False),
    ('2021-10-31T02:00+01:00', '2021-10-31T02:30+01:00', False),
    ('2021-10-31T02:30+01:00', '2021-10-31T02:30+01:00', True),
])
async def test_daylight_saving(
        tap, time_mock, job, current_time, start_time, expected
):
    with tap.plan(1, 'необходимость запуска с учётом таймзоны'):
        time_mock.set(coerces.date_time(current_time))

        task = schet_task.SchetTask(
            handler=schet_handler.SchetHandler('dummy_cron'),
            schedule_draft=Schedule({
                'start_time': start_time,
                'interval': {'days': 1},
            }),
            created_by='__created_by__',
            tz='Europe/Paris',
        )
        await task.save()
        await task.approve('__approved_by__')
        await task.start()

        tap.ok(task.should_run() is expected, 'ok')


async def test_force_run(tap, time_mock, push_events_cache, job):
    with tap.plan(7, 'несвоевременный запуск через force_run'):
        task = schet_task.SchetTask(
            handler=schet_handler.SchetHandler('dummy_cron'),
            schedule_draft=Schedule({
                'interval': {'seconds': 10},
                'start_time': time_mock.now(),
            }),
            created_by='__created_by__',
        )
        await task.save()
        tap.ok(task, 'task created')

        await task.approve('__approved_by__')
        await task.start()

        await task.delay()
        tap.eq(task.status, 'delayed', 'task delayed')

        await process_jobs(tap, push_events_cache, job, task)
        await task.reload()
        tap.eq(task.status, 'pending', 'task proceeded')

        tap.ok(not task.should_run(), 'time has not come yet')
        await task.force_run()
        tap.ok(task.should_run(), 'force run')


async def test_error_task(tap, time_mock, push_events_cache, job):
    with tap.plan(9, 'таск с ошибкой должен оставаться в статусе running'
                     ' пока ретраится джобами'):
        task = schet_task.SchetTask(
            handler=schet_handler.SchetHandler('dummy_cron'),
            schedule_draft=Schedule({
                'interval': {'seconds': 10},
                'start_time': time_mock.now(),
            }),
            kwargs={'raise_error': True},
            created_by='__created_by__',
        )
        await task.save()
        tap.ok(task, 'task created')

        await task.approve('__approved_by__')
        await task.start()

        await task.delay()
        tap.eq(task.status, 'delayed', 'task delayed')

        with tap.raises(SchetTaskEr):
            await process_jobs(tap, push_events_cache, job, task)

        await task.reload()
        tap.eq(task.status, 'running', 'task running')

        await task.delay()
        tap.eq(task.status, 'running', 'task still running')

        # self-made retry
        await job.put(
            schet_task.SchetTask.run,
            schet_task_id=task.schet_task_id
        )

        with tap.raises(SchetTaskEr):
            await process_jobs(tap, push_events_cache, job, task)

        await task.reload()
        tap.eq(task.status, 'running', 'task running')


async def test_list(tap, dataset):
    with tap.plan(4, 'получаем список тасок по условиям'):
        store = await dataset.store()

        task = schet_task.SchetTask(
            handler=schet_handler.SchetHandler('dummy_cron'),
            schedule_draft=Schedule({'interval': {'seconds': 10}}),
            kwargs={'raise_error': True},
            created_by='__created_by__',
            store_id=store.store_id,
        )
        await task.save()
        tap.ok(task, 'task created')

        tasks = await schet_task.SchetTask.list(by='full', conditions=[
            ('store_id', store.store_id),
            ('status', 'paused'),
        ])
        tap.eq(tasks.list, [task], 'paused task fetched')

        tasks = await schet_task.SchetTask.list(by='full', conditions=[
            ('store_id', store.store_id),
            ('status', 'pending'),
        ])
        tap.eq(tasks.list, [], 'pending task not fetched')

        await task.approve('__approved_by__')
        await task.start()

        tasks = await schet_task.SchetTask.list(by='full', conditions=[
            ('store_id', store.store_id),
            ('status', 'pending'),
        ])
        tap.eq(tasks.list, [task], 'pending task fetched')


async def test_schedule_changing(tap, time_mock, push_events_cache, job):
    with tap.plan(10, 'изменяем расписание после запуска'):
        task = schet_task.SchetTask(
            handler=schet_handler.SchetHandler('dummy_cron'),
            schedule_draft=Schedule({
                'interval': {'seconds': 10},
                'start_time': time_mock.now(),
            }),
            created_by='__created_by__',
        )
        await task.save()
        await task.approve('__approved_by__')
        await task.start()
        tap.ok(task, 'task created')

        await task.delay()
        tap.eq(task.status, 'delayed', 'task delayed')

        await process_jobs(tap, push_events_cache, job, task)
        await task.reload()
        tap.eq(task.status, 'pending', 'task proceeded')

        tap.ok(not task.should_run(), 'time has not come')
        time_mock.sleep(seconds=10)
        tap.ok(task.should_run(), 'time has come')

        task.schedule_draft = Schedule({
            'interval': {'seconds': 10},
            'start_time': (
                task.schedule.start_time + datetime.timedelta(seconds=5)
            ),
        })
        await task.approve('__approved_by__')

        tap.ok(not task.should_run(), 'time has not come')
        time_mock.sleep(seconds=3)
        tap.ok(not task.should_run(), 'time has not come')
        time_mock.sleep(seconds=2)
        tap.ok(task.should_run(), 'time has come')


async def test_start_after_long_pause(tap, time_mock, push_events_cache, job):
    with tap.plan(9, 'обновляем время запуска после старта'):
        task = schet_task.SchetTask(
            handler=schet_handler.SchetHandler('dummy_cron'),
            schedule_draft=Schedule({
                'interval': {'seconds': 10},
                'start_time': time_mock.now(),
            }),
            created_by='__created_by__',
        )
        await task.save()
        await task.approve('__approved_by__')
        await task.start()
        tap.eq(task.status, 'pending', 'task started')

        await task.delay()
        tap.eq(task.status, 'delayed', 'task delayed')

        await process_jobs(tap, push_events_cache, job, task)
        await task.reload()
        tap.eq(task.status, 'pending', 'task proceeded')

        tap.ok(not task.should_run(), 'time has not come')
        await task.pause()

        time_mock.sleep(seconds=30)
        tap.ok(not task.should_run(), 'task paused')

        await task.start()
        tap.ok(not task.should_run(), 'time has not come')
        time_mock.sleep(seconds=10)
        tap.ok(task.should_run(), 'time has come')


async def process_jobs(tap, push_events_cache, job, task):
    await push_events_cache(task, job_method='run')
    task = await job.take()
    tap.ok(task, 'job received task')
    res = await job.call(task)
    task_ack = await job.ack(task)
    tap.ok(task_ack, 'job task ack')
    return res


@pytest.fixture(autouse=True)
def crons_config_mock(monkeypatch):
    # pylint: disable=protected-access
    monkeypatch.setattr(
        schet_handler, 'SCHETS',
        schet_handler._load_schets('tests/model/schet_handler/schets.yaml')
    )
