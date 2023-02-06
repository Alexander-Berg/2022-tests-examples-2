import datetime
import decimal

import pytest

from taxi.util import dates

from atlas_etl.generated.cron import run_cron

NOW = datetime.datetime(2021, 3, 10, 6, 15, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    ATLAS_BACKEND_ETL_CONTROL={
        'atlas_etl': {
            'ods.food_couriers': {
                'run_modes': {'atlas_clickhouse_mdb': True, 'logbroker': True},
                'run_permission': True,
            },
        },
    },
)
async def test_food_couriers(
        atlas_mysql_client_mock,
        clickhouse_client_mock,
        fix_ch_insert_data,
        load,
        load_py_json,
        db,
        patch,
):
    @patch('atlas_mysql.pytest_plugin.MysqlPoolWrapperMock.fetchall')
    async def _fetchall(*args, **kwargs):
        query = args[0]
        expected_query = load('food_couriers_query.sql')
        assert query == expected_query
        mysql_answer = load_py_json(
            'food_couriers_mysql_answer.json',
            {'$decimal': decimal.Decimal, '$date': dates.parse_timestring},
        )
        return mysql_answer

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        data = kwargs.get('params')
        data = fix_ch_insert_data(data)
        expected_ch_insert = load_py_json('food_couriers_ch_insert.json')
        assert data == expected_ch_insert
        return len(data)

    @patch('atlas_etl.loaders.common.DataLoader._write_to_logbroker')
    async def _write_to_logbroker_mock(data, *_):
        assert data == load_py_json('food_couriers_lb_insert.json')

    await run_cron.main(['atlas_etl.crontasks.food_couriers', '-t', '0'])
