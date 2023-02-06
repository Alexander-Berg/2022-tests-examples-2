# pylint: disable=import-error

from geobus_tools.channels import universal_signals
import pytest

from tests_plugins import utils


INPUT_UNIVERSAL_CHANNEL = 'test$test-adjusted-1$@0'


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(YAGA_METROLOG_LOG_DRIVERS_PERCENTAGE=100)
@pytest.mark.config(GEOBUS_SUBSCRIPTION_MAX_PARTITIONS_COUNT=2)
async def test_yt_write_check(
        taxi_yaga_metrolog_adv, redis_store, testpoint, now,
):
    @testpoint('write-position-to-yt-pipeline-:test')
    def on_position_written_yt(data):
        pass

    @testpoint('write-position-to-additional-yt-pipeline-:test__taxi')
    def on_position_written_add_yt(data):
        pass

    await taxi_yaga_metrolog_adv.update_service_config('pipeline_config4.json')

    universal_listener = redis_store.pubsub()
    _subscribe(universal_listener, INPUT_UNIVERSAL_CHANNEL)
    _read_all(universal_listener)

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
    redis_store.publish(INPUT_UNIVERSAL_CHANNEL, message)

    await on_position_written_yt.wait_call()
    await on_position_written_add_yt.wait_call()


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
