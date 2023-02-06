# pylint: disable=import-error

import datetime

import pytest

from geobus_tools import geobus  # noqa: F401 C5521


MESSAGE_HANDLED = 'message-handled'


def dt_from_ts(ts_ms: int) -> datetime.datetime:
    timestamp = int(str(ts_ms)[:-3])
    return datetime.datetime.utcfromtimestamp(timestamp)


async def _publish_message(message, redis_store, message_handled):
    fbs_message = geobus.serialize_signal_v2(message, datetime.datetime.now())
    redis_store.publish('channel:yagr:signal_v2', fbs_message)

    assert await message_handled.wait_call()


@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3_history.json')
@pytest.mark.suspend_periodic_tasks('bad_areas_detector', 'Cleaner')
@pytest.mark.config(
    COORD_CONTROL_HISTORY_SETTINGS=[
        {'points_limit': 0, 'time_bound': 5},
        {'points_limit': 50, 'time_bound': 30},
        {'points_limit': 60, 'time_bound': 90},
    ],
    COORD_CONTROL_INTERESTING_POINTS_SETTINGS={
        'radius': 5000,
        'points_ttl': 600,
        'detector_batch_size': 50,
        'cleanup_batch_size': 50,
        'minimum_points_for_detection': 3,
        'points_weight_threshold_applied': 1,
    },
)
@pytest.mark.parametrize(
    'test_case_idx',
    list(range(4)),
    ids=[
        'Reference exists, good zone',
        'No references, good zone',
        'No references, bad zone',
        'Reference lags at first, gsm is bad',
    ],
)
async def test_simple_jump_and_return(
        taxi_coord_control,
        redis_store,
        load_json,
        testpoint,
        mocked_time,
        test_case_idx,
):
    """
    Gps jumps and returns for all cases 0-2

    For the 3rd case, yandex_lbs_gsm is received first and becomes
    good without references (good zone), but when reference
    is received we should check it
    """

    # Reset service state
    await taxi_coord_control.invalidate_caches()

    @testpoint(MESSAGE_HANDLED)
    def message_handled(data):
        return data

    await taxi_coord_control.enable_testpoints()

    signals = load_json(f'signals_{test_case_idx}.json')
    signals = sorted(signals, key=lambda s: s['unix_time'])
    start = 0
    while start < len(signals):
        now = dt_from_ts(signals[start]['unix_time'])
        now += datetime.timedelta(seconds=1)
        mocked_time.set(now)
        await taxi_coord_control.tests_control(invalidate_caches=False)

        end = start + 1
        while (
                end < len(signals)
                and dt_from_ts(signals[end]['unix_time']) < now
        ):
            end += 1

        await _publish_message(
            signals[start:end], redis_store, message_handled,
        )
        await taxi_coord_control.run_periodic_task('bad_areas_detector')
        await taxi_coord_control.run_periodic_task('Cleaner')
        start = end

    response = await taxi_coord_control.post(
        '/atlas/primary_group_change', json={'dbid_uuid': 'dead_b0d4'},
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        f'primary_group_change_{test_case_idx}.json',
    )
