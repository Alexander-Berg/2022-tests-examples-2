# pylint: disable=import-error

from geobus_tools.channels import universal_signals
import pytest

from tests_plugins import utils

INPUT_UNIVERSAL_CHANNEL_0 = 'test$test-adjusted-1$@0'
INPUT_UNIVERSAL_CHANNEL_1 = 'test$test-adjusted-1$@1'
INPUT_OTHER_UNIVERSAL_CHANNEL_0 = 'test$test-adjusted-2$@0'


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(YAGA_METROLOG_LOG_DRIVERS_PERCENTAGE=100)
@pytest.mark.config(GEOBUS_SUBSCRIPTION_MAX_PARTITIONS_COUNT=2)
async def test_statistics_by_partitions(
        taxi_yaga_metrolog_adv,
        taxi_yaga_metrolog_monitor,
        redis_store,
        testpoint,
        now,
):
    @testpoint('write-position-to-yt-pipeline-:test')
    def on_position_written_yt(data):
        pass

    @testpoint('write-position-to-additional-yt-pipeline-:test__taxi')
    def on_position_written_add_yt(data):
        pass

    @testpoint('finish-OnPositionsReceived')
    def finish_on_position_recieved(data):
        pass

    await taxi_yaga_metrolog_adv.update_service_config('pipeline_config4.json')

    timestamp = int(utils.timestamp(now))
    dbid_uuid = 'qwerty_asdfgh'
    position = [37.466104, 55.727191]
    message = universal_signals.serialize_message(
        {
            'payload': [
                {
                    'contractor_id': dbid_uuid,
                    'client_timestamp': timestamp,
                    'signals': [
                        {
                            'geo_position': {
                                'position': position,
                                'direction': 0,
                                'speed': 42.0,
                            },
                            'position_on_edge': {
                                'persistent_edge_id': 255,
                                'edge_displacement': 1.0,
                            },
                            'probability': 1.0,
                            'log_likelihood': -1.5,
                        },
                    ],
                },
            ],
        },
        now,
    )

    wrong_driver_message = universal_signals.serialize_message(
        {
            'payload': [
                {
                    'contractor_id': 'abc',
                    'client_timestamp': timestamp,
                    'signals': [
                        {
                            'geo_position': {
                                'position': position,
                                'direction': 0,
                                'speed': 42.0,
                            },
                            'position_on_edge': {
                                'persistent_edge_id': 255,
                                'edge_displacement': 1.0,
                            },
                            'probability': 1.0,
                            'log_likelihood': -1.5,
                        },
                    ],
                },
            ],
        },
        now,
    )

    redis_store.publish(INPUT_UNIVERSAL_CHANNEL_0, wrong_driver_message)

    redis_store.publish(INPUT_UNIVERSAL_CHANNEL_0, message)
    await on_position_written_yt.wait_call()
    await on_position_written_add_yt.wait_call()

    redis_store.publish(INPUT_UNIVERSAL_CHANNEL_1, message)
    await on_position_written_yt.wait_call()
    await on_position_written_add_yt.wait_call()

    redis_store.publish(INPUT_OTHER_UNIVERSAL_CHANNEL_0, message)
    await on_position_written_yt.wait_call()
    await on_position_written_add_yt.wait_call()

    await finish_on_position_recieved.wait_call()

    stats = await taxi_yaga_metrolog_monitor.get_metric('geobus-listeners')
    geobus_stats = stats['collections']['test']['geobus'][
        'test$test-adjusted-1$'
    ]['listener']
    assert geobus_stats == {
        'elements-count': 0,
        'valid-elements-count': 0,
        'nonsensical-payload-msg': 0,
        'invalid-reaons': {
            'invalid-driver': 0,
            'gps-signal-parse-fail': 0,
            'invalid-source': 0,
            'universal-signal-parse-fail': 0,
            'unknown-error': 0,
            'no-universal-signals': 0,
            '$meta': {'solomon_children_labels': 'invalid-reason'},
        },
        'channel-msg-errors': 0,
        'user-callback-errors': 0,
        'by-partitions': {
            '$meta': {'solomon_children_labels': 'partition'},
            '0': {
                'elements-count': 2,
                'valid-elements-count': 1,
                'nonsensical-payload-msg': 0,
                'invalid-reaons': {
                    'invalid-driver': 1,
                    'gps-signal-parse-fail': 0,
                    'invalid-source': 0,
                    'universal-signal-parse-fail': 0,
                    'unknown-error': 0,
                    'no-universal-signals': 0,
                    '$meta': {'solomon_children_labels': 'invalid-reason'},
                },
                'channel-msg-errors': 0,
                'user-callback-errors': 0,
            },
            '1': {
                'elements-count': 1,
                'valid-elements-count': 1,
                'nonsensical-payload-msg': 0,
                'invalid-reaons': {
                    'invalid-driver': 0,
                    'gps-signal-parse-fail': 0,
                    'invalid-source': 0,
                    'universal-signal-parse-fail': 0,
                    'unknown-error': 0,
                    'no-universal-signals': 0,
                    '$meta': {'solomon_children_labels': 'invalid-reason'},
                },
                'channel-msg-errors': 0,
                'user-callback-errors': 0,
            },
        },
    }

    geobus_stats = stats['collections']['test']['geobus'][
        'test$test-adjusted-2$'
    ]['listener']
    assert geobus_stats == {
        'elements-count': 0,
        'valid-elements-count': 0,
        'nonsensical-payload-msg': 0,
        'invalid-reaons': {
            'invalid-driver': 0,
            'gps-signal-parse-fail': 0,
            'invalid-source': 0,
            'universal-signal-parse-fail': 0,
            'unknown-error': 0,
            'no-universal-signals': 0,
            '$meta': {'solomon_children_labels': 'invalid-reason'},
        },
        'channel-msg-errors': 0,
        'user-callback-errors': 0,
        'by-partitions': {
            '$meta': {'solomon_children_labels': 'partition'},
            '0': {
                'elements-count': 1,
                'valid-elements-count': 1,
                'nonsensical-payload-msg': 0,
                'invalid-reaons': {
                    'invalid-driver': 0,
                    'gps-signal-parse-fail': 0,
                    'invalid-source': 0,
                    'universal-signal-parse-fail': 0,
                    'unknown-error': 0,
                    'no-universal-signals': 0,
                    '$meta': {'solomon_children_labels': 'invalid-reason'},
                },
                'channel-msg-errors': 0,
                'user-callback-errors': 0,
            },
        },
    }
