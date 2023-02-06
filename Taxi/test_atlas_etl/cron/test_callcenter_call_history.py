# pylint: disable=redefined-outer-name
import datetime

import pytest

from atlas_etl.generated.cron import run_cron


NOW = datetime.datetime(2019, 9, 3, 12, 20, 0)


@pytest.mark.now(NOW.isoformat())
@pytest.mark.pgsql(
    'taxi_db_postgres_atlas_backend', files=['fill_full_geo_hierarchy.sql'],
)
@pytest.mark.pgsql(
    'callcenter_stats', files=['fill_callcenter_call_history.sql'],
)
@pytest.mark.config(
    CALLCENTER_STATS_CALLCENTER_PHONE_INFO_MAP={
        '+74959999997': {
            'application': 'call_center',
            'city_name': 'Москва',
            'geo_zone_coords': {'lat': 55.755814, 'lon': 37.617635},
        },
        '+74959999998': {
            'application': 'call_center_spb',
            'city_name': 'Санкт-Петербург',
            'geo_zone_coords': {'lat': 59.939095, 'lon': 30.315868},
        },
        '__default__': {
            'application': 'default_app',
            'city_name': 'Неизвестно',
            'geo_zone_coords': {'lat': 0, 'lon': 0},
        },
    },
)
@pytest.mark.config(
    ATLAS_BACKEND_ETL_CONTROL={
        'atlas_etl': {
            'ods.callcenter_call_history': {
                'run_modes': {'atlas_clickhouse_mdb': True},
                'run_permission': True,
            },
        },
    },
)
async def test_callcenter_call_history(
        clickhouse_client_mock, load_json, db, patch,
):
    expected_ch_insert = load_json('expected_ch_insert.json')

    @patch('atlas_clickhouse.pytest_plugin.ClientMock.execute')
    async def _execute(*args, **kwargs):
        data = kwargs.get('params')
        for row in data:
            for key in row:
                if isinstance(row[key], datetime.datetime):
                    row[key] = row[key].isoformat()
        assert data == expected_ch_insert
        return len(data)

    await run_cron.main(
        ['atlas_etl.crontasks.callcenter_call_history', '-t', '0'],
    )

    etl_info = await db.atlas_etl_control.find_one(
        {'etl_name': 'ods.callcenter_call_history'},
    )
    assert etl_info['last_upload_date'] == datetime.datetime(
        2019, 9, 3, 12, 14, 0,
    )
