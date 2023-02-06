import datetime

from dateutil import tz
import pytest

pytest_plugins = ['taxi_testsuite.plugins.mocks.mock_yt']


@pytest.mark.now('2020-05-10 00:00:00')
@pytest.mark.yt(static_table_data=['yt_dm_executor_profile_act.yaml'])
@pytest.mark.config(
    LOYALTY_JOBS_SETTINGS={
        '__default__': {},
        'last_order_update': {
            'sleep': 150,
            'enabled': True,
            'pg_write_chunk_size': 100,
            'yt_read_chunk_size': 10_000,
            'hours_to_next_month_start': 32 * 24,
            'hours_to_next_month_end': 0,
            'yt_table_name': (
                '//home/taxi-dwh/cdm/supply/'
                'dm_executor_profile_act/dm_executor_profile_act'
            ),
        },
    },
)
async def test_last_order_update(
        cron_runner, mockserver, pgsql, load_json, yt_apply,
):
    await cron_runner.last_order_update()

    with pgsql['loyalty'].cursor() as cursor:
        cursor.execute(
            'SELECT unique_driver_id, last_active_at '
            'FROM loyalty.loyalty_accounts ',
        )
        last_active_times = {r[0]: r[1] for r in cursor}

    expected_accounts = load_json('expected_accounts.json')

    for expected in expected_accounts:
        udid = expected['unique_driver_id']
        last_active_time = None
        if expected['last_active_at']:
            last_active_time = datetime.datetime.fromisoformat(
                expected['last_active_at'],
            ).astimezone(tz.tzutc())
        assert last_active_times[udid] == last_active_time
