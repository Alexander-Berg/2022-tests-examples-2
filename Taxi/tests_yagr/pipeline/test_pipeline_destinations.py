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


YAGR_TEST_POSITIONS_CHANNEL = 'channel:test:positions'
YAGR_TEST_PEDESTRAIN_POSITIONS_CHANNEL = 'channel:test:pedestrian-positions'
YAGR_TEST_PREDICTION_CHANNEL = 'test$pp-test-prediction$@0'
YAGR_TEST_DISCARD_POSITIONS_CHANNEL = 'channel:test:discard-positions'


@pytest.mark.now('2019-09-11T13:42:15+0300')
async def test_pipline_pedestrian(
        taxi_yagr_adv, redis_store, contractor_transport_request,
):
    await taxi_yagr_adv.update_service_config(
        'pipeline_config_destinations.json',
    )

    positions_listener = redis_store.pubsub()
    _subscribe(positions_listener, YAGR_TEST_POSITIONS_CHANNEL)
    _read_all(positions_listener)

    pedestrina_positions_listener = redis_store.pubsub()
    _subscribe(
        pedestrina_positions_listener, YAGR_TEST_PEDESTRAIN_POSITIONS_CHANNEL,
    )
    _read_all(pedestrina_positions_listener)

    unix_ts = 1568198535000

    park_id = 'park'
    driver_id = 'pedestrian'
    params = {'pipeline': 'test', 'uuid': f'{park_id}_{driver_id}'}
    data_args = {'positions': []}

    position = {
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
        'sensors': dict([('transport_type', 'pedestrian')]),
    }
    data_args['positions'].append(position)

    headers = {'Accept-Language': 'ru', 'X-YaFts-Client-Service-Tvm': '123'}
    response = await taxi_yagr_adv.post(
        '/v2/position/store', json=data_args, headers=headers, params=params,
    )
    assert response.status_code == 200

    redis_message = _get_message(positions_listener, redis_store)
    assert redis_message is None

    ped_pos_redis_message = _get_message(
        pedestrina_positions_listener, redis_store,
    )
    assert ped_pos_redis_message is not None
    deserialized = universal_signals.deserialize_message(
        ped_pos_redis_message['data'],
    )
    signals = deserialized['payload']
    assert len(signals) == 1
    signal = signals[0]
    assert signal == {
        'client_timestamp': unix_ts * 1000,
        'contractor_id': 'park_pedestrian',
        'source': 'Verified',
        'sensors': [{'key': 'transport_type', 'value': 'pedestrian'}],
        'signals': [
            {
                'geo_position': {
                    'accuracy': 5,
                    'altitude': 9,
                    'direction': 23,
                    'position': [30.20, 57.40],
                    'speed': 10.0,
                },
                'log_likelihood': 0.0,
                'prediction_shift': 0,
                'probability': 1.0,
            },
        ],
    }

    park_id = 'park'
    driver_id = 'nonpedestrian'
    params = {'pipeline': 'test', 'uuid': f'{park_id}_{driver_id}'}
    data_args = {'positions': []}

    position = {
        'geodata': {
            'lat': 56.40,
            'lon': 31.20,
            'direction': 23,
            'speed': 10.0,
            'accuracy': 5,
            'altitude': 9,
        },
        'source': 'Verified',
        'timestamp': unix_ts,
        'sensors': {'transport_type': 'bicycle'},
    }
    data_args['positions'].append(position)

    headers = {'Accept-Language': 'ru', 'X-YaFts-Client-Service-Tvm': '123'}
    response = await taxi_yagr_adv.post(
        '/v2/position/store', json=data_args, headers=headers, params=params,
    )
    assert response.status_code == 200

    ped_pos_redis_message = _get_message(
        pedestrina_positions_listener, redis_store,
    )
    assert ped_pos_redis_message is None

    redis_message = _get_message(positions_listener, redis_store)
    assert redis_message is not None
    deserialized = universal_signals.deserialize_message(redis_message['data'])
    signals = deserialized['payload']
    assert len(signals) == 1
    signal = signals[0]
    assert signal == {
        'client_timestamp': unix_ts * 1000,
        'contractor_id': 'park_nonpedestrian',
        'source': 'Verified',
        'sensors': [{'key': 'transport_type', 'value': 'bicycle'}],
        'signals': [
            {
                'geo_position': {
                    'accuracy': 5,
                    'altitude': 9,
                    'direction': 23,
                    'position': [31.20, 56.40],
                    'speed': 10.0,
                },
                'log_likelihood': 0.0,
                'prediction_shift': 0,
                'probability': 1.0,
            },
        ],
    }


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': True,
        'future_boundary': 60,
        'past_boundary': 7200,
    },
)
async def test_pipline_time_boundaries(taxi_yagr_adv, redis_store):
    await taxi_yagr_adv.update_service_config(
        'pipeline_config_destinations.json',
    )

    positions_listener = redis_store.pubsub()
    _subscribe(positions_listener, YAGR_TEST_DISCARD_POSITIONS_CHANNEL)
    _read_all(positions_listener)

    unix_ts_ok1 = (
        datetime.datetime(
            2019,
            9,
            11,
            13,
            42,
            00,
            tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
        ).timestamp()
        * 1000
    )
    unix_ts_ok2 = (
        datetime.datetime(
            2019,
            9,
            11,
            13,
            42,
            30,
            tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
        ).timestamp()
        * 1000
    )
    unix_ts_discard1 = (
        datetime.datetime(
            2019,
            9,
            11,
            10,
            41,
            30,
            tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
        ).timestamp()
        * 1000
    )
    unix_ts_discard2 = (
        datetime.datetime(
            2019,
            9,
            11,
            13,
            43,
            30,
            tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
        ).timestamp()
        * 1000
    )

    park_id = 'sberty'
    driver_id = 'sqwerty1'
    data_args = {
        'positions': [
            {
                'lon': 30.20,
                'lat': 57.40,
                'source': 'Verified',
                'direction': 23,
                'speed': 10.0,
                'accuracy': 5,
                'altitude': 9,
                'unix_timestamp': unix_ts_ok1,
            },
            {
                'lon': 31.20,
                'lat': 56.40,
                'source': 'Verified',
                'direction': 20,
                'speed': 12.0,
                'accuracy': 4,
                'altitude': 10,
                'unix_timestamp': unix_ts_ok2,
            },
            {
                'lon': 32.20,
                'lat': 57.40,
                'source': 'Verified',
                'direction': 23,
                'speed': 10.0,
                'accuracy': 5,
                'altitude': 9,
                'unix_timestamp': unix_ts_discard1,
            },
            {
                'lon': 33.20,
                'lat': 56.40,
                'source': 'Verified',
                'direction': 20,
                'speed': 12.0,
                'accuracy': 4,
                'altitude': 10,
                'unix_timestamp': unix_ts_discard2,
            },
        ],
        'contractor_id': {'dbid': park_id, 'uuid': driver_id},
    }

    headers = {'Accept-Language': 'ru'}
    response = await taxi_yagr_adv.post(
        '/pipeline/test/position/store', json=data_args, headers=headers,
    )
    assert response.status_code == 200

    # check after all processing is done
    pos_redis_message = _get_message(positions_listener, redis_store)
    assert pos_redis_message is not None
    deserialized = geobus.deserialize_positions_v2(pos_redis_message['data'])[
        'positions'
    ]
    assert len(deserialized) == 2

    pos = deserialized[0]
    print(pos)
    assert pos == {
        'position': [30.2, 57.4],
        'direction': 23,
        'unix_timestamp': 1568198520000,
        'rtc_timestamp': 0,
        'speed': 10.0,
        'accuracy': 5,
        'source': 0,
        'timestamp': 1568198520,
        'driver_id': 'sberty_sqwerty1',
    }

    pos = deserialized[1]
    print(pos)
    assert pos == {
        'position': [31.2, 56.4],
        'direction': 20,
        'unix_timestamp': 1568198550000,
        'rtc_timestamp': 0,
        'speed': 12.0,
        'accuracy': 4,
        'source': 0,
        'timestamp': 1568198550,
        'driver_id': 'sberty_sqwerty1',
    }
