import datetime
import decimal

import pytest

from taxi.util import dates

from atlas_etl.generated.cron import run_cron
from atlas_etl.processes import food_transform_methods

NOW = datetime.datetime(2021, 3, 10, 6, 15, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    ATLAS_BACKEND_ETL_CONTROL={
        'atlas_etl': {
            'ods.food_orders': {
                'run_modes': {'atlas_clickhouse_mdb': True, 'logbroker': True},
                'run_permission': True,
            },
        },
    },
)
async def test_food_orders(
        atlas_mysql_client_mock,
        clickhouse_client_mock,
        fix_ch_insert_data,
        load,
        load_py_json,
        db,
        patch,
):
    mysql_max_dttm = (
        NOW + datetime.timedelta(hours=3) - datetime.timedelta(minutes=1)
    )

    @patch('atlas_mysql.pytest_plugin.MysqlPoolWrapperMock.fetchone')
    async def _fetchone(*args, **kwargs):
        mysql_answer = {'value': mysql_max_dttm}
        return mysql_answer

    @patch('atlas_mysql.pytest_plugin.MysqlPoolWrapperMock.fetchall')
    async def _fetchall(*args, **kwargs):
        query = args[0]
        expected_query = load('food_orders_query.sql').format(
            start_date='\'2021-03-10 09:07:00\'',
            end_date='\'2021-03-10 09:14:00\'',
        )
        assert query == expected_query
        mysql_answer = load_py_json(
            'food_orders_mysql_answer.json',
            {'$decimal': decimal.Decimal, '$date': dates.parse_timestring},
        )
        return mysql_answer

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        data = kwargs.get('params')
        data = fix_ch_insert_data(data)
        expected_ch_insert = load_py_json('food_orders_ch_insert.json')
        assert data == expected_ch_insert
        return len(data)

    @patch('atlas_etl.loaders.common.DataLoader._write_to_logbroker')
    async def _write_to_logbroker_mock(data, *_):
        assert data == load_py_json('food_orders_lb_insert.json')

    await run_cron.main(['atlas_etl.crontasks.food_orders', '-t', '0'])

    etl_info = await db.atlas_etl_control.find_one(
        {'etl_name': 'ods.food_orders'},
    )

    assert etl_info['last_upload_date'] == NOW - datetime.timedelta(minutes=1)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    ATLAS_BACKEND_ETL_CONTROL={
        'atlas_etl': {
            'ods.food_orders': {
                'run_modes': {'atlas_clickhouse_mdb': True},
                'run_permission': True,
            },
        },
    },
)
async def test_food_orders_custom_args(
        atlas_mysql_client_mock,
        clickhouse_client_mock,
        load,
        load_json,
        db,
        patch,
):
    @patch('atlas_mysql.pytest_plugin.MysqlPoolWrapperMock.fetchone')
    async def _fetchone(*args, **kwargs):
        raise RuntimeError('This method must not be used!')

    @patch('atlas_mysql.pytest_plugin.MysqlPoolWrapperMock.fetchall')
    async def _fetchall(*args, **kwargs):
        query = args[0]
        expected_query = load('food_orders_query.sql').format(
            start_date='\'2021-03-10 08:30:00\'',
            end_date='\'2021-03-10 08:50:00\'',
        )
        assert query == expected_query
        return []

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        raise RuntimeError('This method must not be used!')

    etl_info = await db.atlas_etl_control.find_one(
        {'etl_name': 'ods.food_orders'},
    )

    dttm_before = etl_info['last_upload_date']

    await run_cron.main(
        [
            'atlas_etl.crontasks.food_orders',
            '-t',
            '0',
            '--start_dttm',
            '2021-03-10 05:30:00',
            '--end_dttm',
            '2021-03-10 05:50:00',
            '--no-update_load_info',
        ],
    )

    etl_info = await db.atlas_etl_control.find_one(
        {'etl_name': 'ods.food_orders'},
    )

    assert etl_info['last_upload_date'] == dttm_before


@pytest.mark.now(NOW.isoformat())
@pytest.mark.config(
    ATLAS_BACKEND_ETL_CONTROL={
        'atlas_etl': {
            'ods.food_orders': {
                'run_modes': {'atlas_clickhouse_mdb': True},
                'run_permission': True,
            },
        },
    },
)
async def test_food_orders_fail_ch_insert(
        atlas_mysql_client_mock,
        clickhouse_client_mock,
        fix_ch_insert_data,
        load,
        load_py_json,
        db,
        patch,
):
    mysql_max_dttm = (
        NOW + datetime.timedelta(hours=3) - datetime.timedelta(minutes=1)
    )

    class CHError(Exception):
        pass

    @patch('atlas_mysql.pytest_plugin.MysqlPoolWrapperMock.fetchone')
    async def _fetchone(*args, **kwargs):
        mysql_answer = {'value': mysql_max_dttm}
        return mysql_answer

    @patch('atlas_mysql.pytest_plugin.MysqlPoolWrapperMock.fetchall')
    async def _fetchall(*args, **kwargs):
        query = args[0]
        expected_query = load('food_orders_query.sql').format(
            start_date='\'2021-03-10 09:07:00\'',
            end_date='\'2021-03-10 09:14:00\'',
        )
        assert query == expected_query
        mysql_answer = load_py_json(
            'food_orders_mysql_answer.json',
            {'$decimal': decimal.Decimal, '$date': dates.parse_timestring},
        )
        return mysql_answer

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        raise CHError('Ch insert failed!')

    etl_info = await db.atlas_etl_control.find_one(
        {'etl_name': 'ods.food_orders'},
    )

    dttm_before = etl_info['last_upload_date']

    with pytest.raises(CHError) as excinfo:
        await run_cron.main(['atlas_etl.crontasks.food_orders', '-t', '0'])

    assert str(excinfo.value) == 'Ch insert failed!'

    etl_info = await db.atlas_etl_control.find_one(
        {'etl_name': 'ods.food_orders'},
    )

    assert etl_info['last_upload_date'] == dttm_before


@pytest.mark.parametrize(
    'timezone,expected_offset',
    [
        ('Asia/Almaty', 21600),
        ('Asia/Novosibirsk', 25200),
        ('Asia/Vladivostok', 36000),
        ('Asia/Yekaterinburg', 18000),
        ('Europe/Kaliningrad', 7200),
        ('Europe/Lisbon', 0),
        ('Europe/London', 0),
        ('Europe/Minsk', 10800),
        ('Europe/Moscow', 10800),
        ('Europe/Paris', 3600),
        ('NotExisting', None),
        (None, None),
    ],
)
def test_extract_local_offset(timezone, expected_offset):
    dttm_utc = food_transform_methods.convert_to_utc(
        datetime.datetime(2022, 3, 10, 12, 31, 45),
    )
    offset = food_transform_methods.extract_local_offset_sec(
        dttm_utc, timezone,
    )
    assert offset == expected_offset
