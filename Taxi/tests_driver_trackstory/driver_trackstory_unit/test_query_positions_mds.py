# pylint: disable=import-error
# pylint: disable=unused-variable

import datetime
import time

from geobus_tools import geobus  # noqa: F401 C5521
import pytest

from tests_plugins import utils

POSITIONS_CHANNEL = 'channel:yagr:position'


def _get_channel_message(driver_id, now):
    timestamp = int(utils.timestamp(now))
    drivers = [
        {
            'driver_id': driver_id,
            'position': [55, 37],
            'direction': 45,
            'timestamp': timestamp,
            'speed': 11.666666666666668,
            'accuracy': 3,
            'source': 'Gps',
        },
    ]
    return geobus.serialize_positions_v2(drivers, now)


async def _wait_message_received(
        taxi_driver_trackstory_adv,
        redis_store,
        retry_channel=None,
        max_tries=30,
        retry_message=None,
):
    # wait while track-geobus-saver component receives message
    for _ in range(max_tries):
        keys = redis_store.keys()
        print(keys)
        if len(keys) > 1:
            return
        if retry_channel is not None and retry_message is not None:
            await taxi_driver_trackstory_adv.sync_send_to_channel(
                retry_channel, retry_message, 2,
            )
        time.sleep(0.2)

    # if failed to receive message
    assert False


# ok with AsOfNow algorithm
@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': False,
            'storage': {'max_age_seconds': 10, 'max_points_count': 10},
        },
        'unverified': {
            'enabled': False,
            'storage': {'max_age_seconds': 100, 'max_points_count': 10},
        },
    },
)
async def test_points_from_mds_success(
        taxi_driver_trackstory_adv, redis_store, now, mockserver, testpoint,
):
    @testpoint('testpoint_GetPositionFromRedis')
    def testpoint_positions_from_redis(data):
        pass

    dbid = 'dbid'
    uuid = 'uuid_7'
    driver_id = dbid + '_' + uuid

    pos_tp = now - datetime.timedelta(minutes=1)
    message = _get_channel_message(driver_id, pos_tp)
    await taxi_driver_trackstory_adv.sync_send_to_channel(
        POSITIONS_CHANNEL, message,
    )
    await _wait_message_received(
        taxi_driver_trackstory_adv,
        redis_store,
        retry_channel=POSITIONS_CHANNEL,
        retry_message=message,
    )

    response = await taxi_driver_trackstory_adv.post(
        'query/positions',
        json={
            'driver_ids': [driver_id],
            'max_age': 99,
            'prefered_sources': 'all',
            'parameterized_algorithm': {'algorithm': 'AsOfNow'},
        },
    )

    assert response.status_code == 200

    assert testpoint_positions_from_redis.times_called == 1
    assert len(response.json()['results'][0]) == 1
    assert response.json()['results'][0] == [
        {
            'position': {
                'accuracy': 3.0,
                'direction': 45,
                'lat': 37.0,
                'lon': 55.0,
                'speed': 11.6,
                'timestamp': 1568198475,
            },
            'source': 'Raw',
            'source2': 'RawPositions',
        },
    ]


#  ok with WithRetry algorithm
@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': False,
            'storage': {'max_age_seconds': 10, 'max_points_count': 10},
        },
        'unverified': {
            'enabled': False,
            'storage': {'max_age_seconds': 1, 'max_points_count': 1},
        },
    },
)
async def test_points_from_mds_with_retries_success(
        taxi_driver_trackstory_adv, redis_store, now, mockserver, testpoint,
):
    @testpoint('testpoint_GetPositionFromRedis')
    def testpoint_positions_from_redis(data):
        pass

    dbid = 'dbid'
    uuid = 'uuid_7'
    driver_id = dbid + '_' + uuid
    pos_tp = now - datetime.timedelta(minutes=1)

    @testpoint('add_points')
    async def add_point(data):
        message = _get_channel_message(driver_id, pos_tp)
        await taxi_driver_trackstory_adv.sync_send_to_channel(
            POSITIONS_CHANNEL, message,
        )
        await _wait_message_received(
            taxi_driver_trackstory_adv,
            redis_store,
            retry_channel=POSITIONS_CHANNEL,
            retry_message=message,
        )

    response = await taxi_driver_trackstory_adv.post(
        'query/positions',
        json={
            'driver_ids': [driver_id],
            'max_age': 100,
            'prefered_sources': 'all',
            'parameterized_algorithm': {
                'algorithm': 'WithRetry',
                'timeout': 30,
                'max_retries': 3,
            },
        },
    )
    assert testpoint_positions_from_redis.times_called == 1
    assert len(response.json()['results'][0]) == 1
    assert response.json()['results'][0] == [
        {
            'position': {
                'accuracy': 3.0,
                'direction': 45,
                'lat': 37.0,
                'lon': 55.0,
                'speed': 11.6,
                'timestamp': 1568198475,
            },
            'source': 'Raw',
            'source2': 'RawPositions',
        },
    ]


# checks handle doesn't call mds method cause max_age is
# lower than cache max age storing time
@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(TRACKSTORY_REDIS_PROCESS_DRIVERS_PERCENT=100)
@pytest.mark.config(
    DRIVER_TRACKSTORY_REDIS_STORAGE_CONFIG={
        'enable_storing_raw': True,
        'enable_storing_adjusted': True,
    },
)
@pytest.mark.config(
    TRACKSTORY_SHORTTRACKS_SETTINGS={
        'raw_and_adjusted': {
            'enabled': True,
            'storage': {'max_age_seconds': 150, 'max_points_count': 60},
        },
        'unverified': {
            'enabled': False,
            'storage': {'max_age_seconds': 150, 'max_points_count': 30},
        },
    },
)
async def test_not_go_to_mds_cause_small_time(
        taxi_driver_trackstory_adv, redis_store, now, mockserver, testpoint,
):
    @testpoint('testpoit_GetPositionFromRedis')
    def testpoint_positions_from_redis(data):
        pass

    dbid = 'dbid'
    uuid = 'uuid_7'
    driver_id = dbid + '_' + uuid

    await taxi_driver_trackstory_adv.post(
        'query/positions',
        json={
            'driver_ids': [driver_id],
            'max_age': 100,
            'prefered_sources': 'all',
            'parameterized_algorithm': {'algorithm': 'AsOfNow'},
        },
    )

    assert testpoint_positions_from_redis.times_called == 0
