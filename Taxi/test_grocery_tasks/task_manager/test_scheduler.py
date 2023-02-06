import datetime

import pytest

from taxi.util import dates

from grocery_tasks.task_manager import dates_util
from grocery_tasks.task_manager import scheduler as scheduler_module


@pytest.mark.now('2020-03-17T06:30:00')  # UTC
@pytest.mark.parametrize(
    'cron_schedule, needs_run, expected_timedelta',
    [
        ('30 9 * * *', True, datetime.timedelta(seconds=0)),
        ('29 9 * * *', False, datetime.timedelta(hours=23, minutes=59)),
        ('31 9 * * *', False, datetime.timedelta(minutes=1)),
        (None, False, None),
    ],
)
async def test_set_cron_schedule(
        cron_context, cron_schedule, needs_run, expected_timedelta,
):
    scheduler = scheduler_module.TaskScheduler(
        cron_context.pg.grocery_tasks, cron_context.sqlt,
    )
    if cron_schedule is not None:
        await scheduler.set_cron_schedule('task', cron_schedule)  # Moscow
    now = dates_util.get_now()

    for scheduler_inst in [
            scheduler,
            scheduler_module.TaskScheduler(
                cron_context.pg.grocery_tasks, cron_context.sqlt,
            ),
    ]:
        schedule = await scheduler_inst.load(['task'])
        assert schedule['task'].needs_run(now) == needs_run
        if expected_timedelta is not None:
            assert (
                schedule['task'].get_next_run(now) == now + expected_timedelta
            )
        else:
            assert schedule['task'].get_next_run(now) is None


async def test_set_schedule_errors(cron_context):
    scheduler = scheduler_module.TaskScheduler(
        cron_context.pg.grocery_tasks, cron_context.sqlt,
    )
    with pytest.raises(TypeError):
        await scheduler.set_cron_schedule('fail', '1 2 * * * *')
    with pytest.raises(TypeError):
        await scheduler.set_cron_schedule('fail', 'abc 2 * * *')

    await scheduler.set_next_run(
        'abc',
        dates.localize(
            datetime.datetime(2020, 3, 17, 9, 29), dates_util.CRON_TZ,
        ),
    )
    schedule = await scheduler.load(['abc'])
    with pytest.raises(TypeError):
        schedule['abc'].get_next_run(datetime.datetime.now())


@pytest.mark.now('2020-03-17T06:30:00')  # UTC
@pytest.mark.parametrize(
    'next_run, needs_run, expected_next_run',
    [
        (
            dates.localize(
                datetime.datetime(2020, 3, 17, 6, 29), dates_util.CRON_TZ,
            ),
            False,
            None,
        ),
        (
            dates.localize(
                datetime.datetime(2020, 3, 17, 6, 30), dates_util.CRON_TZ,
            ),
            True,
            dates.localize(
                datetime.datetime(2020, 3, 17, 6, 30), dates_util.CRON_TZ,
            ),
        ),
        (
            dates.localize(
                datetime.datetime(2020, 3, 17, 6, 31), dates_util.CRON_TZ,
            ),
            False,
            dates.localize(
                datetime.datetime(2020, 3, 17, 6, 31), dates_util.CRON_TZ,
            ),
        ),
    ],
)
async def test_set_next_run(
        cron_context, next_run, needs_run, expected_next_run,
):
    scheduler = scheduler_module.TaskScheduler(
        cron_context.pg.grocery_tasks, cron_context.sqlt,
    )
    await scheduler.set_next_run('abc', next_run)
    for scheduler_inst in [
            scheduler,
            scheduler_module.TaskScheduler(
                cron_context.pg.grocery_tasks, cron_context.sqlt,
            ),
    ]:
        schedule = await scheduler_inst.load(['abc'])
        now = dates_util.get_now()
        assert schedule['abc'].needs_run(now) == needs_run
        assert schedule['abc'].get_next_run(now) == expected_next_run
        assert schedule['abc'].get_next_run() == expected_next_run
