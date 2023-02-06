# pylint: disable=redefined-outer-name,unused-variable,no-method-argument
import datetime

from driver_referrals.generated.cron import run_cron


async def test_task_generator():
    await run_cron.main(['driver_referrals.jobs.task_generator', '-t', '0'])


async def test_task_generator_auto(cron_context):
    await run_cron.main(
        ['driver_referrals.jobs.task_generator', '-t', '0', '-d'],
    )
    async with cron_context.pg.master_pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM tasks')
    assert len(rows) == 1

    # check that auto-tasks do not duplicate
    await run_cron.main(
        ['driver_referrals.jobs.task_generator', '-t', '0', '-d'],
    )
    async with cron_context.pg.master_pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM tasks')
    assert len(rows) == 1


async def test_task_generator_manual(cron_context):
    await run_cron.main(
        [
            'driver_referrals.jobs.task_generator',
            '-t',
            '0',
            '-d',
            '--date',
            '2019-02-02',
        ],
    )
    async with cron_context.pg.master_pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM tasks WHERE is_manual = true')
    assert [row['task_date'] for row in rows] == [
        datetime.datetime(2019, 2, 2),
    ]

    await run_cron.main(
        [
            'driver_referrals.jobs.task_generator',
            '-t',
            '0',
            '-d',
            '--date',
            '2019-02-02 23:00',
        ],
    )
    async with cron_context.pg.master_pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM tasks WHERE is_manual = true')
    assert [row['task_date'] for row in rows] == [
        datetime.datetime(2019, 2, 2),
        datetime.datetime(2019, 2, 2),
    ]
