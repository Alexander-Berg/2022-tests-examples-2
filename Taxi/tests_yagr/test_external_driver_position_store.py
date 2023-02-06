# pylint: disable=import-error
# flake8: noqa: E501

import urllib.parse

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
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 100,
        'driver_v1_position_store': 100,
        'driver_v1_position_store_extra_data': 100,
    },
)
@pytest.mark.parametrize('request_speed,', [-7, 100500])
async def test_driver_position_store_wrong_speed(
        taxi_yagr_adv, driver_authorizer, testpoint, request_speed, mockserver,
):
    @testpoint('write-positions-to-yt')
    def testpoint_clid(data):
        pass

    @mockserver.json_handler('/yagr/pipeline/taxi/position/store')
    def mock_pipeline(request):
        assert request.json == {
            'contractor_id': {'dbid': 'zxcvb', 'uuid': 'qwerty'},
            'positions': [
                {
                    'accuracy': 2.0,
                    'direction': 238,
                    'lat': 55.0,
                    'lon': 37.0,
                    'source': 'Verified',
                    'unix_timestamp': 1568198535000,
                },
            ],
        }
        return mockserver.make_response(status=200)

    driver_authorizer.set_session('zxcvb', 'asdfg', 'qwerty')
    params = {'session': 'asdfg', 'db': 'zxcvb'}
    data_args = {
        'driverId': 'qwerty',
        'lat': 55.0,
        'lon': 37.0,
        'angel': 238.4,
        'speed': request_speed,  # must be replaced with -1
        'isBad': 'false',
        'status': 1,
        'orderStatus': 0,
        'accuracy': 2.0,
        'timeGpsOrig': 1568388595484,
        'timeSystemOrig': 1568388595484,
        'timeSystemSync': 1568388595484,
    }
    data = urllib.parse.urlencode(data_args)
    response = await taxi_yagr_adv.post(
        '/driver/position/store', params=params, data=data,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}
    await testpoint_clid.wait_call()

    assert mock_pipeline.times_called == 1


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 60,
        'past_boundary': 7200,
    },
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 100,
        'driver_v1_position_store': 100,
        'driver_v1_position_store_extra_data': 100,
    },
)
async def test_driver_position_store_skip_bad(
        taxi_yagr_adv, driver_authorizer, testpoint, mockserver,
):
    @testpoint('write-positions-to-yt')
    def testpoint_clid(data):
        pass

    @mockserver.json_handler('/yagr/pipeline/taxi/position/store')
    def mock_pipeline(request):
        pass

    driver_authorizer.set_session('dbid0', 'asdfg', 'qwerty')
    params = {'session': 'asdfg', 'db': 'dbid0'}
    data_args = {
        'driverId': 'qwerty',
        'lat': 55.740404,
        'lon': 37.513276,
        'angel': 238.4,
        'speed': 58,
        'isBad': 'true',  # must be skipped
        'status': 1,
        'orderStatus': 0,
        'accuracy': 2.0,
        'timeGpsOrig': 1568388595484,
        'timeSystemOrig': 1568388595484,
        'timeSystemSync': 1568388595484,
    }
    data = urllib.parse.urlencode(data_args)
    response = await taxi_yagr_adv.post(
        '/driver/position/store', params=params, data=data,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}
    data = await testpoint_clid.wait_call()

    assert 'clid=clid0' in data['data']['tskv']
    assert mock_pipeline.times_called == 0


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 60,
        'past_boundary': 7200,
    },
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 100,
        'driver_v1_position_store': 100,
        'driver_v1_position_store_extra_data': 100,
    },
)
@pytest.mark.parametrize(
    'headers,app_family',
    [
        ({'User-Agent': 'Taximeter 9.1 (1234)'}, 'taximeter'),
        ({'User-Agent': 'Taximeter-Uber 9.1 (1234)'}, 'uberdriver'),
    ],
)
async def test_driver_position_store(
        taxi_yagr_adv,
        driver_authorizer,
        testpoint,
        headers,
        app_family,
        mockserver,
):
    @testpoint('write-positions-to-yt')
    def testpoint_clid(data):
        pass

    @mockserver.json_handler('/yagr/pipeline/taxi/position/store')
    def mock_pipeline(request):
        assert (
            abs(request.json['positions'][0]['speed'] - 16.111111) < 0.000001
        )
        request.json['positions'][0]['speed'] = 16
        assert request.json == {
            'contractor_id': {'dbid': 'zxcvb', 'uuid': 'qwerty'},
            'positions': [
                {
                    'accuracy': 2.0,
                    'direction': 238,
                    'lat': 55.740404,
                    'lon': 37.513276,
                    'speed': 16,
                    'source': 'Verified',
                    'unix_timestamp': 1568198535000,
                },
            ],
        }
        return mockserver.make_response(status=200)

    driver_authorizer.set_client_session(
        app_family, 'zxcvb', 'asdfg', 'qwerty',
    )
    params = {'session': 'asdfg', 'db': 'zxcvb'}
    data_args = {
        'driverId': 'qwerty',
        'lat': 55.740404,
        'lon': 37.513276,
        'angel': 238.4,
        'speed': 58,
        'isBad': 'false',
        'status': 1,
        'orderStatus': 0,
        'accuracy': 2.0,
        'timeGpsOrig': 1568388595484,
        'timeSystemOrig': 1568388595484,
        'timeSystemSync': 1568388595484,
    }
    data = urllib.parse.urlencode(data_args)
    response = await taxi_yagr_adv.post(
        '/driver/position/store', params=params, data=data, headers=headers,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}
    data = await testpoint_clid.wait_call()

    # Check here for clid empty field
    assert 'clid=\t' in data['data']['tskv']

    # check after all processing is done
    assert mock_pipeline.times_called == 1


@pytest.mark.now('2019-09-11T13:42:15+0300')
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 60,
        'past_boundary': 7200,
    },
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 100,
        'driver_v1_position_store': 100,
        'driver_v1_position_store_extra_data': 100,
    },
)
async def test_driver_position_store_empty(
        taxi_yagr_adv, driver_authorizer, testpoint, mockserver,
):
    @testpoint('write-positions-to-yt')
    def testpoint_clid(data):
        pass

    @mockserver.json_handler('/yagr/pipeline/taxi/position/store')
    def mock_pipeline(request):
        assert (
            abs(request.json['positions'][0]['speed'] - 16.111111) < 0.000001
        )
        request.json['positions'][0]['speed'] = 16
        assert request.json == {
            'contractor_id': {'dbid': 'zxcvb', 'uuid': 'qwerty'},
            'positions': [
                {
                    'accuracy': 2.0,
                    'direction': 238,
                    'lat': 0,
                    'lon': 0,
                    'speed': 16,
                    'source': 'Verified',
                    'unix_timestamp': 1568198535000,
                },
            ],
        }
        return mockserver.make_response(status=200)

    driver_authorizer.set_session('zxcvb', 'asdfg', 'qwerty')
    params = {'session': 'asdfg', 'db': 'zxcvb'}
    data_args = {
        'driverId': 'qwerty',
        'lat': 0.0,
        'lon': 0.0,
        'angel': 238.4,
        'speed': 58,
        'isBad': 'false',
        'status': 1,
        'orderStatus': 0,
        'accuracy': 2.0,
        'timeGpsOrig': 1568388595484,
        'timeSystemOrig': 1568388595484,
        'timeSystemSync': 1568388595484,
    }
    data = urllib.parse.urlencode(data_args)
    response = await taxi_yagr_adv.post(
        '/driver/position/store', params=params, data=data,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}
    await testpoint_clid.wait_call()

    assert mock_pipeline.times_called == 1


@pytest.mark.config(
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 100,
        'driver_v1_position_store': 100,
        'driver_v1_position_store_extra_data': 100,
    },
)
async def test_driver_position_store_400(taxi_yagr_adv, driver_authorizer):
    driver_authorizer.set_session('zxcvb', 'asdfg', 'qwerty')

    params = {
        'session': 'asdfg',
        'db': 'zxcvb',
        'driverId': 'qwerty',
        'lat': 55.740404,
        'lon': 37.513276,
        'speed': 58,
        'isBad': 'false',
        'status': 1,
        'orderStatus': 0,
        'accuracy': 2.0,
    }
    response = await taxi_yagr_adv.post(
        '/driver/position/store', params=params,
    )
    assert response.status_code == 400


@pytest.mark.now('2019-09-11T13:42:15+0000')  # 1568209335
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': True,
        'future_boundary': 30,
        'past_boundary': 30,
    },
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 100,
        'driver_v1_position_store': 100,
        'driver_v1_position_store_extra_data': 100,
    },
)
async def test_driver_position_store_discard_too_old_points(
        taxi_yagr_adv, driver_authorizer, testpoint, mockserver,
):
    """ YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP prevents yagr from
    fixing timestamps of positions that are too old, e.g. 2 hours and more.
    This test tests that when enabled, timestamps are indeed left unfixed
    """

    @testpoint('write-positions-to-yt')
    def testpoint_clid(data):
        pass

    @mockserver.json_handler('/yagr/pipeline/taxi/position/store')
    def mock_pipeline(request):
        assert request.json['positions'][0]['unix_timestamp'] in [
            1568209330000,
            1568209335000,
        ]
        request.json['positions'][0]['unix_timestamp'] = 1568209330000
        assert request.json == {
            'contractor_id': {'dbid': 'zxcvb', 'uuid': 'qwerty'},
            'positions': [
                {
                    'accuracy': 2.0,
                    'direction': 238,
                    'lat': 55.0,
                    'lon': 37.0,
                    'source': 'Verified',
                    'unix_timestamp': 1568209330000,
                },
            ],
        }
        return mockserver.make_response(status=200)

    driver_authorizer.set_session('zxcvb', 'asdfg', 'qwerty')
    params = {'session': 'asdfg', 'db': 'zxcvb'}

    def get_data(timestamp_in_seconds):
        data_args = {
            'driverId': 'qwerty',
            'lat': 55.0,
            'lon': 37.0,
            'angel': 238.4,
            'speed': -7,  # must be replaced with -1
            'isBad': 'false',
            'status': 1,
            'orderStatus': 0,
            'accuracy': 2.0,
            'timeGpsOrig': timestamp_in_seconds * 1000,  # in milliseconds!
            'timeSystemOrig': timestamp_in_seconds * 1000,  # in milliseconds!
            'timeSystemSync': timestamp_in_seconds * 1000,  # in milliseconds!
        }

        return urllib.parse.urlencode(data_args)

    # test 1 - send data slightly in the past - within past_boundary
    # It should arrive with unchanged timestamp
    response = await taxi_yagr_adv.post(
        '/driver/position/store', params=params, data=get_data(1568209330),
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}
    await testpoint_clid.wait_call()

    # test 2 - send data slightly in the future - within future_boundary
    # It should arrive with timestamp equal to now
    response = await taxi_yagr_adv.post(
        '/driver/position/store', params=params, data=get_data(1568209340),
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}
    await testpoint_clid.wait_call()

    # test 3 - send data way outside of past_boundary
    # It should be discarded
    response = await taxi_yagr_adv.post(
        '/driver/position/store', params=params, data=get_data(1568209300),
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    # test 4 - send data way outside of future_boundary
    # It should be discarded
    response = await taxi_yagr_adv.post(
        '/driver/position/store', params=params, data=get_data(1568209370),
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    assert mock_pipeline.times_called == 2


@pytest.mark.now('2019-09-11T13:42:15+0000')  # UTC zone here!
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 10,
        'past_boundary': 10,
    },
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 100,
        'driver_v1_position_store': 100,
        'driver_v1_position_store_extra_data': 100,
    },
)
async def test_driver_position_store_dont_discard_old_points(
        taxi_yagr_adv, driver_authorizer, testpoint, mockserver,
):
    """ YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP prevents yagr from
    fixing timestamps of positions that are too old, e.g. 2 hours and more.
    This test tests that when this setting is disabled, its timestamps
    are properly fixed
    """

    @testpoint('write-positions-to-yt')
    def testpoint_clid(data):
        pass

    @mockserver.json_handler('/yagr/pipeline/taxi/position/store')
    def mock_pipeline(request):
        assert request.json == {
            'contractor_id': {'dbid': 'zxcvb', 'uuid': 'qwerty'},
            'positions': [
                {
                    'accuracy': 2.0,
                    'direction': 238,
                    'lat': 55.0,
                    'lon': 37.0,
                    'source': 'Verified',
                    'unix_timestamp': 1568209335000,
                },
            ],
        }
        return mockserver.make_response(status=200)

    driver_authorizer.set_session('zxcvb', 'asdfg', 'qwerty')
    params = {'session': 'asdfg', 'db': 'zxcvb'}
    data_args = {
        'driverId': 'qwerty',
        'lat': 55.0,
        'lon': 37.0,
        'angel': 238.4,
        'speed': -7,  # must be replaced with -1
        'isBad': 'false',
        'status': 1,
        'orderStatus': 0,
        'accuracy': 2.0,
        'timeGpsOrig': 5000,  # in milliseconds!
        'timeSystemOrig': 5000,  # in milliseconds!
        'timeSystemSync': 5000,  # in milliseconds!
    }
    data = urllib.parse.urlencode(data_args)
    response = await taxi_yagr_adv.post(
        '/driver/position/store', params=params, data=data,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}
    await testpoint_clid.wait_call()

    assert mock_pipeline.times_called == 1


@pytest.mark.parametrize(
    'position_incomplete_data',
    [
        # missing lon
        {'lat': 55.740404, 'angel': 238.4, 'speed': 58},
        # missing angle
        {'lat': 55.740404, 'lon': 37.513276, 'speed': 58},
        # missing speed
        {'lat': 55.740404, 'lon': 37.513276, 'angel': 238.4},
    ],
)
@pytest.mark.config(
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 100,
        'driver_v1_position_store': 100,
        'driver_v1_position_store_extra_data': 100,
    },
)
async def test_driver_position_store_invalid_position_schema(
        taxi_yagr_adv, driver_authorizer, position_incomplete_data, mockserver,
):
    @mockserver.json_handler('/yagr/pipeline/taxi/position/store')
    def mock_pipeline(request):
        pass

    headers = {'User-Agent': 'Taximeter 9.1 (1234)'}
    app_family = 'taximeter'

    driver_authorizer.set_client_session(
        app_family, 'zxcvb', 'asdfg', 'qwerty',
    )
    params = {'session': 'asdfg', 'db': 'zxcvb'}
    data_args = {
        'driverId': 'qwerty',
        'isBad': 'false',
        'status': 1,
        'orderStatus': 0,
        'accuracy': 2.0,
        'timeGpsOrig': 1568388595484,
        'timeSystemOrig': 1568388595484,
        'timeSystemSync': 1568388595484,
    }
    data_args.update(position_incomplete_data)
    data = urllib.parse.urlencode(data_args)
    response = await taxi_yagr_adv.post(
        '/driver/position/store', params=params, data=data, headers=headers,
    )
    assert response.status_code == 400
    assert mock_pipeline.times_called == 0


@pytest.mark.now('2019-09-11T13:42:15+0000')  # UTC zone here!
@pytest.mark.config(
    YAGR_DISCARD_POINTS_WITH_BAD_TIMESTAMP={
        'enabled': False,
        'future_boundary': 10,
        'past_boundary': 10,
    },
    YAGR_TRANSFER_TAXI_HANDLERS={
        'driver_position_store': 100,
        'driver_v1_position_store': 100,
        'driver_v1_position_store_extra_data': 100,
    },
)
@pytest.mark.config(YAGR_SIGNAL_V2_FROM_OLD_STORE_PERCENT=100)
@pytest.mark.config(YAGR_MULTIPOS_YT_LOG_DRIVER_PERCENT=100)
async def test_driver_position_store_aggregated_data_signal_v2(
        taxi_yagr_adv, driver_authorizer, testpoint, mockserver,
):
    @testpoint('write-position-from-source-to-yt')
    def testpoint_position_from_source(data):
        pass

    @mockserver.json_handler('/yagr/pipeline/taxi/position/store')
    def mock_pipeline(request):
        assert abs(request.json['positions'][0]['speed'] - 2.777777) < 0.000001
        request.json['positions'][0]['speed'] = 16
        assert request.json == {
            'contractor_id': {'dbid': 'zxcvb1', 'uuid': 'qwerty'},
            'positions': [
                {
                    'accuracy': 2.0,
                    'direction': 238,
                    'lat': 55.0,
                    'lon': 37.0,
                    'speed': 16,
                    'source': 'Verified',
                    'unix_timestamp': 1568209335000,
                },
            ],
        }
        return mockserver.make_response(status=200)

    driver_authorizer.set_session('zxcvb1', 'asdfg', 'qwerty')
    params = {'session': 'asdfg', 'db': 'zxcvb1'}
    data_args = {
        'driverId': 'qwerty',
        'lat': 55.0,
        'lon': 37.0,
        'angel': 238.4,
        'speed': 10,
        'aggregated_data': (
            'p=55.833934,37.631911,1908013264,13.0,121.97385509,1587471462786,'
            '25.25,null,passive,false,false;'
            'l=55.901420,37.580165,1908008694,140.0,0.0,1587471458215,null,'
            'null,lbs-wifi,false,false;'
            'n=55.834,37.632,1908013262,542.0,null,1587471462784,null,'
            'null,network,false,false;'
            'gps=55.833934,37.6319115,1908013264,13.0,121.97385509,'
            '1587471462786,0.0,123,gps,false,false'
        ),
        'isBad': 'false',
        'status': 1,
        'orderStatus': 0,
        'accuracy': 2.0,
        'timeGpsOrig': 5000,  # in milliseconds!
        'timeSystemOrig': 5000,  # in milliseconds!
        'timeSystemSync': 5000,  # in milliseconds!
    }
    data = urllib.parse.urlencode(data_args)
    response = await taxi_yagr_adv.post(
        '/driver/position/store', params=params, data=data,
    )
    assert response.status_code == 200
    check_polling_header(response.headers['X-Polling-Power-Policy'])
    assert response.json() == {}

    assert mock_pipeline.times_called == 1
    # Just pass position to pipeline handler and don't write aggregated data to yt
    assert testpoint_position_from_source.times_called == 0
