# pylint: disable=import-error

import datetime

import pytest

from geobus_tools import geobus  # noqa: F401 C5521


CHANNEL_NAME = 'channel:yagr:signal_v2'
INTERESTING_POINTS_REMOVED_NAME = 'interesting-points-removed'
MESSAGE_HANDLED = 'message-handled'
PERFORMER_FROM_PUBSUB_NAME = 'performer-from-pubsub-received'

# To save yt logs locally you need to change
# $BUILD_DIR/services/coord-control/testsuite/configs/service.yaml
# #components_manager/components/logging/loggers/
# yt-logger-coord_control_strategy/file_path = <any path>


def get_yt_log_file(build_dir: str):
    config_path = build_dir
    config_path += '/services/coord-control/testsuite/configs/service.yaml'

    with open(config_path, 'r') as config:
        found = False
        for line in config:
            if found:
                line = (
                    line.replace('\n', '')
                    .replace('\t', '')
                    .replace('\'', '')
                    .replace(' ', '')
                )
                return line.split(':')[1]
            if 'yt-logger-coord_control_strategy:' in line:
                found = True
    return None


def dt_from_ts(ts_ms: int) -> datetime.datetime:
    timestamp = int(str(ts_ms)[:-3])
    return datetime.datetime.utcfromtimestamp(timestamp)


async def _publish_message(message, redis_store, message_handled):
    fbs_message = geobus.serialize_signal_v2(message, datetime.datetime.now())
    redis_store.publish(CHANNEL_NAME, fbs_message)

    assert await message_handled.wait_call()


@pytest.mark.xfail(reason='Running only on local machine')
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
        'radius': 750,
        'points_ttl': 720,
        'detector_batch_size': 50,
        'cleanup_batch_size': 50,
        'minimum_points_for_detection': 10,
        'points_weight_threshold_applied': 1.25,
    },
)
async def test_gps_jump_by_history(
        taxi_coord_control, redis_store, load_json, testpoint, mocked_time,
):
    # change to signals filepath
    signals_loc = None

    # change to you build directory
    build_dir = '/tmp/uservices-build/build'

    @testpoint(MESSAGE_HANDLED)
    def message_handled(data):
        return data

    await taxi_coord_control.enable_testpoints()

    assert signals_loc is not None
    signals = load_json(signals_loc)
    signals = sorted(signals, key=lambda signal: signal['unix_time'])

    log_file = get_yt_log_file(build_dir)
    assert log_file != '@null'
    open(log_file, 'w').close()

    ticks = 1
    start = 0
    while start < len(signals):
        now = dt_from_ts(signals[start]['unix_time'])
        now += datetime.timedelta(seconds=1.0)
        mocked_time.set(now)
        await taxi_coord_control.tests_control(invalidate_caches=False)

        end = start + 1
        while (
                end < len(signals)
                and dt_from_ts(signals[end]['unix_time']) < now
        ):
            if (end - start) > 200:
                break
            end += 1

        print(f'Sent {end - start} signals')

        await _publish_message(
            signals[start:end], redis_store, message_handled,
        )
        if ticks % 120 == 0:
            await taxi_coord_control.run_periodic_task('bad_areas_detector')
            await taxi_coord_control.run_periodic_task('Cleaner')
        start = end
        ticks += 1
