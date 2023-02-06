# pylint: disable=import-error,too-many-lines

import datetime

from dap_tools.dap import dap_fixture  # noqa: F401 C5521
import pytest

from geobus_tools import (
    geobus,
)  # noqa: F401 C5521 from tests_plugins import utils


# YAGR_OUTPUT_CHANNEL = 'channel:tracker:position'
YAGR_OUTPUT_V2_CHANNEL = 'channel:yagr:position'
YAGR_OUTPUT_SIGNAL_V2_CHANNEL = 'channel:yagr:signal_v2'


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
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 60,
        'past_boundary': 7200,
    },
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 0,
        'driver_v1_position_store': 0,
        'driver_v1_position_store_extra_data': 0,
    },
)
@pytest.mark.config(YAGR_WRITE_TO_LBKX_PERCENT=100)
@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_driver_position_store_basic_check(
        taxi_yagr_adv,
        dap,
        redis_store,
        testpoint,
        user_agent,
        app_family,
        geobus_redis_getter,
):
    @testpoint('write-verified-position-to-yt')
    def testpoint_clid(data):
        pass

    @testpoint('write-position-to-lbkx')
    def testpoint_lbkx(data):
        pass

    signal_v2_listener = await geobus_redis_getter.get_listener(
        YAGR_OUTPUT_SIGNAL_V2_CHANNEL,
    )

    position_listener = await geobus_redis_getter.get_listener(
        YAGR_OUTPUT_V2_CHANNEL,
    )

    park_id = 'berty'
    driver_id = 'qwerty1'
    taxi_yagr_adv = dap.create_driver_wrapper(
        taxi_yagr_adv,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )

    data_args = {'positions': []}

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
        '/driver/v1/position/store', json=data_args, headers=headers,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    data = await testpoint_clid.wait_call()
    await testpoint_lbkx.wait_call()

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
    redis_message = position_listener.get_message()
    assert redis_message is not None
    deserialized = geobus.deserialize_positions_v2(redis_message['data'])[
        'positions'
    ]
    print(deserialized)
    assert len(deserialized) == 1
    pos = deserialized[0]
    assert pos['driver_id'] == park_id + '_' + driver_id
    assert pos['position'] == [first_position['lon'], first_position['lat']]
    assert pos['source'] == 0
    assert pos['speed'] == first_position['speed']
    assert pos['direction'] == first_position['direction']
    assert pos['accuracy'] == first_position['accuracy']
    assert pos['timestamp'] == unix_ts / 1000


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(YAGR_MULTIPOS_YT_LOG_DRIVER_PERCENT=100)
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 60,
        'past_boundary': 7200,
    },
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 0,
        'driver_v1_position_store': 0,
        'driver_v1_position_store_extra_data': 0,
    },
)
@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_driver_position_store_log_multipos_to_yt_check(
        taxi_yagr_adv, dap, redis_store, testpoint, user_agent, app_family,
):
    @testpoint('write-position-from-source-to-yt')
    def testpoint_position_from_source(data):
        pass

    park_id = 'berty'
    driver_id = 'qwerty_for_multipos'
    taxi_yagr_adv = dap.create_driver_wrapper(
        taxi_yagr_adv,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )
    data_args = {'positions': []}

    unix_ts = datetime.datetime(2019, 9, 11, 13, 42, 15).timestamp() * 1000
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
        'unix_timestamp': unix_ts,
    }
    data_args['positions'].append(third_position)

    headers = {'Accept-Language': 'ru'}
    response = await taxi_yagr_adv.post(
        '/driver/v1/position/store', json=data_args, headers=headers,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    def check_driver_id(test_data):
        assert test_data['contractor_uuid'] == driver_id
        assert test_data['contractor_dbid'] == park_id

    data = await testpoint_position_from_source.wait_call()
    json = data['data']['json']
    assert json['source'] == 'verified'
    eql_keys = ['lat', 'lon', 'altitude', 'direction', 'speed', 'accuracy']
    for k in eql_keys:
        assert json[k] == first_position[k]
    # unix_timestamp is in microseconds in Yt
    k = 'unix_timestamp'
    assert json[k] == first_position[k] * 1000  # Yt is in microseconds

    check_driver_id(json)

    data = await testpoint_position_from_source.wait_call()
    json = data['data']['json']
    assert json['source'] == 'android network'
    eql_keys = ['lat', 'lon', 'altitude', 'direction', 'speed', 'accuracy']
    for k in eql_keys:
        assert json[k] == second_position[k]
    k = 'unix_timestamp'
    assert json[k] == second_position[k] * 1000  # Yt is in microseconds
    check_driver_id(json)

    data = await testpoint_position_from_source.wait_call()
    json = data['data']['json']
    assert json['source'] == 'yandex lbs ip'
    eql_keys = ['lat', 'lon']
    for k in eql_keys:
        assert json[k] == third_position[k]
    k = 'unix_timestamp'
    assert json[k] == third_position[k] * 1000  # Yt is in microseconds
    missing_fields = ['altitude', 'direction', 'speed', 'accuracy']
    for k in missing_fields:
        assert k not in json
    check_driver_id(json)


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 60,
        'past_boundary': 7200,
    },
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 0,
        'driver_v1_position_store': 0,
        'driver_v1_position_store_extra_data': 0,
    },
)
@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_driver_position_store_empty_data_check(
        taxi_yagr_adv,
        dap,
        redis_store,
        testpoint,
        user_agent,
        app_family,
        geobus_redis_getter,
):
    positions_listener = redis_store.pubsub()
    _subscribe(positions_listener, YAGR_OUTPUT_V2_CHANNEL)
    _read_all(positions_listener)

    park_id = 'berty'
    driver_id = 'qwerty2'
    taxi_yagr_adv = dap.create_driver_wrapper(
        taxi_yagr_adv,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )
    data_args = {'positions': []}

    unix_ts = datetime.datetime(2019, 9, 11, 13, 42, 15).timestamp() * 1000
    # 1st pos
    first_position = {'unix_timestamp': unix_ts}
    data_args['positions'].append(first_position)

    headers = {'Accept-Language': 'ru'}
    response = await taxi_yagr_adv.post(
        '/driver/v1/position/store', json=data_args, headers=headers,
    )
    assert response.status_code == 400


@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
@pytest.mark.config(
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 0,
        'driver_v1_position_store': 0,
        'driver_v1_position_store_extra_data': 0,
    },
)
async def test_driver_position_store_time_out_of_bounds_check(
        taxi_yagr_adv, dap, redis_store, testpoint, user_agent, app_family,
):
    """Check that timestamps after 31-12-2105 cause error code 400"""

    park_id = 'nextcentury'
    driver_id = 'doc'
    taxi_yagr_adv = dap.create_driver_wrapper(
        taxi_yagr_adv,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )
    data_args = {'positions': []}

    unix_ts = datetime.datetime(2106, 9, 11, 13, 42, 15).timestamp() * 1000
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

    headers = {'Accept-Language': 'ru'}
    response = await taxi_yagr_adv.post(
        '/driver/v1/position/store', json=data_args, headers=headers,
    )
    assert response.status_code == 400

    first_position = {
        'lon': 30.20,
        'lat': 57.40,
        'source': 'Verified',
        'direction': 23,
        'speed': 10.0,
        'accuracy': 5,
        'altitude': 9,
        'unix_timestamp': -5,
    }
    data_args['positions'] = [first_position]
    response = await taxi_yagr_adv.post(
        '/driver/v1/position/store', json=data_args, headers=headers,
    )
    assert response.status_code == 400


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 60,
        'past_boundary': 7200,
    },
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 0,
        'driver_v1_position_store': 0,
        'driver_v1_position_store_extra_data': 0,
    },
)
@pytest.mark.config(YAGR_WRITE_TO_LBKX_PERCENT=100)
@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_driver_position_store_clid_to_yt_check(
        taxi_yagr_adv,
        dap,
        redis_store,
        testpoint,
        user_agent,
        app_family,
        geobus_redis_getter,
):
    @testpoint('write-verified-position-to-yt')
    def testpoint_clid(data):
        pass

    @testpoint('write-position-to-lbkx')
    def testpoint_lbkx(data):
        pass

    park_id = 'dbid0'
    driver_id = 'qwerty3'
    taxi_yagr_adv = dap.create_driver_wrapper(
        taxi_yagr_adv,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )
    data_args = {'positions': []}

    unix_ts = datetime.datetime(2019, 9, 11, 13, 42, 15).timestamp() * 1000
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
        '/driver/v1/position/store', json=data_args, headers=headers,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    data = await testpoint_clid.wait_call()
    await testpoint_lbkx.wait_call()
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
    assert kv_data['clid'] == 'clid0'


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 60,
        'past_boundary': 7200,
    },
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 0,
        'driver_v1_position_store': 0,
        'driver_v1_position_store_extra_data': 0,
    },
)
@pytest.mark.config(YAGR_WRITE_TO_LBKX_PERCENT=100)
@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_driver_position_store_check_empty_fields_to_yt(
        taxi_yagr_adv,
        dap,
        redis_store,
        testpoint,
        user_agent,
        app_family,
        geobus_redis_getter,
):
    @testpoint('write-verified-position-to-yt')
    def testpoint_clid(data):
        pass

    @testpoint('write-position-to-lbkx')
    def testpoint_lbkx(data):
        pass

    park_id = 'berty'
    driver_id = 'qwerty4'
    taxi_yagr_adv = dap.create_driver_wrapper(
        taxi_yagr_adv,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )
    data_args = {'positions': []}

    unix_ts = datetime.datetime(2019, 9, 11, 13, 42, 15).timestamp() * 1000
    # 1st pos
    first_position = {
        'lon': 30.20,
        'lat': 57.40,
        'source': 'Verified',
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
        '/driver/v1/position/store', json=data_args, headers=headers,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    data = await testpoint_clid.wait_call()
    await testpoint_lbkx.wait_call()
    tskv = data['data']['tskv']
    kv_pairs = list(map(lambda x: x.split('='), tskv.split('\t')[1:]))
    kv_data = {value[0].strip(): value[1].strip() for value in kv_pairs}
    assert kv_data['timestamp'] == str(int(unix_ts / 1000))
    assert kv_data['db_id'] == park_id
    assert kv_data['uuid'] == driver_id
    assert kv_data['direction'] == '0.000000'
    assert kv_data['lat'] == '57.400000'
    assert kv_data['lon'] == '30.200000'
    assert kv_data['speed'] == '-1.000000'
    assert kv_data['bad'] == '0'
    assert kv_data['clid'] == ''


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 60,
        'past_boundary': 7200,
    },
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 0,
        'driver_v1_position_store': 0,
        'driver_v1_position_store_extra_data': 0,
    },
)
@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_driver_position_store_not_authorized(
        taxi_yagr_adv, dap, redis_store, testpoint, user_agent, app_family,
):
    headers = {
        'User-Agent': user_agent,
        'Accept-Language': 'ru',
        'X-Request-Application-Version': '9.1',
        'X-YaTaxi-Park-Id': '',
        'X-YaTaxi-Driver-Profile-Id': '',
    }
    response = await taxi_yagr_adv.post(
        '/driver/v1/position/store', json={'positions': []}, headers=headers,
    )
    assert response.status_code == 401


@pytest.mark.skip(reason='flaky TAXIFLAPTEST-2563')
@pytest.mark.now('2019-09-11T13:42:15+0000')  # 1568209335
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': True,
        'future_boundary': 30,
        'past_boundary': 30,
    },
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 0,
        'driver_v1_position_store': 0,
        'driver_v1_position_store_extra_data': 0,
    },
)
@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_driver_position_store_discard_too_old_points(
        taxi_yagr_adv, dap, redis_store, testpoint, user_agent, app_family,
):
    # Check we convert negative speeds to kNoSpeed
    redis_listener = redis_store.pubsub()
    _subscribe(redis_listener, YAGR_OUTPUT_V2_CHANNEL)
    _read_all(redis_listener)

    park_id = 'berty'
    driver_id = 'qwerty5'
    taxi_yagr_adv = dap.create_driver_wrapper(
        taxi_yagr_adv,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )

    def get_data(timestamp_in_seconds):
        position = {
            'lon': 30.20,
            'lat': 57.40,
            'source': 'Verified',
            'direction': 23,
            'speed': 10.0,
            'accuracy': 5,
            'altitude': 9,
            'unix_timestamp': timestamp_in_seconds * 1000,
        }  # in ms
        return {'positions': [position]}

    headers = {'Accept-Language': 'ru'}

    # test 1 - send data slightly in the past - within past_boundary
    # It should arrive with unchanged timestamp
    response = await taxi_yagr_adv.post(
        '/driver/v1/position/store',
        headers=headers,
        json=get_data(1568209330),
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    redis_message = _get_message(redis_listener, redis_store)
    positions = geobus.deserialize_positions_v2(redis_message['data'])[
        'positions'
    ]
    assert positions[0]['timestamp'] == 1568209330

    # test 2 - send data slightly in the future - within future_boundary
    # It should arrive with timestamp equal to now
    response = await taxi_yagr_adv.post(
        '/driver/v1/position/store',
        headers=headers,
        json=get_data(1568209340),
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    redis_message = _get_message(redis_listener, redis_store)
    positions = geobus.deserialize_positions_v2(redis_message['data'])[
        'positions'
    ]
    assert positions[0]['timestamp'] == 1568209335

    # test 3 - send data way outside of past_boundary
    # It should be discarded
    response = await taxi_yagr_adv.post(
        '/driver/v1/position/store',
        headers=headers,
        json=get_data(1568209300),
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    redis_message = _get_message(redis_listener, redis_store)
    assert redis_message is None

    # test 4 - send data way outside of future_boundary
    # It should be discarded
    response = await taxi_yagr_adv.post(
        '/driver/v1/position/store',
        headers=headers,
        json=get_data(1568209370),
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    redis_message = _get_message(redis_listener, redis_store)
    assert redis_message is None


@pytest.mark.skip(reason='flaky TODO(unlimiq): Check properly')
@pytest.mark.now('2019-09-11T13:42:15+0000')  # UTC zone here! 1568209335
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 10,
        'past_boundary': 10,
    },
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 0,
        'driver_v1_position_store': 0,
        'driver_v1_position_store_extra_data': 0,
    },
)
@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_driver_position_store_dont_discard_old_points(
        taxi_yagr_adv,
        dap,
        redis_store,
        testpoint,
        now,
        user_agent,
        app_family,
):
    # Check we convert negative speeds to kNoSpeed
    redis_listener = redis_store.pubsub()
    _subscribe(redis_listener, YAGR_OUTPUT_V2_CHANNEL)
    _read_all(redis_listener)

    park_id = 'berty'
    driver_id = 'qwerty6'
    taxi_yagr_adv = dap.create_driver_wrapper(
        taxi_yagr_adv,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )

    def get_data(timestamp_in_seconds):
        position = {
            'lon': 30.20,
            'lat': 57.40,
            'source': 'Verified',
            'direction': 23,
            'speed': 10.0,
            'accuracy': 5,
            'altitude': 9,
            'unix_timestamp': timestamp_in_seconds * 1000,
        }  # in ms
        return {'positions': [position]}

    headers = {'Accept-Language': 'ru'}

    really_old_timestamp = 1000
    response = await taxi_yagr_adv.post(
        '/driver/v1/position/store',
        headers=headers,
        json=get_data(really_old_timestamp),
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    redis_message = _get_message(redis_listener, redis_store)
    positions = geobus.deserialize_positions_v2(redis_message['data'])[
        'positions'
    ]
    assert positions[0]['timestamp'] == 1568209335


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(YAGR_DRIVER_EXTRA_DATA_POS_PERCENT=100)
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 60,
        'past_boundary': 7200,
    },
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 0,
        'driver_v1_position_store': 0,
        'driver_v1_position_store_extra_data': 0,
    },
)
@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_driver_position_store_pos_to_driver_extra_data(
        taxi_yagr_adv, dap, redis_store, testpoint, user_agent, app_family,
):
    @testpoint('write-verified-position-to-driver-extra-data')
    def testpoint_position_to_yt(data):
        pass

    park_id = 'driverextradata'
    driver_id = 'qwertydriverextradata'
    taxi_yagr_adv = dap.create_driver_wrapper(
        taxi_yagr_adv,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )
    data_args = {'positions': []}

    unix_ts = datetime.datetime(2019, 9, 11, 13, 42, 15).timestamp() * 1000
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

    headers = {'Accept-Language': 'ru'}
    response = await taxi_yagr_adv.post(
        '/driver/v1/position/store', json=data_args, headers=headers,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    def check_driver_id(test_data):
        assert test_data['contractor_uuid'] == driver_id
        assert test_data['contractor_dbid'] == park_id

    data = await testpoint_position_to_yt.wait_call()
    json = data['data']['json']
    signal = json['position']
    eql_keys = ['lat', 'lon', 'altitude', 'direction', 'speed', 'accuracy']
    for k in eql_keys:
        assert signal[k] == first_position[k]

    assert signal['timestamp'] * 1000 == first_position['unix_timestamp']

    check_driver_id(json)


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
