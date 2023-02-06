import datetime

from hiring_data_markup.generated.cron import run_cron as run_cron_module

CRON_ADDRESS = 'hiring_data_markup.crontasks.delete_old_history'
DB = 'hiring_data_markup'


async def run_cron():
    return await run_cron_module.main([CRON_ADDRESS, '-t', '0'])


async def test_delete_old_history(pgsql, insert_data_markup_history):
    date = (
        datetime.datetime.utcnow() - datetime.timedelta(days=365, hours=1)
    ).strftime('%Y-%m-%d %H:%M:%S')
    await insert_data_markup_history(date)
    with pgsql[DB].cursor() as cursor:
        cursor.execute(f'SELECT * FROM hiring_data_markup.history ')
        assert cursor.rowcount
    await run_cron()
    with pgsql[DB].cursor() as cursor:
        cursor.execute(f'SELECT * FROM hiring_data_markup.history ')
        assert not cursor.rowcount


async def test_not_delete_not_old_history(pgsql, insert_data_markup_history):
    date = (
        datetime.datetime.utcnow() - datetime.timedelta(days=364, hours=20)
    ).strftime('%Y-%m-%d %H:%M:%S')
    await insert_data_markup_history(date)
    with pgsql[DB].cursor() as cursor:
        cursor.execute(f'SELECT * FROM hiring_data_markup.history ')
        assert cursor.rowcount
    await run_cron()
    with pgsql[DB].cursor() as cursor:
        cursor.execute(f'SELECT * FROM hiring_data_markup.history ')
        assert cursor.rowcount
