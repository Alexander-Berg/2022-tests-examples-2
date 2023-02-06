# pylint: disable=import-error
import datetime

import pytest

from geobus_tools import geobus  # noqa: F401 C5521

STRATEGY_CALCULATED_NAME = 'strategy-calculated'
CHANNEL_NAME = 'channel:yagr:signal_v2'
POSITIONS_HISTORY_CLEANUP_NAME = 'positions-history-cleanup-finished'


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
@pytest.mark.suspend_periodic_tasks('positions_history_cleanup')
@pytest.mark.now('2020-04-21T12:17:43.786+0000')
@pytest.mark.config(
    COORD_CONTROL_STORAGE_SETTINGS_V2={
        'max_performer_age': 2,
        'update_expiration_time': 1800,
        'alive_timeout': 60,
    },
)
async def test_history_cleaner(
        taxi_coord_control, redis_store, load_json, testpoint, mocked_time,
):
    await taxi_coord_control.tests_control(invalidate_caches=False)

    @testpoint(POSITIONS_HISTORY_CLEANUP_NAME)
    def cleanup_finished(data):
        return data

    @testpoint(STRATEGY_CALCULATED_NAME)
    def strategy_calculated(data):
        return data

    await taxi_coord_control.enable_testpoints()

    messages = load_json('geobus_messages.json')

    fbs_message = geobus.serialize_signal_v2(messages, datetime.datetime.now())

    # publish to coord-control input channel
    redis_store.publish(CHANNEL_NAME, fbs_message)

    performer_ids = set()
    for _ in range(3):
        performer_ids.add(
            (await strategy_calculated.wait_call())['data']['performer_id'],
        )
    assert performer_ids == {'dbid_uuid_0', 'dbid_uuid_1', 'dbid_uuid_2'}

    mocked_time.set(datetime.datetime(2020, 4, 21, 12, 18, 44))
    await taxi_coord_control.run_periodic_task('Cleaner')

    cleanup_result = (await cleanup_finished.wait_call())['data']
    assert sorted(cleanup_result) == ['dbid_uuid_1', 'dbid_uuid_2']
