import pytest


@pytest.mark.config(
    DISTLOCKS_NAMESPACES_SYNCHRONIZER_SETTINGS={
        'enabled': True,
        'period_secs': 60,
    },
    DISTLOCKS_NAMESPACES=['namespace3', 'namespace4'],
)
@pytest.mark.suspend_periodic_tasks('namespaces-synchronizer')
async def test_namespaces_synchronizer(taxi_distlocks, pgsql):
    pg_cursor = pgsql['distlocks'].cursor()
    await taxi_distlocks.run_periodic_task('namespaces-synchronizer')
    pg_cursor.execute('SELECT name FROM distlocks.namespaces;')
    rows = pg_cursor.fetchall()
    assert {row[0] for row in rows} == {'namespace3', 'namespace4'}
