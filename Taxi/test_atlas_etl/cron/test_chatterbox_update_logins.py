import datetime

import pytest

from atlas_etl.generated.cron import run_cron

EXPECTED_CH_QUERY = """SELECT
    DISTINCT login
FROM ods.chatterbox_stats
WHERE
    1655814000 <= utc_created_dttm and utc_created_dttm < 1657023600;
"""

NOW = datetime.datetime(2022, 7, 5, 12, 20, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['fill_chatterbox_logins.sql'],
)
@pytest.mark.config(
    ATLAS_BACKEND_ETL_CONTROL={
        'atlas_etl': {'chatterbox_update_logins': {'run_permission': True}},
    },
)
async def test_update_chatterbox_logins(clickhouse_client_mock, patch, pgsql):
    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        assert args[0] == EXPECTED_CH_QUERY
        return ('login_1',), ('login_2',)

    await run_cron.main(
        ['atlas_etl.crontasks.chatterbox_update_logins', '-t', '0'],
    )

    cursor = pgsql['taxi_db_postgres_atlas_backend'].cursor()
    cursor.execute(
        'SELECT login from taxi_db_postgres_atlas_backend.chatterbox_logins',
    )
    result = {row[0] for row in cursor}
    assert result == {'login_1', 'login_2', 'login_3'}
