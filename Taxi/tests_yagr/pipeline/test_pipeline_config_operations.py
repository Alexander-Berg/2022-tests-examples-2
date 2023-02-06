# pylint: disable=import-error,too-many-lines

import datetime

import pytest

from geobus_tools import (
    geobus,
)  # noqa: F401 C5521 from tests_plugins import utils
from geobus_tools.channels import universal_signals


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


YAGR_TEST_V2_CHANNEL = 'channel:test:positions'
YAGR_TEST_V2_UNIVERSAL_CHANNEL = 'channel:test:positions_universal'
YAGR_TEST_SIGNAL_V2_CHANNEL = 'channel:test:signal_v2'
YAGR_TEST_DATA_STREAM = 'test$pp-test-data-stream$@0'


@pytest.mark.now('2019-09-11T13:42:15+0300')
async def test_pipline_basic_check(taxi_yagr_adv, redis_store):
    await taxi_yagr_adv.update_service_config('pipeline_config_base.json')

    signal_v2_listener = redis_store.pubsub()
    _subscribe(signal_v2_listener, YAGR_TEST_SIGNAL_V2_CHANNEL)
    _read_all(signal_v2_listener)

    positions_listener = redis_store.pubsub()
    _subscribe(positions_listener, YAGR_TEST_V2_CHANNEL)
    _read_all(positions_listener)

    positions_universal_listener = redis_store.pubsub()
    _subscribe(positions_universal_listener, YAGR_TEST_V2_UNIVERSAL_CHANNEL)
    _read_all(positions_universal_listener)

    data_stream_listener = redis_store.pubsub()
    _subscribe(data_stream_listener, YAGR_TEST_DATA_STREAM)
    _read_all(data_stream_listener)

    park_id = 'sberty'
    driver_id = 'sqwerty1'
    params = {'pipeline': 'test', 'uuid': f'{park_id}_{driver_id}'}
    data_args = {'positions': []}

    unix_ts = 1568198535000

    # 1st pos
    first_position = {
        'geodata': {
            'lat': 57.40,
            'lon': 30.20,
            'direction': 23,
            'speed': 10.0,
            'accuracy': 5,
            'altitude': 9,
        },
        'source': 'Verified',
        'timestamp': unix_ts,
        'sensors': dict(),
    }
    data_args['positions'].append(first_position)

    # 2nd pos
    second_position = {
        'geodata': {
            'lat': 58.0,
            'lon': 31.0,
            'direction': 25,
            'speed': 11.0,
            'accuracy': 3,
            'altitude': 15,
        },
        'source': 'AndroidNetwork',
        'timestamp': unix_ts,
        'sensors': dict(),
    }
    data_args['positions'].append(second_position)

    # 3rd pos
    third_position = {
        'geodata': {
            'lat': 58.0,
            'lon': 29.0,
            'direction': 20,
            'speed': 20.0,
            'accuracy': 1,
            'altitude': 20,
        },
        'source': 'YandexLbsIp',
        'timestamp': unix_ts,
        'sensors': dict(),
    }
    data_args['positions'].append(third_position)

    headers = {'Accept-Language': 'ru', 'X-YaFts-Client-Service-Tvm': '123'}
    response = await taxi_yagr_adv.post(
        '/v2/position/store', json=data_args, headers=headers, params=params,
    )
    assert response.status_code == 200

    # check after all processing is done
    redis_message = _get_message(signal_v2_listener, redis_store)
    assert redis_message is not None
    deserialized = geobus.deserialize_signal_v2_message(redis_message['data'])
    assert len(deserialized) == 3

    pos = deserialized[0]
    assert pos['driver_id'] == park_id + '_' + driver_id
    assert pos['position'][0] == first_position['geodata']['lon']
    assert pos['position'][1] == first_position['geodata']['lat']
    source_verified_in_enum = 10
    assert pos['source'] == source_verified_in_enum
    assert pos['speed'] == first_position['geodata']['speed']
    assert pos['direction'] == first_position['geodata']['direction']
    assert pos['accuracy'] == first_position['geodata']['accuracy']
    assert pos['altitude'] == first_position['geodata']['altitude']
    assert pos['unix_time'] == unix_ts

    pos = deserialized[1]
    assert pos['driver_id'] == park_id + '_' + driver_id
    assert pos['position'][0] == second_position['geodata']['lon']
    assert pos['position'][1] == second_position['geodata']['lat']
    source_android_network_in_enum = 1
    assert pos['source'] == source_android_network_in_enum
    assert pos['speed'] == second_position['geodata']['speed']
    assert pos['direction'] == second_position['geodata']['direction']
    assert pos['accuracy'] == second_position['geodata']['accuracy']
    assert pos['altitude'] == second_position['geodata']['altitude']
    assert pos['unix_time'] == unix_ts

    pos = deserialized[2]
    assert pos['driver_id'] == park_id + '_' + driver_id
    assert pos['position'][0] == third_position['geodata']['lon']
    assert pos['position'][1] == third_position['geodata']['lat']
    source_yandex_lbs_ip_in_enum = 6
    assert pos['source'] == source_yandex_lbs_ip_in_enum
    assert pos['speed'] == third_position['geodata']['speed']
    assert pos['direction'] == third_position['geodata']['direction']
    assert pos['accuracy'] == third_position['geodata']['accuracy']
    assert pos['altitude'] == third_position['geodata']['altitude']
    assert pos['unix_time'] == unix_ts

    # check that verified position was sent in old channel
    redis_message = _get_message(positions_listener, redis_store)
    assert redis_message is not None
    deserialized = geobus.deserialize_positions_v2(redis_message['data'])[
        'positions'
    ]
    assert len(deserialized) == 1
    print(deserialized)
    pos = deserialized[0]
    print(pos)
    assert pos == {
        'position': [
            first_position['geodata']['lon'],
            first_position['geodata']['lat'],
        ],
        'direction': first_position['geodata']['direction'],
        'unix_timestamp': unix_ts,
        'rtc_timestamp': 0,
        'speed': first_position['geodata']['speed'],
        'accuracy': first_position['geodata']['accuracy'],
        'source': 0,
        'timestamp': 1568198535,
        'driver_id': park_id + '_' + driver_id,
    }

    # check that verified position was sent in universal channel
    redis_message = _get_message(positions_universal_listener, redis_store)
    assert redis_message is not None
    deserialized = universal_signals.deserialize_message(redis_message['data'])
    signals = deserialized['payload']
    assert len(signals) == 1
    signal = signals[0]
    assert signal == {
        'client_timestamp': unix_ts * 1000,
        'contractor_id': park_id + '_' + driver_id,
        'source': first_position['source'],
        'signals': [
            {
                'geo_position': {
                    'accuracy': first_position['geodata']['accuracy'],
                    'altitude': first_position['geodata']['altitude'],
                    'direction': first_position['geodata']['direction'],
                    'position': [
                        first_position['geodata']['lon'],
                        first_position['geodata']['lat'],
                    ],
                    'speed': first_position['geodata']['speed'],
                },
                'log_likelihood': 0.0,
                'prediction_shift': 0,
                'probability': 1.0,
            },
        ],
    }

    # check that all positions was sent to data stream
    redis_message = _get_message(data_stream_listener, redis_store)
    assert redis_message is not None
    deserialized = universal_signals.deserialize_message(redis_message['data'])
    signals = deserialized['payload']
    assert len(signals) == 3


@pytest.mark.now('2019-09-11T13:42:15+0300')
async def test_add_new_pipeline(taxi_yagr_adv, redis_store):
    signal_v2_listener = redis_store.pubsub()
    _subscribe(signal_v2_listener, YAGR_TEST_SIGNAL_V2_CHANNEL)
    _read_all(signal_v2_listener)

    positions_listener = redis_store.pubsub()
    _subscribe(positions_listener, YAGR_TEST_V2_CHANNEL)
    _read_all(positions_listener)

    park_id = 'sberty'
    driver_id = 'sqwerty1'
    params = {'pipeline': 'test', 'uuid': f'{park_id}_{driver_id}'}
    data_args = {'positions': []}

    unix_ts = datetime.datetime(2019, 9, 11, 13, 42, 15).timestamp() * 1000
    # 1st pos
    first_position = {
        'geodata': {
            'lat': 57.40,
            'lon': 30.20,
            'direction': 23,
            'speed': 10.0,
            'accuracy': 5,
            'altitude': 9,
        },
        'source': 'Verified',
        'timestamp': unix_ts,
        'sensors': dict(),
    }
    data_args['positions'].append(first_position)

    response = await taxi_yagr_adv.post(
        '/v2/position/store',
        json=data_args,
        params=params,
        headers={'X-YaFts-Client-Service-Tvm': '123'},
    )
    assert response.status_code == 404
    await taxi_yagr_adv.update_service_config('pipeline_config_base.json')

    response = await taxi_yagr_adv.post(
        '/v2/position/store',
        json=data_args,
        params=params,
        headers={'X-YaFts-Client-Service-Tvm': '123'},
    )
    assert response.status_code == 200
    redis_message = _get_message(signal_v2_listener, redis_store)
    assert redis_message is not None
    deserialized = geobus.deserialize_signal_v2_message(redis_message['data'])
    assert len(deserialized) == 1


@pytest.mark.now('2019-09-11T13:42:15+0300')
async def test_delete_pipeline(taxi_yagr_adv, redis_store):
    signal_v2_listener = redis_store.pubsub()
    _subscribe(signal_v2_listener, YAGR_TEST_SIGNAL_V2_CHANNEL)
    _read_all(signal_v2_listener)

    positions_listener = redis_store.pubsub()
    _subscribe(positions_listener, YAGR_TEST_V2_CHANNEL)
    _read_all(positions_listener)

    park_id = 'sberty'
    driver_id = 'sqwerty1'
    params = {'pipeline': 'test', 'uuid': f'{park_id}_{driver_id}'}
    data_args = {
        'positions': [],
        'contractor_id': {'dbid': park_id, 'uuid': driver_id},
    }

    unix_ts = datetime.datetime(2019, 9, 11, 13, 42, 15).timestamp() * 1000
    # 1st pos
    first_position = {
        'geodata': {
            'lat': 57.40,
            'lon': 30.20,
            'direction': 23,
            'speed': 10.0,
            'accuracy': 5,
            'altitude': 9,
        },
        'source': 'Verified',
        'timestamp': unix_ts,
        'sensors': dict(),
    }
    data_args['positions'].append(first_position)
    headers = {'Accept-Language': 'ru', 'X-YaFts-Client-Service-Tvm': '123'}

    await taxi_yagr_adv.update_service_config('pipeline_config_base.json')

    response = await taxi_yagr_adv.post(
        '/v2/position/store', json=data_args, headers=headers, params=params,
    )
    assert response.status_code == 200
    redis_message = _get_message(signal_v2_listener, redis_store)
    assert redis_message is not None
    deserialized = geobus.deserialize_signal_v2_message(redis_message['data'])
    assert len(deserialized) == 1

    await taxi_yagr_adv.update_service_config_by_value({})

    response = await taxi_yagr_adv.post(
        '/v2/position/store', json=data_args, headers=headers, params=params,
    )
    assert response.status_code == 404
