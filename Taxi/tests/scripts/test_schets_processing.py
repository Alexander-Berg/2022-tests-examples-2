# pylint: disable=protected-access,unused-argument
import datetime
import typing

import pytest

from libstall.model import coerces
from scripts.cron import schets_processing
from stall.model import schet_task, schet_handler
from stall.model.schedule import Schedule


async def test_common(tap, time_mock, job, push_events_cache):
    with tap.plan(7, 'общий цикл таска'):
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
        tap.eq(task.status, 'pending', 'task started')

        await schets_processing._process_tasks([task])
        tap.eq(task.status, 'delayed', 'task delayed')
        await process_jobs(tap, push_events_cache, job, task)
        await task.reload()
        tap.eq(task.status, 'pending', 'task proceeded')

        time_mock.sleep(seconds=5)
        await schets_processing._process_tasks([task])
        tap.eq(task.status, 'pending', 'task not delayed')
        await process_jobs(tap, push_events_cache, job, task)
        await task.reload()
        tap.eq(task.status, 'pending', 'task still pending')

        time_mock.sleep(seconds=10)
        await schets_processing._process_tasks([task])
        tap.eq(task.status, 'delayed', 'task delayed')


async def test_unknown_handler(tap, time_mock, push_events_cache, job):
    with tap.plan(4, 'таск с неизвестным хэндлером тоже запускается,'
                     ' но пишет в лог ошибку'):
        task = schet_task.SchetTask(
            handler=schet_handler.SchetHandler('unknown'),
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
        tap.eq(task.status, 'pending', 'task started')

        await schets_processing._process_tasks([task])
        tap.eq(task.status, 'delayed', 'task delayed')
        await process_jobs(tap, push_events_cache, job, task)
        await task.reload()
        tap.eq(task.status, 'pending', 'task proceeded')


async def test_failing_task(tap, time_mock, push_events_cache, job):
    with tap.plan(4, 'упавший таск остаётся в статусе running'
                     ' и перезапускается джобами'):
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
        tap.eq(task.status, 'pending', 'task started')

        await schets_processing._process_tasks([task])
        tap.eq(task.status, 'delayed', 'task delayed')
        await process_jobs(tap, push_events_cache, job, task)
        await task.reload()
        tap.eq(task.status, 'running', 'task stays running')


async def test_queue_not_working(tap, time_mock, push_events_cache, job):
    with tap.plan(13, 'очередь берёт таск после сброса статуса delayed'):
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
        tap.eq(task.status, 'pending', 'task started')

        await schets_processing._process_tasks([task])
        tap.eq(task.status, 'delayed', 'task delayed')
        delayed_at = time_mock.now()
        tap.eq(task.delayed_at, delayed_at, 'task delayed now')

        time_mock.sleep(minutes=1)

        await schets_processing._process_tasks([task])
        tap.eq(task.status, 'delayed', 'task delayed')
        tap.eq(task.delayed_at, delayed_at, 'task delayed then')

        time_mock.sleep(minutes=3)

        await schets_processing._process_tasks([task])
        tap.eq(task.status, 'delayed', 'task delayed')
        tap.eq(task.delayed_at, delayed_at, 'task delayed then')

        time_mock.sleep(minutes=1)

        await schets_processing._process_tasks([task])
        tap.eq(task.status, 'delayed', 'task delayed')
        tap.eq(task.delayed_at, delayed_at, 'task delayed then')

        total, proceeded = await process_jobs(
            tap, push_events_cache, job, task
        )
        tap.eq(total, 1, '1 task was in queue')
        tap.eq(proceeded, 1, 'task proceeded')

        await task.reload()
        tap.eq(task.status, 'pending', 'task proceeded')


async def test_running_long(tap, time_mock, push_events_cache, job):
    with tap.plan(9, 'таск долго работает, новый не ставится'):
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
        tap.eq(task.status, 'pending', 'task started')

        await schets_processing._process_tasks([task])
        tap.eq(task.status, 'delayed', 'task delayed')
        delayed_at = time_mock.now()
        tap.eq(task.delayed_at, delayed_at, 'task delayed now')

        await process_jobs(tap, push_events_cache, job, task)
        await task.reload()
        tap.eq(task.status, 'running', 'task stays running')

        time_mock.sleep(minutes=20)

        await task.reload()
        tap.eq(task.status, 'running', 'task stays running')

        await schets_processing._process_tasks([task])
        tap.eq(task.status, 'running', 'task still running')
        tap.eq(task.delayed_at, delayed_at, 'task delayed then')

        total, _ = await process_jobs(tap, push_events_cache, job, task)
        tap.eq(total, 0, 'no tasks in queue')


@pytest.mark.parametrize(
    [
        'start_time',
        'reaches',
    ],
    [
        (
            '2021-01-01T05:00:00+00:00',
            [
                '2021-01-01T05:00:00+00:00',
                '2021-01-02T05:00:00+00:00',
            ],
        ),
        (
            '2021-03-27T05:00:00+00:00',
            [
                '2021-03-27T05:00:00+00:00',
                '2021-03-28T04:00:00+00:00',
            ],
        ),
        (
            '2021-07-01T05:00:00+00:00',
            [
                '2021-07-01T04:00:00+00:00',
                '2021-07-02T04:00:00+00:00',
            ],
        ),
        (
            '2021-10-30T05:00:00+00:00',
            [
                '2021-10-30T04:00:00+00:00',
                '2021-10-31T05:00:00+00:00',
            ],
        ),
    ]
)
async def test_dst_timezone(
    tap, time_mock, push_events_cache, job, start_time, reaches
):
    with tap.plan(17, 'проверка полного цикла с учётом dst в Лондоне'):
        start_time = coerces.date_time(start_time)
        reaches = list(map(coerces.date_time, reaches))

        time_mock.set(start_time - datetime.timedelta(days=1))
        tap.note(f'[{time_mock.now()}]')

        task = schet_task.SchetTask(
            handler=schet_handler.SchetHandler('dummy_cron'),
            schedule_draft=Schedule({
                'interval': {'days': 1},
                'start_time': start_time,
            }),
            created_by='__created_by__',
            tz='Europe/London',
        )
        await task.save()
        await task.approve('__approved_by__')
        await task.start()
        tap.eq(task.status, 'pending', 'task started')
        tap.is_ok(task.next_run_at, None, 'next run not planned')

        await schets_processing._process_tasks([task])
        tap.eq(
            await process_jobs(tap, push_events_cache, job, task),
            (0, 0), 'too early to start'
        )

        for reach in reaches:
            for offset in [
                datetime.timedelta(days=-1),
                datetime.timedelta(hours=-1),
                datetime.timedelta(minutes=-1),
            ]:
                time_mock.set(reach + offset)
                tap.note(f'[{time_mock.now()}]')

                await schets_processing._process_tasks([task])
                tap.eq(
                    await process_jobs(tap, push_events_cache, job, task),
                    (0, 0), 'no tasks'
                )

            time_mock.set(reach)
            tap.note(f'[{time_mock.now()}] – reach')
            await schets_processing._process_tasks([task])
            _, proceeded = await process_jobs(
                tap, push_events_cache, job, task
            )
            tap.eq(proceeded, 1, 'task proceeded')
            await task.reload()

            for offset in [
                datetime.timedelta(minutes=1),
                datetime.timedelta(minutes=10),
                datetime.timedelta(hours=1),
            ]:
                time_mock.set(reach + offset)
                tap.note(f'[{time_mock.now()}]')

                await schets_processing._process_tasks([task])
                tap.eq(
                    await process_jobs(tap, push_events_cache, job, task),
                    (0, 0), 'no tasks'
                )


async def process_jobs(
    tap, push_events_cache, job, task
) -> typing.Tuple[int, int]:
    await push_events_cache(task, 'run')

    total = 0
    proceeded = 0

    while True:
        result = await job._worker()
        if result is None:
            break

        total += 1
        if result:
            proceeded += 1

    tap.note(f'{proceeded}/{total} tasks proceeded')
    return total, proceeded


@pytest.fixture(autouse=True)
def crons_config_mock(monkeypatch):
    # pylint: disable=protected-access
    monkeypatch.setattr(
        schet_handler, 'SCHETS',
        schet_handler._load_schets('tests/model/schet_handler/schets.yaml')
    )
