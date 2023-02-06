# pylint: disable=import-error,too-many-lines

import datetime

import pytest

from geobus_tools import (
    geobus,
)  # noqa: F401 C5521 from tests_plugins import utils


YAGR_OUTPUT_CAMERA_CHANNEL = 'channel:camera:raw_positions'


def check_polling_header(header):
    parts = header.split(', ')
    parts.sort()
    assert parts == [
        'background=1200s',
        'full=600s',
        'idle=1800s',
        'powersaving=1200s',
    ]


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_camera_position_store_basic_check(
        taxi_yagr_adv, redis_store, testpoint, user_agent, app_family,
):
    camera_listener = redis_store.pubsub()
    _subscribe(camera_listener, YAGR_OUTPUT_CAMERA_CHANNEL)
    _read_all(camera_listener)

    park_id = 'bertycamera'
    driver_id = 'qwerty1'
    data_args = {'positions': []}

    unix_ts = datetime.datetime(2019, 9, 11, 13, 42, 15).timestamp() * 1000
    # 1st pos
    first_position = {
        'lon': 30.20,
        'lat': 57.40,
        'contractor_uuid': driver_id,
        'contractor_dbid': park_id,
        'source': 'Camera',
        'direction': 23,
        'speed': 10.0,
        'accuracy': 5,
        'altitude': 9,
        'unix_timestamp': unix_ts,
    }
    data_args['positions'].append(first_position)

    # 2nd pos
    second_position = {
        'lon': 31.0,
        'lat': 58.0,
        'contractor_uuid': driver_id,
        'contractor_dbid': park_id,
        'source': 'Camera',
        'direction': 25,
        'speed': 11.0,
        'accuracy': 3,
        'altitude': 15,
        'unix_timestamp': unix_ts,
    }
    data_args['positions'].append(second_position)

    # 3rd pos
    third_position = {
        'lon': 29.0,
        'lat': 59.0,
        'contractor_uuid': driver_id,
        'contractor_dbid': park_id,
        'source': 'Camera',
        'direction': 20,
        'speed': 20.0,
        'accuracy': 1,
        'altitude': 20,
        'unix_timestamp': unix_ts,
    }
    data_args['positions'].append(third_position)

    headers = {
        'User-Agent': user_agent,
        'Accept-Language': 'ru',
        'X-Request-Application-Version': '9.1',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': driver_id,
    }
    response = await taxi_yagr_adv.post(
        '/camera/position/v2/store', json=data_args, headers=headers,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    # check after all processing is done
    redis_message = _get_message(camera_listener, redis_store)
    assert redis_message is not None
    print(redis_message['data'])
    deserialized = geobus.deserialize_positions_v2(redis_message['data'])
    deserialized = deserialized['positions']
    assert len(deserialized) == 3
    pos = deserialized[0]
    assert pos['driver_id'] == park_id + '_' + driver_id
    assert pos['position'] == [first_position['lon'], first_position['lat']]
    assert pos['speed'] == first_position['speed']
    assert pos['direction'] == first_position['direction']
    assert pos['accuracy'] == first_position['accuracy']
    assert pos['unix_timestamp'] == unix_ts

    pos = deserialized[1]
    assert pos['driver_id'] == park_id + '_' + driver_id
    assert pos['position'] == [second_position['lon'], second_position['lat']]
    assert pos['speed'] == second_position['speed']
    assert pos['direction'] == second_position['direction']
    assert pos['accuracy'] == second_position['accuracy']
    assert pos['unix_timestamp'] == unix_ts

    pos = deserialized[2]
    assert pos['driver_id'] == park_id + '_' + driver_id
    assert pos['position'] == [third_position['lon'], third_position['lat']]
    assert pos['speed'] == third_position['speed']
    assert pos['direction'] == third_position['direction']
    assert pos['accuracy'] == third_position['accuracy']
    assert pos['unix_timestamp'] == unix_ts


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_camera_position_to_yt_log(
        taxi_yagr_adv, redis_store, testpoint, user_agent, app_family,
):
    @testpoint('write-camera-position-to-yt')
    def testpoint_camera_to_yt(data):
        pass

    park_id = 'berty'
    driver_id = 'qwerty_for_multipos'
    data_args = {'positions': []}

    unix_ts = datetime.datetime(2019, 9, 11, 13, 42, 15).timestamp() * 1000
    # 1st pos
    first_position = {
        'lon': 30.20,
        'lat': 57.40,
        'contractor_uuid': driver_id + '1',
        'contractor_dbid': park_id + '1',
        'source': 'Camera',
        'direction': 23,
        'speed': 10.0,
        'accuracy': 5,
        'altitude': 9,
        'unix_timestamp': unix_ts,
    }
    data_args['positions'].append(first_position)

    # 2nd pos
    second_position = {
        'lon': 31.0,
        'lat': 58.0,
        'contractor_uuid': driver_id + '2',
        'contractor_dbid': park_id + '2',
        'source': 'Camera',
        'direction': 25,
        'speed': 11.0,
        'accuracy': 3,
        'altitude': 15,
        'unix_timestamp': unix_ts,
    }
    data_args['positions'].append(second_position)

    # 3rd pos
    third_position = {
        'lon': 29.0,
        'lat': 59.0,
        'contractor_uuid': driver_id + '3',
        'contractor_dbid': park_id + '3',
        'source': 'Camera',
        'unix_timestamp': unix_ts,
    }
    data_args['positions'].append(third_position)

    headers = {
        'User-Agent': user_agent,
        'Accept-Language': 'ru',
        'X-Request-Application-Version': '9.1',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': driver_id,
    }
    response = await taxi_yagr_adv.post(
        '/camera/position/v2/store', json=data_args, headers=headers,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    data = await testpoint_camera_to_yt.wait_call()
    json = data['data']['json']
    assert json['source'] == 'Camera'
    eql_keys = [
        'contractor_uuid',
        'contractor_dbid',
        'lat',
        'lon',
        'unix_timestamp',
        'altitude',
        'direction',
        'speed',
        'accuracy',
    ]
    for k in eql_keys:
        assert json[k] == first_position[k]

    data = await testpoint_camera_to_yt.wait_call()
    json = data['data']['json']
    assert json['source'] == 'Camera'
    eql_keys = [
        'contractor_uuid',
        'contractor_dbid',
        'lat',
        'lon',
        'unix_timestamp',
        'altitude',
        'direction',
        'speed',
        'accuracy',
    ]
    for k in eql_keys:
        assert json[k] == second_position[k]

    data = await testpoint_camera_to_yt.wait_call()
    json = data['data']['json']
    assert json['source'] == 'Camera'
    eql_keys = [
        'contractor_uuid',
        'contractor_dbid',
        'lat',
        'lon',
        'unix_timestamp',
    ]
    for k in eql_keys:
        assert json[k] == third_position[k]
    missing_fields = ['altitude', 'direction', 'speed', 'accuracy']
    for k in missing_fields:
        assert k not in json


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_camera_position_store_empty(
        taxi_yagr_adv, redis_store, testpoint, user_agent, app_family,
):
    camera_listener = redis_store.pubsub()
    _subscribe(camera_listener, YAGR_OUTPUT_CAMERA_CHANNEL)
    _read_all(camera_listener)

    park_id = 'berty5'
    driver_id = 'qwerty2'
    data_args = {'positions': []}

    unix_ts = datetime.datetime(2019, 9, 11, 13, 42, 15).timestamp() * 1000
    # 1st pos
    first_position = {'unix_timestamp': unix_ts}
    data_args['positions'].append(first_position)

    headers = {
        'User-Agent': user_agent,
        'Accept-Language': 'ru',
        'X-Request-Application-Version': '9.1',
        'X-YaTaxi-Park-Id': park_id,
        'X-YaTaxi-Driver-Profile-Id': driver_id,
    }
    response = await taxi_yagr_adv.post(
        '/camera/position/v2/store', json=data_args, headers=headers,
    )
    assert response.status_code == 400


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


def _read_all(listener):
    # Get all messages from channel
    for _ in range(3):
        while listener.get_message(timeout=0.2) is not None:
            print('**********')
