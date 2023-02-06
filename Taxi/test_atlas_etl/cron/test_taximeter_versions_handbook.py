import datetime

import pytest

from atlas_etl.generated.cron import run_cron

EXPECTED_CH_QUERY = """SELECT
    DISTINCT taximeter_version
FROM atlas.ods_order
ARRAY JOIN candidates_taximeter_version AS taximeter_version
WHERE
    1656850800 <= dttm_utc_1_min AND dttm_utc_1_min < 1657023600
    AND taximeter_version != \'\';
"""

NOW = datetime.datetime(2022, 7, 5, 12, 20, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['fill_taximeter_versions.sql'],
)
@pytest.mark.config(
    ATLAS_BACKEND_ETL_CONTROL={
        'atlas_etl': {
            'update_taximeter_version_handbook': {'run_permission': True},
        },
    },
)
async def test_update_taximeter_versions(clickhouse_client_mock, patch, pgsql):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        assert args[0] == EXPECTED_CH_QUERY
        return ('9.97 (8246)',), ('12.00 (15167)',), ('9.99 (8371)',)

    await run_cron.main(
        ['atlas_etl.crontasks.update_taximeter_version_handbook', '-t', '0'],
    )

    cursor = pgsql['taxi_db_postgres_atlas_backend'].cursor()
    cursor.execute(
        'SELECT taximeter_version '
        'from taxi_db_postgres_atlas_backend.taximeter_versions',
    )
    result = {row[0] for row in cursor}
    assert result == {
        '11.11 (3014662)',
        '12.00 (15167)',
        '9.99 (8371)',
        '9.97 (8246)',
    }
