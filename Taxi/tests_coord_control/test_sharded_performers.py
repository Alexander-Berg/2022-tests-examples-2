# pylint: disable=import-error

import datetime
import socket

import pytest

from geobus_tools import geobus  # noqa: F401 C5521

CONSISTENT_HASHING_NAME = 'consistent-hashing-finished'
REDIS_TABLE_NAME = 'consistent_hashing'
IS_RESPONSIBLE_FOR_KEY_NAME = 'is-responsible-for-key'
CHANNEL_NAME = 'channel:yagr:signal_v2'
SHARD_KEY = 'shard_key'
NOW = datetime.datetime(2020, 9, 9, 9, 0, 0)


def _timestring(time):
    return time.isoformat() + '+0000'


def _publish_message(redis_store, message):
    fbs_message = geobus.serialize_signal_v2(message, datetime.datetime.now())
    redis_store.publish(CHANNEL_NAME, fbs_message)


@pytest.mark.redis_store(
    ['hmset', REDIS_TABLE_NAME, {SHARD_KEY: _timestring(NOW)}],
)
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
async def test_remove_expired_keys(
        taxi_coord_control, redis_store, load_json, testpoint, mocked_time,
):
    @testpoint(CONSISTENT_HASHING_NAME)
    def consistent_hashing_finished(data):
        pass

    mocked_time.set(NOW + datetime.timedelta(seconds=10))

    await taxi_coord_control.invalidate_caches()
    await consistent_hashing_finished.wait_call()
    keys = redis_store.hkeys(REDIS_TABLE_NAME)
    assert len(keys) == 1
    assert keys[0].decode('utf-8') == socket.gethostname()


@pytest.mark.redis_store(
    [
        'hmset',
        'consistent_hashing',
        {SHARD_KEY: _timestring(NOW), socket.gethostname(): _timestring(NOW)},
    ],
)
@pytest.mark.geoareas(filename='geoareas.json', db_format=True)
@pytest.mark.tariffs(filename='tariffs.json')
@pytest.mark.experiments3(filename='experiments3.json')
async def test_sharded_performers(
        taxi_coord_control, redis_store, load_json, testpoint, mocked_time,
):
    @testpoint(CONSISTENT_HASHING_NAME)
    def consistent_hashing_finished(data):
        pass

    @testpoint(IS_RESPONSIBLE_FOR_KEY_NAME)
    def responsible_for_key(data):
        pass

    mocked_time.set(NOW)

    await taxi_coord_control.tests_control()
    await consistent_hashing_finished.wait_call()

    messages = load_json('geobus_messages.json')
    _publish_message(redis_store, messages)
    assert (await responsible_for_key.wait_call())['data']

    redis_store.hset(
        'consistent_hashing',
        SHARD_KEY,
        _timestring(NOW - datetime.timedelta(seconds=10)),
    )
    await consistent_hashing_finished.wait_call()
    _publish_message(redis_store, messages)

    assert (await responsible_for_key.wait_call())['data']
