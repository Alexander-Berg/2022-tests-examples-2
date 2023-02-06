# pylint: disable=import-error,too-many-lines
# flake8: noqa: E501

import datetime

from dap_tools.dap import dap_fixture  # noqa: F401 C5521
import pytest


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
    CONTRACTOR_TRANSPORT_CACHE_SETTINGS={
        'contractor-fts-receiver': {
            'cache_enabled': True,
            'batch_size': 1,
            'only_active_contractors': True,
        },
    },
)
@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_driver_position_store_basic_check(
        taxi_contractor_fts_receiver,
        dap,
        testpoint,
        user_agent,
        app_family,
        contractor_transport_request,
        mockserver,
):
    @testpoint('write-verified-position-to-yt')
    def testpoint_clid(data):
        pass

    @testpoint('write-position-to-lbkx')
    def testpoint_lbkx(data):
        pass

    unix_ts = int(
        datetime.datetime(
            2019,
            9,
            11,
            13,
            42,
            15,
            tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
        ).timestamp()
        * 1000,
    )

    @mockserver.json_handler('/fleet-tracking-system/v1/position/store')
    def mock_pipeline(request):
        assert request.query['uuid'] == 'berty_qwerty1'
        assert request.json == {
            'positions': [
                {
                    'geodata': {
                        'accuracy': 5.0,
                        'altitude': 9.0,
                        'direction': 23,
                        'lat': 57.4,
                        'lon': 30.2,
                        'speed': 10.0,
                    },
                    'source': 'Verified',
                    'sensors': {'transport_type': 'car', 'region': ''},
                    'timestamp': unix_ts,
                },
                {
                    'geodata': {
                        'accuracy': 3.0,
                        'altitude': 15.0,
                        'direction': 25,
                        'lat': 58.0,
                        'lon': 31.0,
                        'speed': 11.0,
                    },
                    'source': 'AndroidNetwork',
                    'sensors': {},
                    'timestamp': unix_ts,
                },
                {
                    'geodata': {
                        'accuracy': 1.0,
                        'altitude': 20.0,
                        'lat': 59.0,
                        'lon': 29.0,
                        'speed': 20.0,
                        # no direction
                    },
                    'source': 'YandexLbsIp',
                    'sensors': {},
                    'timestamp': unix_ts,
                },
            ],
        }
        return mockserver.make_response(status=200)

    park_id = 'berty'
    driver_id = 'qwerty1'
    taxi_contractor_fts_receiver = dap.create_driver_wrapper(
        taxi_contractor_fts_receiver,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )

    data_args = {'positions': []}

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
        # incorrect direction, but somehow some clients still send
        # it.a TAXIGRAPH-1923
        'direction': -1,
        'speed': 20.0,
        'accuracy': 1,
        'altitude': 20,
        'unix_timestamp': unix_ts,
    }
    data_args['positions'].append(third_position)

    headers = {'Accept-Language': 'ru'}
    response = await taxi_contractor_fts_receiver.post(
        '/driver/v1/position/store', json=data_args, headers=headers,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
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

    assert mock_pipeline.times_called == 1
    assert testpoint_lbkx.times_called == 0


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(YAGR_MULTIPOS_YT_LOG_DRIVER_PERCENT=100)
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 60,
        'past_boundary': 7200,
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
        taxi_contractor_fts_receiver,
        dap,
        testpoint,
        user_agent,
        app_family,
        mockserver,
):
    @testpoint('write-position-from-source-to-yt')
    def testpoint_position_from_source(data):
        pass

    unix_ts = int(
        datetime.datetime(
            2019,
            9,
            11,
            13,
            42,
            15,
            tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
        ).timestamp()
        * 1000,
    )

    @mockserver.json_handler('/fleet-tracking-system/v1/position/store')
    def mock_pipeline(request):
        assert request.query['uuid'] == 'berty_qwerty1'
        assert request.json == {
            'positions': [
                {
                    'geodata': {
                        'accuracy': 5.0,
                        'altitude': 9.0,
                        'direction': 23,
                        'lat': 57.4,
                        'lon': 30.2,
                        'speed': 10.0,
                    },
                    'source': 'Verified',
                    'sensors': {'transport_type': 'car', 'region': ''},
                    'timestamp': unix_ts,
                },
                {
                    'geodata': {
                        'accuracy': 3.0,
                        'altitude': 15.0,
                        'direction': 25,
                        'lat': 58.0,
                        'lon': 31.0,
                        'speed': 11.0,
                    },
                    'source': 'AndroidNetwork',
                    'sensors': {},
                    'timestamp': unix_ts,
                },
                {
                    'geodata': {'lat': 59.0, 'lon': 29.0},
                    'source': 'YandexLbsIp',
                    'sensors': {},
                    'timestamp': unix_ts,
                },
            ],
        }
        return mockserver.make_response(status=200)

    park_id = 'berty'
    driver_id = 'qwerty1'
    taxi_contractor_fts_receiver = dap.create_driver_wrapper(
        taxi_contractor_fts_receiver,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )
    data_args = {'positions': []}

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
    response = await taxi_contractor_fts_receiver.post(
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

    assert mock_pipeline.times_called == 1


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 60,
        'past_boundary': 7200,
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
        taxi_contractor_fts_receiver, dap, user_agent, app_family, mockserver,
):
    unix_ts = int(
        datetime.datetime(
            2019,
            9,
            11,
            13,
            42,
            15,
            tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
        ).timestamp()
        * 1000,
    )

    @mockserver.json_handler('/fleet-tracking-system/v1/position/store')
    def mock_pipeline(request):
        pass

    park_id = 'berty'
    driver_id = 'qwerty2'
    taxi_contractor_fts_receiver = dap.create_driver_wrapper(
        taxi_contractor_fts_receiver,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )
    data_args = {'positions': []}

    # 1st pos
    first_position = {'unix_timestamp': unix_ts}
    data_args['positions'].append(first_position)

    headers = {'Accept-Language': 'ru'}
    response = await taxi_contractor_fts_receiver.post(
        '/driver/v1/position/store', json=data_args, headers=headers,
    )
    assert response.status_code == 400
    assert mock_pipeline.times_called == 0


@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_driver_position_store_time_out_of_bounds_check(
        taxi_contractor_fts_receiver, dap, user_agent, app_family, mockserver,
):
    """Check that timestamps after 31-12-2105 cause error code 400"""

    @mockserver.json_handler('/fleet-tracking-system/v1/position/store')
    def mock_pipeline(request):
        pass

    park_id = 'nextcentury'
    driver_id = 'doc'
    taxi_contractor_fts_receiver = dap.create_driver_wrapper(
        taxi_contractor_fts_receiver,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )
    data_args = {'positions': []}

    unix_ts = int(
        datetime.datetime(
            2016,
            9,
            11,
            13,
            42,
            15,
            tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
        ).timestamp()
        * 1000,
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

    headers = {'Accept-Language': 'ru'}
    response = await taxi_contractor_fts_receiver.post(
        '/driver/v1/position/store', json=data_args, headers=headers,
    )
    assert response.status_code == 200

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
    response = await taxi_contractor_fts_receiver.post(
        '/driver/v1/position/store', json=data_args, headers=headers,
    )
    assert response.status_code == 400

    assert mock_pipeline.times_called == 0


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 60,
        'past_boundary': 7200,
    },
)
@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_driver_position_store_clid_to_yt_check(
        taxi_contractor_fts_receiver,
        dap,
        testpoint,
        user_agent,
        app_family,
        mockserver,
):
    @testpoint('write-verified-position-to-yt')
    def testpoint_clid(data):
        pass

    @testpoint('write-position-to-lbkx')
    def testpoint_lbkx(data):
        pass

    unix_ts = int(
        datetime.datetime(
            2019,
            9,
            11,
            13,
            42,
            15,
            tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
        ).timestamp()
        * 1000,
    )

    @mockserver.json_handler('/fleet-tracking-system/v1/position/store')
    def mock_pipeline(request):
        assert request.query['uuid'] == 'dbid0_qwerty3'
        assert request.json == {
            'positions': [
                {
                    'geodata': {
                        'accuracy': 5.0,
                        'altitude': 9.0,
                        'direction': 23,
                        'lat': 57.4,
                        'lon': 30.2,
                        'speed': 10.0,
                    },
                    'source': 'Verified',
                    'sensors': {'region': ''},
                    'timestamp': unix_ts,
                },
                {
                    'geodata': {
                        'accuracy': 3.0,
                        'altitude': 15.0,
                        'direction': 25,
                        'lat': 58.0,
                        'lon': 31.0,
                        'speed': 11.0,
                    },
                    'source': 'AndroidNetwork',
                    'sensors': {},
                    'timestamp': unix_ts,
                },
                {
                    'geodata': {
                        'accuracy': 1.0,
                        'altitude': 20.0,
                        'direction': 20,
                        'lat': 59.0,
                        'lon': 29.0,
                        'speed': 20.0,
                    },
                    'source': 'YandexLbsIp',
                    'sensors': {},
                    'timestamp': unix_ts,
                },
            ],
        }
        return mockserver.make_response(status=200)

    park_id = 'dbid0'
    driver_id = 'qwerty3'
    taxi_contractor_fts_receiver = dap.create_driver_wrapper(
        taxi_contractor_fts_receiver,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )
    data_args = {'positions': []}

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
    response = await taxi_contractor_fts_receiver.post(
        '/driver/v1/position/store', json=data_args, headers=headers,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
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
    assert kv_data['clid'] == 'clid0'

    assert mock_pipeline.times_called == 1
    assert testpoint_lbkx.times_called == 0


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 60,
        'past_boundary': 7200,
    },
)
@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_driver_position_store_check_empty_fields_to_yt(
        taxi_contractor_fts_receiver,
        dap,
        testpoint,
        user_agent,
        app_family,
        mockserver,
):
    @testpoint('write-verified-position-to-yt')
    def testpoint_clid(data):
        pass

    @testpoint('write-position-to-lbkx')
    def testpoint_lbkx(data):
        pass

    unix_ts = int(
        datetime.datetime(
            2019,
            9,
            11,
            13,
            42,
            15,
            tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
        ).timestamp()
        * 1000,
    )

    @mockserver.json_handler('/fleet-tracking-system/v1/position/store')
    def mock_pipeline(request):
        assert request.query['uuid'] == 'berty_qwerty4'
        assert request.json == {
            'positions': [
                {
                    'geodata': {'lat': 57.4, 'lon': 30.2},
                    'source': 'Verified',
                    'sensors': {'region': ''},
                    'timestamp': unix_ts,
                },
                {
                    'geodata': {
                        'accuracy': 3.0,
                        'altitude': 15.0,
                        'direction': 25,
                        'lat': 58.0,
                        'lon': 31.0,
                        'speed': 11.0,
                    },
                    'source': 'AndroidNetwork',
                    'sensors': {},
                    'timestamp': unix_ts,
                },
                {
                    'geodata': {
                        'accuracy': 1.0,
                        'altitude': 20.0,
                        'direction': 20,
                        'lat': 59.0,
                        'lon': 29.0,
                        'speed': 20.0,
                    },
                    'source': 'YandexLbsIp',
                    'sensors': {},
                    'timestamp': unix_ts,
                },
            ],
        }
        return mockserver.make_response(status=200)

    park_id = 'berty'
    driver_id = 'qwerty4'
    taxi_contractor_fts_receiver = dap.create_driver_wrapper(
        taxi_contractor_fts_receiver,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )
    data_args = {'positions': []}

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
    response = await taxi_contractor_fts_receiver.post(
        '/driver/v1/position/store', json=data_args, headers=headers,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    data = await testpoint_clid.wait_call()
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

    assert mock_pipeline.times_called == 1
    assert testpoint_lbkx.times_called == 0


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 60,
        'past_boundary': 7200,
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
        taxi_contractor_fts_receiver, user_agent, app_family,
):
    headers = {
        'User-Agent': user_agent,
        'Accept-Language': 'ru',
        'X-Request-Application-Version': '9.1',
        'X-YaTaxi-Park-Id': '',
        'X-YaTaxi-Driver-Profile-Id': '',
    }
    response = await taxi_contractor_fts_receiver.post(
        '/driver/v1/position/store', json={'positions': []}, headers=headers,
    )
    assert response.status_code == 401


@pytest.mark.now('2019-09-11T13:42:15+0300')  # 1568198535s
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': True,
        'future_boundary': 30,
        'past_boundary': 30,
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
        taxi_contractor_fts_receiver, dap, user_agent, app_family, mockserver,
):
    @mockserver.json_handler('/fleet-tracking-system/v1/position/store')
    def mock_pipeline(request):
        assert request.json['positions'][0]['timestamp'] in [
            1568198535000,
            1568198530000,
        ]
        assert request.query['uuid'] == 'berty_qwerty5'
        request.json['positions'][0]['timestamp'] = 1568209330000
        assert request.json == {
            'positions': [
                {
                    'geodata': {
                        'accuracy': 5.0,
                        'altitude': 9.0,
                        'direction': 23,
                        'lat': 57.4,
                        'lon': 30.2,
                        'speed': 10.0,
                    },
                    'source': 'Verified',
                    'sensors': {'region': ''},
                    'timestamp': 1568209330000,
                },
            ],
        }
        return mockserver.make_response(status=200)

    park_id = 'berty'
    driver_id = 'qwerty5'
    taxi_contractor_fts_receiver = dap.create_driver_wrapper(
        taxi_contractor_fts_receiver,
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
    response = await taxi_contractor_fts_receiver.post(
        '/driver/v1/position/store',
        headers=headers,
        json=get_data(1568198530),
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    # test 2 - send data slightly in the future - within future_boundary
    # It should arrive with timestamp equal to now
    response = await taxi_contractor_fts_receiver.post(
        '/driver/v1/position/store',
        headers=headers,
        json=get_data(1568198540),
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    # test 3 - send data way outside of past_boundary
    # It should be discarded
    response = await taxi_contractor_fts_receiver.post(
        '/driver/v1/position/store',
        headers=headers,
        json=get_data(1568198500),
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    # test 4 - send data way outside of future_boundary
    # It should be discarded
    response = await taxi_contractor_fts_receiver.post(
        '/driver/v1/position/store',
        headers=headers,
        json=get_data(1568198570),
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    assert mock_pipeline.times_called == 2


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 10,
        'past_boundary': 10,
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
        taxi_contractor_fts_receiver, dap, user_agent, app_family, mockserver,
):
    @mockserver.json_handler('/fleet-tracking-system/v1/position/store')
    def mock_pipeline(request):
        assert request.query['uuid'] == 'berty_qwerty6'
        assert request.json == {
            'positions': [
                {
                    'geodata': {
                        'accuracy': 5.0,
                        'altitude': 9.0,
                        'direction': 23,
                        'lat': 57.4,
                        'lon': 30.2,
                        'speed': 10.0,
                    },
                    'source': 'Verified',
                    'sensors': {'region': ''},
                    # when discarding is disabled, then old
                    # scheme kicks in, where position can't be older
                    # them some X seconds from now().
                    'timestamp': 1568198535000,
                },
            ],
        }
        return mockserver.make_response(status=200)

    park_id = 'berty'
    driver_id = 'qwerty6'
    taxi_contractor_fts_receiver = dap.create_driver_wrapper(
        taxi_contractor_fts_receiver,
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
    response = await taxi_contractor_fts_receiver.post(
        '/driver/v1/position/store',
        headers=headers,
        json=get_data(really_old_timestamp),
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    assert mock_pipeline.times_called == 1


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(YAGR_DRIVER_EXTRA_DATA_POS_PERCENT=100)
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 60,
        'past_boundary': 7200,
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
        taxi_contractor_fts_receiver,
        dap,
        testpoint,
        user_agent,
        app_family,
        mockserver,
):
    @testpoint('write-verified-position-to-driver-extra-data')
    def testpoint_position_to_yt(data):
        pass

    unix_ts = int(
        datetime.datetime(
            2019,
            9,
            11,
            13,
            42,
            15,
            tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
        ).timestamp()
        * 1000,
    )

    @mockserver.json_handler('/fleet-tracking-system/v1/position/store')
    def mock_pipeline(request):
        assert request.query['uuid'] == 'driverextradata_qwertydriverextradata'
        assert request.json == {
            'positions': [
                {
                    'geodata': {
                        'accuracy': 5.0,
                        'altitude': 9.0,
                        'direction': 23,
                        'lat': 57.4,
                        'lon': 30.2,
                        'speed': 10.0,
                    },
                    'source': 'Verified',
                    'sensors': {'region': ''},
                    'timestamp': unix_ts,
                },
            ],
        }
        return mockserver.make_response(status=200)

    park_id = 'driverextradata'
    driver_id = 'qwertydriverextradata'
    taxi_contractor_fts_receiver = dap.create_driver_wrapper(
        taxi_contractor_fts_receiver,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )
    data_args = {'positions': []}

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
    response = await taxi_contractor_fts_receiver.post(
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

    assert mock_pipeline.times_called == 1


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 60,
        'past_boundary': 7200,
    },
)
@pytest.mark.parametrize(
    'user_agent,app_family',
    [
        ('Taximeter 9.1 (1234)', 'taximeter'),
        ('Taximeter-Uber 9.1 (1234)', 'uberdriver'),
    ],
)
async def test_driver_position_store_special_case_with_ios_location(
        taxi_contractor_fts_receiver,
        dap,
        testpoint,
        user_agent,
        app_family,
        mockserver,
):

    unix_ts = int(
        datetime.datetime(
            2019,
            9,
            11,
            13,
            42,
            15,
            tzinfo=datetime.timezone(datetime.timedelta(hours=3)),
        ).timestamp()
        * 1000,
    )

    @mockserver.json_handler('/fleet-tracking-system/v1/position/store')
    def mock_pipeline(request):
        assert request.query['uuid'] == 'berty_qwerty1'
        assert request.json == {
            'positions': [
                {
                    'geodata': {
                        'accuracy': -1.0,
                        'altitude': 0.0,
                        'lat': 57.4,
                        'lon': 30.2,
                    },
                    'source': 'IosLocation',
                    'sensors': {},
                    'timestamp': unix_ts,
                },
            ],
        }
        return mockserver.make_response(status=200)

    park_id = 'berty'
    driver_id = 'qwerty1'
    taxi_contractor_fts_receiver = dap.create_driver_wrapper(
        taxi_contractor_fts_receiver,
        driver_uuid=driver_id,
        driver_dbid=park_id,
        user_agent=user_agent,
    )

    data_args = {'positions': []}

    # 1st pos
    first_position = {
        'lon': 30.20,
        'lat': 57.40,
        'source': 'IosLocation',
        'direction': None,
        'speed': None,
        'accuracy': -1,
        'altitude': 0,
        'unix_timestamp': unix_ts,
    }
    data_args['positions'].append(first_position)

    headers = {'Accept-Language': 'ru'}
    response = await taxi_contractor_fts_receiver.post(
        '/driver/v1/position/store', json=data_args, headers=headers,
    )
    assert response.status_code == 200
    assert mock_pipeline.times_called == 1
