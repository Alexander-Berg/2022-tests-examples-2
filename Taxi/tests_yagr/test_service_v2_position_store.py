# pylint: disable=import-error,too-many-lines,redefined-outer-name

import datetime

import pytest

from geobus_tools import geobus  # noqa: F401 C5521
from geobus_tools.redis import geobus_redis_getter  # noqa: F401 C5521

YAGR_OUTPUT_V2_CHANNEL = 'channel:yagr:position'
YAGR_OUTPUT_SIGNAL_V2_CHANNEL = 'channel:yagr:signal_v2'


@pytest.mark.now('2019-09-11T13:42:15+0300')
async def test_service_v2_position_store_basic_check(
        taxi_yagr_adv,
        redis_store,
        testpoint,
        geobus_redis_getter,  # noqa: F811
):
    @testpoint('write-verified-position-to-yt')
    def testpoint_clid(data):
        pass

    signal_v2_listener = await geobus_redis_getter.get_listener(
        YAGR_OUTPUT_SIGNAL_V2_CHANNEL,
    )

    positions_listener = await geobus_redis_getter.get_listener(
        YAGR_OUTPUT_V2_CHANNEL,
    )

    park_id = 'sberty'
    driver_id = 'sqwerty1'
    data_args = {
        'positions': [],
        'contractor_id': {'dbid': park_id, 'uuid': driver_id},
    }

    unix_ts = (
        datetime.datetime(
            2019,
            9,
            11,
            13,
            42,
            15,
            tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
        ).timestamp()
        * 1000
    )
    # 1st pos
    first_position = {
        'lon': 30.20,
        'lat': 57.40,
        'source': 'Verified',
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
        'source': 'AndroidNetwork',
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
        'source': 'YandexLbsIp',
        'direction': 20,
        'speed': 20.0,
        'accuracy': 1,
        'altitude': 20,
        'unix_timestamp': unix_ts,
    }
    data_args['positions'].append(third_position)

    headers = {'Accept-Language': 'ru'}
    response = await taxi_yagr_adv.post(
        '/service/v2/position/store', json=data_args, headers=headers,
    )
    assert response.status_code == 200
    assert response.json() == {}

    data = await testpoint_clid.wait_call()
    tskv = data['data']['tskv']
    kv_pairs = list(map(lambda x: x.split('='), tskv.split('\t')[1:]))
    kv_data = {value[0].strip(): value[1].strip() for value in kv_pairs}
    assert kv_data['timestamp'] == str(int(unix_ts / 1000))
    assert kv_data['db_id'] == park_id
    assert kv_data['uuid'] == driver_id
    assert kv_data['direction'] == '23.000000'
    assert kv_data['lat'] == '57.400000'
    assert kv_data['lon'] == '30.200000'
    assert kv_data['speed'] == '36.000000'
    assert kv_data['bad'] == '0'

    # check after all processing is done
    redis_message = signal_v2_listener.get_message()

    assert redis_message is not None
    deserialized = geobus.deserialize_signal_v2_message(redis_message['data'])
    assert len(deserialized) == 3
    pos = deserialized[0]
    assert pos['driver_id'] == park_id + '_' + driver_id
    assert pos['position'] == [first_position['lon'], first_position['lat']]
    source_verified_in_enum = 10
    assert pos['source'] == source_verified_in_enum
    assert pos['speed'] == first_position['speed']
    assert pos['direction'] == first_position['direction']
    assert pos['accuracy'] == first_position['accuracy']
    assert pos['altitude'] == first_position['altitude']
    assert pos['unix_time'] == unix_ts

    pos = deserialized[1]
    assert pos['driver_id'] == park_id + '_' + driver_id
    assert pos['position'] == [second_position['lon'], second_position['lat']]
    source_android_network_in_enum = 1
    assert pos['source'] == source_android_network_in_enum
    assert pos['speed'] == second_position['speed']
    assert pos['direction'] == second_position['direction']
    assert pos['accuracy'] == second_position['accuracy']
    assert pos['altitude'] == second_position['altitude']
    assert pos['unix_time'] == unix_ts

    pos = deserialized[2]
    assert pos['driver_id'] == park_id + '_' + driver_id
    assert pos['position'] == [third_position['lon'], third_position['lat']]
    source_yandex_lbs_ip_in_enum = 6
    assert pos['source'] == source_yandex_lbs_ip_in_enum
    assert pos['speed'] == third_position['speed']
    assert pos['direction'] == third_position['direction']
    assert pos['accuracy'] == third_position['accuracy']
    assert pos['altitude'] == third_position['altitude']
    assert pos['unix_time'] == unix_ts

    # check that verified position was sent in old channel
    redis_message = positions_listener.get_message()

    assert redis_message is not None
    deserialized = geobus.deserialize_positions_v2(redis_message['data'])[
        'positions'
    ]
    assert len(deserialized) == 1
    print(deserialized)
    pos = deserialized[0]
    assert pos['driver_id'] == park_id + '_' + driver_id
    assert pos['position'] == [first_position['lon'], first_position['lat']]
    assert pos['speed'] == first_position['speed']
    assert pos['direction'] == first_position['direction']
    assert pos['accuracy'] == first_position['accuracy']
    assert pos['timestamp'] == unix_ts / 1000


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
