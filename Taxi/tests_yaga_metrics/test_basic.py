# flake8: noqa
# pylint: disable=import-error
from geobus_tools.channels import universal_signals
import pytest

YAGA_TEST_INPUT_CHANNEL_UNIVERSAL = 'channel:test:positions_universal@0'
YAGA_TEST_INPUT_CHANNEL_ADJUSTED_UNIVERSAL = (
    'channel:test:adjusted_universal@0'
)


class NextDriverId:
    yaga_next_driver_id = 10

    @staticmethod
    def get_next_id():
        NextDriverId.yaga_next_driver_id += 1
        return NextDriverId.yaga_next_driver_id - 1


@pytest.mark.now('2019-09-11T13:42:15+0300')
async def test_basic_check(taxi_yaga_metrics, redis_store, testpoint, now):
    @testpoint('write-position-to-yt-adjusted')
    def on_position_written_yt_adj(data):
        pass

    @testpoint('write-position-to-yt-raw')
    def on_position_written_yt_raw(data):
        pass

    await taxi_yaga_metrics.enable_testpoints()

    unique_timestamp_test = 1514764810
    track_test = _make_track(unique_timestamp_test)

    universal_message = _make_universal_message_from_track(track_test)
    input_universal_message = universal_signals.serialize_message(
        universal_message, now,
    )

    universal_listener_raw = redis_store.pubsub()
    _subscribe(universal_listener_raw, YAGA_TEST_INPUT_CHANNEL_UNIVERSAL)
    _read_all(universal_listener_raw)

    redis_store.publish(
        YAGA_TEST_INPUT_CHANNEL_UNIVERSAL, input_universal_message,
    )

    universal_listener_adjusted = redis_store.pubsub()
    _subscribe(
        universal_listener_adjusted,
        YAGA_TEST_INPUT_CHANNEL_ADJUSTED_UNIVERSAL,
    )
    _read_all(universal_listener_adjusted)

    redis_store.publish(
        YAGA_TEST_INPUT_CHANNEL_ADJUSTED_UNIVERSAL, input_universal_message,
    )

    await on_position_written_yt_adj.wait_call()
    await on_position_written_yt_raw.wait_call()

    await _check_service_is_alive(taxi_yaga_metrics)


def _make_track(timestamp=1514764800):
    track = [
        {
            'speed': 16.6,
            'lon': 37.698035 + (timestamp % 10) * 0.0001,
            'lat': 55.721591,
            'timestamp': timestamp,
        },
        {
            'speed': 16.6,
            'lon': 37.699561 + (timestamp % 10) * 0.0001,
            'timestamp': timestamp + 7,
            'lat': 55.720928,
        },
        {
            'lon': 37.69938 + (timestamp % 10) * 0.0001,
            'speed': 16.6,
            'lat': 55.720603,
            'timestamp': timestamp + 9,
        },
        {
            'lon': 37.69782 + (timestamp % 10) * 0.0001,
            'speed': 16.6,
            'lat': 55.720206,
            'timestamp': timestamp + 15,
        },
        {
            'lon': 37.695893 + (timestamp % 10) * 0.0001,
            'speed': 16.6,
            'timestamp': timestamp + 23,
            'lat': 55.719651,
        },
        {
            'speed': 16.6,
            'lon': 37.694498 + (timestamp % 10) * 0.0001,
            'timestamp': timestamp + 28,
            'lat': 55.71923,
        },
        {
            'lat': 55.718765,
            'timestamp': timestamp + 31,
            'speed': 16.6,
            'lon': 37.694135 + (timestamp % 10) * 0.0001,
        },
        {
            'speed': 16.6,
            'lon': 37.694035 + (timestamp % 10) * 0.0001,
            'lat': 55.718316,
            'timestamp': timestamp + 34,
        },
        {
            'speed': 16.6,
            'lon': 37.692801 + (timestamp % 10) * 0.0001,
            'timestamp': timestamp + 39,
            'lat': 55.717985,
        },
        {
            'speed': 16.6,
            'lon': 37.690895 + (timestamp % 10) * 0.0001,
            'lat': 55.71754,
            'timestamp': timestamp + 46,
        },
    ]
    return [(x['timestamp'], [x['lon'], x['lat']]) for x in track]


def _make_universal_message_from_track(track):
    yaga_next_driver_id = NextDriverId()
    driver_id = 'dbid_uuid{}'.format(yaga_next_driver_id.get_next_id())
    message = {'payload': []}
    message['payload'] = [
        {
            'contractor_id': driver_id,
            'client_timestamp': timestamp,
            'source': 'Verified',
            'signals': [
                {
                    'geo_position': {'position': position},
                    'position_on_edge': {
                        'persistent_edge_id': 123123124,
                        'edge_displacement': 0.5,
                    },
                },
            ],
        }
        for timestamp, position in track
    ]
    return message


async def _check_service_is_alive(taxi_yaga_metrics):
    response = await taxi_yaga_metrics.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''


def _subscribe(listener, channel, try_count=30):
    for _ in range(try_count):
        listener.subscribe(channel)
        message = listener.get_message(timeout=0.2)
        if message is not None and message['type'] == 'subscribe':
            return
    # failed to subscribe
    assert False


def _read_all(listener):
    # Get all messages from channel
    for _ in range(3):
        while listener.get_message(timeout=0.2) is not None:
            print('**********')
