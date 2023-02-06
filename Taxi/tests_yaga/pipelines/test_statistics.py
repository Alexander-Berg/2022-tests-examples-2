# pylint: disable=import-error
import asyncio
import sys
import json

from geobus_tools import geobus  # noqa: F401 C5521
from geobus_tools.channels import universal_signals
import pytest

YAGA_TEST_INPUT_CHANNEL = 'test$pp-test-positions$@0'
YAGA_TEST_INPUT_CHANNEL_PARTITIONED = 'test$pp-test-positions$@1'
YAGA_TEST_OUTPUT_CHANNEL = 'channel:test:adjusted'
YAGA_TEST_OUTPUT_CHANNEL_UNIVERSAL = 'channel:test:universal'
YAGA_TEST_OUTPUT_CHANNEL_PREDICTED = 'channel:test:predicted'


class PipelineYagaNextDriverId:
    yaga_next_driver_id = 10

    @staticmethod
    def get_next_id():
        PipelineYagaNextDriverId.yaga_next_driver_id += 1
        return PipelineYagaNextDriverId.yaga_next_driver_id - 1


@pytest.mark.asyncio
@pytest.mark.xfail
async def tests_statistics_no_partitions(
        taxi_yaga_adv, redis_store, now, taxi_yaga_monitor,
):
    await taxi_yaga_adv.update_service_config('pipeline_config_base.json')

    unique_timestamp_test = 1514764810
    track_test = _make_track(unique_timestamp_test)
    universal_message = _make_universal_message_from_track(track_test)

    input_universal_message = universal_signals.serialize_message(
        universal_message, now,
    )
    redis_store.publish(YAGA_TEST_INPUT_CHANNEL, input_universal_message)

    stats = await taxi_yaga_monitor.get_metric('geobus-listeners')
    print(json.dumps(stats, indent=4, sort_keys=True), file=sys.stderr)
    geobus_stats = stats['collections']['test']['geobus'][
        YAGA_TEST_INPUT_CHANNEL[:-2]
    ]['listener']
    assert geobus_stats == {
        'by-partitions': {
            '$meta': {'solomon_children_labels': 'partition'},
            '0': {
                'channel-msg-errors': 0,
                'elements-count': 10,
                'invalid-reaons': {
                    '$meta': {'solomon_children_labels': 'invalid-reason'},
                    'gps-signal-parse-fail': 0,
                    'invalid-driver': 0,
                    'invalid-source': 0,
                    'no-universal-signals': 0,
                    'universal-signal-parse-fail': 0,
                    'unknown-error': 0,
                },
                'nonsensical-payload-msg': 0,
                'user-callback-errors': 0,
                'valid-elements-count': 10,
            },
        },
        'channel-msg-errors': 0,
        'elements-count': 10,
        'invalid-reaons': {
            '$meta': {'solomon_children_labels': 'invalid-reason'},
            'gps-signal-parse-fail': 0,
            'invalid-driver': 0,
            'invalid-source': 0,
            'no-universal-signals': 0,
            'universal-signal-parse-fail': 0,
            'unknown-error': 0,
        },
        'nonsensical-payload-msg': 0,
        'user-callback-errors': 0,
        'valid-elements-count': 10,
    }


@pytest.mark.asyncio
@pytest.mark.xfail
async def tests_statistics_partitions(
        taxi_yaga_adv, redis_store, now, taxi_yaga_monitor,
):
    await taxi_yaga_adv.update_service_config(
        'pipeline_config_base_with_partitions.json',
    )
    edge_positions_listener_test = redis_store.pubsub()
    _subscribe(edge_positions_listener_test, YAGA_TEST_OUTPUT_CHANNEL)
    await _read_all(edge_positions_listener_test)

    universal_signals_listener_test = redis_store.pubsub()
    _subscribe(
        universal_signals_listener_test, YAGA_TEST_OUTPUT_CHANNEL_UNIVERSAL,
    )

    predicted_listener_test = redis_store.pubsub()
    _subscribe(predicted_listener_test, YAGA_TEST_OUTPUT_CHANNEL_PREDICTED)
    await _read_all(predicted_listener_test)

    unique_timestamp_test = 1514764810
    track_test = _make_track(unique_timestamp_test)
    universal_message = _make_universal_message_from_track(track_test)

    input_universal_message = universal_signals.serialize_message(
        universal_message, now,
    )
    redis_store.publish(YAGA_TEST_INPUT_CHANNEL, input_universal_message)
    redis_store.publish(
        YAGA_TEST_INPUT_CHANNEL_PARTITIONED, input_universal_message,
    )
    # test edge positions channel
    message_test = _get_message(
        edge_positions_listener_test,
        redis_store,
        retry_channel=YAGA_TEST_INPUT_CHANNEL,
        retry_message=input_universal_message,
    )
    # Failed to get message in max_tries tries
    assert message_test is not None
    assert message_test['data']

    # test universal signals channel
    message_test_universal = _get_message(
        universal_signals_listener_test,
        redis_store,
        retry_channel=YAGA_TEST_INPUT_CHANNEL,
        retry_message=input_universal_message,
    )

    # Failed to get message in max_tries tries
    assert message_test_universal is not None
    assert message_test_universal['data']

    # test predicted positions channel
    message_test_predicted = _get_message(
        predicted_listener_test,
        redis_store,
        retry_channel=YAGA_TEST_INPUT_CHANNEL,
        retry_message=input_universal_message,
    )

    # Failed to get message in max_tries tries
    assert message_test_predicted is not None
    assert message_test_predicted['data']

    await _check_service_is_alive(taxi_yaga_adv)

    stats = await taxi_yaga_monitor.get_metric('geobus-listeners')
    print('tests_statistics_partitions all stats:', stats)
    geobus_stats = stats['collections']['test']['geobus'][
        YAGA_TEST_INPUT_CHANNEL
    ]['listener']
    print('tests_statistics_partitions geobus stats:', geobus_stats)
    assert geobus_stats == {
        'by-partitions': {
            '$meta': {'solomon_children_labels': 'partition'},
            'partition:0': {
                'channel-msg-errors': 0,
                'elements-count': 0,
                'invalid-reaons': {
                    '$meta': {'solomon_children_labels': 'invalid-reason'},
                    'invalid-driver': 0,
                    'invalid-position': 0,
                },
                'nonsensical-payload-msg': 0,
                'user-callback-errors': 0,
                'valid-elements-count': 0,
            },
            'partition:1': {
                'channel-msg-errors': 0,
                'elements-count': 10,
                'invalid-reaons': {
                    '$meta': {'solomon_children_labels': 'invalid-reason'},
                    'invalid-driver': 0,
                    'invalid-position': 0,
                },
                'nonsensical-payload-msg': 0,
                'user-callback-errors': 0,
                'valid-elements-count': 10,
            },
            'partition:2': {
                'channel-msg-errors': 0,
                'elements-count': 0,
                'invalid-reaons': {
                    '$meta': {'solomon_children_labels': 'invalid-reason'},
                    'invalid-driver': 0,
                    'invalid-position': 0,
                },
                'nonsensical-payload-msg': 0,
                'user-callback-errors': 0,
                'valid-elements-count': 0,
            },
        },
        'channel-msg-errors': 0,
        'elements-count': 0,
        'invalid-reaons': {
            '$meta': {'solomon_children_labels': 'invalid-reason'},
            'invalid-driver': 0,
            'invalid-position': 0,
        },
        'nonsensical-payload-msg': 0,
        'user-callback-errors': 0,
        'valid-elements-count': 0,
    }


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


def _make_message_from_track(track):
    print(track)
    yaga_next_driver_id = PipelineYagaNextDriverId()
    driver_id = 'dbid_uuid{}'.format(yaga_next_driver_id.get_next_id())
    return [
        {
            'driver_id': driver_id,
            'direction': 0,
            'speed': int(16.6 * 3.6),
            'accuracy': 0,
            'timestamp': timestamp,
            'position': position,
            'source': 'Gps',
        }
        for timestamp, position in track
    ]


def _make_universal_message_from_track(track):
    yaga_next_driver_id = PipelineYagaNextDriverId()
    driver_id = 'dbid_uuid{}'.format(yaga_next_driver_id.get_next_id())
    message = {'payload': []}
    message['payload'] = [
        {
            'contractor_id': driver_id,
            'client_timestamp': timestamp,
            'source': 'Verified',
            'signals': [{'geo_position': {'position': position}}],
        }
        for timestamp, position in track
    ]
    return message


def _subscribe(listener, channel, try_count=30):
    for _ in range(try_count):
        listener.subscribe(channel)
        message = listener.get_message(timeout=0.2)
        if message is not None and message['type'] == 'subscribe':
            return
    # failed to subscribe
    assert False


def _get_message(
        listener,
        redis_store,
        retry_channel=None,
        max_tries=30,
        retry_message=None,
):
    # wait while yaga-dispatcher pass messages to output channel
    for _ in range(max_tries):
        message = listener.get_message(timeout=0.2)
        if message is not None and message['type'] == 'message':
            return message
        if retry_channel is not None and retry_message is not None:
            redis_store.publish(retry_channel, retry_message)
    return None


async def _read_all(listener):
    # Get all messages from channel
    for _ in range(3):
        while listener.get_message() is not None:
            print('**********')
        await asyncio.sleep(0.1)


async def _check_service_is_alive(taxi_yaga_adv):
    response = await taxi_yaga_adv.get('ping')
    # Status code must be checked for every request
    assert response.status_code == 200
    # Response content (even empty) must be checked for every request
    assert response.content == b''
