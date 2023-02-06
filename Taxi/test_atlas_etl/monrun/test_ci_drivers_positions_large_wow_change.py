import pytest

from atlas_etl.generated.cron import run_monrun

_MODULE = 'atlas_etl.monrun.ci_drivers_positions.check_large_wow_change'


@pytest.mark.now('2021-12-20T10:12:15')
@pytest.mark.parametrize(
    'rows_counts, expected_result',
    [
        (
            [1250, 1000],
            '0; Compare row count in interval '
            '[2021-12-19 10:12; 2021-12-20 10:12) vs '
            '[2021-12-12 10:12; 2021-12-13 10:12). '
            'Wow change: 25.0%',
        ),
        (
            [750, 1000],
            '0; Compare row count in interval '
            '[2021-12-19 10:12; 2021-12-20 10:12) vs '
            '[2021-12-12 10:12; 2021-12-13 10:12). '
            'Wow change: -25.0%',
        ),
        (
            [1500, 1000],
            '2; Compare row count in interval '
            '[2021-12-19 10:12; 2021-12-20 10:12) vs '
            '[2021-12-12 10:12; 2021-12-13 10:12). '
            'Wow change: 50.0%',
        ),
        (
            [500, 1000],
            '2; Compare row count in interval '
            '[2021-12-19 10:12; 2021-12-20 10:12) vs '
            '[2021-12-12 10:12; 2021-12-13 10:12). '
            'Wow change: -50.0%',
        ),
    ],
)
@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend',
    files=['pg_taxi_db_postgres_atlas_backend.sql'],
)
async def test_large_wow(
        patch, clickhouse_client_mock, rows_counts, expected_result,
):
    _ch_data = iter(rows_counts)

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        count = next(_ch_data)
        return [(count,)]

    result = await run_monrun.run([_MODULE])
    assert result == expected_result
