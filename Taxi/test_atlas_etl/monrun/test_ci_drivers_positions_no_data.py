import pytest

from atlas_etl.generated.cron import run_monrun

_MODULE = 'atlas_etl.monrun.ci_drivers_positions.check_no_data'


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend',
    files=['pg_taxi_db_postgres_atlas_backend.sql'],
)
@pytest.mark.now('2021-12-20T10:12:15')
async def test_data_present(patch, clickhouse_client_mock):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        return [(1000,)]

    result = await run_monrun.run([_MODULE])
    expected = (
        '0; Checked data in interval '
        '[2021-12-20 10:09; 2021-12-20 10:12). Row count: 1000'
    )
    assert result == expected


@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend',
    files=['pg_taxi_db_postgres_atlas_backend.sql'],
)
@pytest.mark.now('2021-12-20T10:12:15')
async def test_no_data(patch, clickhouse_client_mock):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        return [(0,)]

    result = await run_monrun.run([_MODULE])
    expected = (
        '2; Checked data in interval '
        '[2021-12-20 10:09; 2021-12-20 10:12). Row count: 0'
    )
    assert result == expected
