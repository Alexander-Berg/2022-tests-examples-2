import pytest


@pytest.mark.config(
    DISTLOCKS_LOCKS_CLEANER_SETTINGS={
        'enabled': True,
        'period_secs': 60,
        'removal_delay_secs': 300,
    },
)
@pytest.mark.suspend_periodic_tasks('locks-cleaner')
async def test_locks_cleaner(taxi_distlocks, pgsql):
    pg_cursor = pgsql['distlocks'].cursor()
    await taxi_distlocks.run_periodic_task('locks-cleaner')
    pg_cursor.execute('SELECT name FROM distlocks.locks;')
    rows = pg_cursor.fetchall()
    assert {row[0] for row in rows} == {'lock3', 'lock4'}
