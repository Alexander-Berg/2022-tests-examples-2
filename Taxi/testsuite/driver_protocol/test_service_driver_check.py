import json

import pytest


@pytest.fixture
def reposition(mockserver):
    class Handlers:
        @mockserver.json_handler('/reposition_api/v1/service/state')
        def mock_state(request):
            return {'has_session': False}

    return Handlers()


@pytest.fixture(name='driver-weariness', autouse=True)
def _mock_driver_weariness(mockserver, load_json):
    @mockserver.json_handler('/driver_weariness/v1/driver-weariness')
    def _driver_weariness(request):
        _id = json.loads(request.get_data())['unique_driver_id']
        cache = load_json('driver_weariness_cache.json')
        if _id not in cache:
            return mockserver.make_response({}, status=404)
        return cache[_id]


def test_bad_request(taxi_driver_protocol):
    response = taxi_driver_protocol.get('service/driver/check')
    assert response.status_code == 400

    response = taxi_driver_protocol.get('service/driver/check?db=1488')
    assert response.status_code == 400

    response = taxi_driver_protocol.get(
        'service/driver/check?db=&driver=driverSS',
    )
    assert response.status_code == 400

    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS'
        '&chain=yes&onlycard=false',
    )
    assert response.status_code == 400


def test_park_not_found(taxi_driver_protocol):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=12345&driver=driverSS',
    )
    assert response.status_code == 404


@pytest.mark.redis_store(['hset', '1488:STATUS_DRIVERS', 'driverSS', '2'])
def test_default_ok(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS',
    )
    assert response.status_code == 200
    assert response.json() == load_json('Ok.json')


@pytest.mark.redis_store(
    ['hset', 'Aggregator:YandexClid', '1369', 'agg1369'],
    ['sadd', 'Aggregator:Disable', 'agg1369'],
    ['hset', '1488:STATUS_DRIVERS', 'driverSS', '2'],
)
def test_aggregator_disabled(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS',
    )
    assert response.status_code == 200
    assert response.json() == load_json('ParkAggregatorDisabled.json')


@pytest.mark.redis_store(
    ['hset', 'Aggregator:YandexClid', '1369', 'agg1369'],
    ['hset', 'Aggregator:Balance:agg1369', '1488', '-200'],
    ['hset', 'Aggregator:agg1369', 'BalanceLimitAlert', '-100'],
    ['hset', '1488:STATUS_DRIVERS', 'driverSS', '2'],
)
def test_aggregator_debt(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS',
    )
    assert response.status_code == 200
    assert response.json() == load_json('ParkAggregatorDebt.json')


@pytest.mark.redis_store(
    ['hset', 'Aggregator:YandexClid', '1369', 'agg1369'],
    ['hset', 'Aggregator:Balance:agg1369', '1488', '-200'],
    ['hset', '1488:STATUS_DRIVERS', 'driverSS', '2'],
)
def test_aggregator_no_limit_info(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS',
    )
    assert response.status_code == 200
    assert response.json() == load_json('Ok.json')


@pytest.mark.redis_store(['hset', '1488:STATUS_DRIVERS', 'driverSS', '1'])
def test_driver_status_busy(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS',
    )
    assert response.status_code == 200
    assert response.json() == load_json('DriverStatusNotFree.json')


@pytest.mark.redis_store(['hset', '1369:STATUS_DRIVERS', 'Vasya', '2'])
def test_selfemployed_block(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1369&driver=Vasya',
    )
    assert response.status_code == 200
    assert response.json() == {
        'can_take_orders': False,
        'reasons': [
            {
                'code': 'SelfemployedBlock',
                'message': (
                    'Driver stoped being selfemployed or revoked '
                    'permissions in nalog app'
                ),
            },
        ],
    }


@pytest.mark.redis_store(['hset', '1488:STATUS_DRIVERS', 'driverSS', '2'])
def test_driver_inactive_reposition(
        taxi_driver_protocol, mockserver, load_json,
):
    @mockserver.json_handler('/reposition_api/v1/service/state')
    def mock_state(request):
        return {'has_session': True, 'active': False}

    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS',
    )
    assert response.status_code == 200
    assert response.json() == load_json('InactiveReposition.json')


@pytest.mark.redis_store(['hset', '1488:STATUS_DRIVERS', 'driverSS', '2'])
def test_driver_active_reposition(taxi_driver_protocol, mockserver, load_json):
    @mockserver.json_handler('/reposition_api/v1/service/state')
    def mock_state(request):
        return {'has_session': True, 'active': True}

    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS',
    )
    assert response.status_code == 200
    assert response.json() == load_json('Ok.json')


@pytest.mark.redis_store(['hset', '1488:STATUS_DRIVERS', 'driverSS', '1'])
def test_driver_active_reposition_busy(
        taxi_driver_protocol, mockserver, load_json,
):
    @mockserver.json_handler('/reposition_api/v1/service/state')
    def mock_state(request):
        return {'has_session': True, 'active': True}

    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS',
    )
    assert response.status_code == 200
    assert response.json() == load_json('DriverStatusNotFree.json')


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS', '2'],
    ['sadd', '1488:STATUS_DRIVERS:INTEGRATOR', 'driverSS'],
)
def test_driver_in_status_integrator(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS',
    )
    assert response.status_code == 200
    assert response.json() == load_json('DriverStatusNotFree.json')


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS', '2'],
    [
        'sadd',
        'Order:SetCar:Driver:Reserv:Items1488:driverSS',
        'order0',
        'order1',
    ],
    [
        'hmset',
        'Order:SetCar:Items:1488',
        {
            'order0': json.dumps({'A': 'B'}),
            'order1': json.dumps({'chain': 'anything'}),
        },
    ],
)
def test_driver_order_chain_begin(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS',
    )
    assert response.status_code == 200
    assert response.json() == load_json('DriverOrderChainBegin.json')


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS', '2'],
    ['sadd', 'Order:SetCar:Driver:Reserv:Items1488:driverSS', 'order0'],
    [
        'hmset',
        'Order:SetCar:Items:1488',
        {
            'order0': json.dumps(
                {
                    'date_view': '2017-10-24T01:23:45Z',
                    'provider': 123,
                    'id': 'ID',
                },
            ),
        },
    ],
)
def test_driver_has_order_in_work(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS',
    )
    assert response.status_code == 200
    assert response.json() == load_json('DriverHasOrderInWork.json')


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS', '3'],
    ['sadd', 'Order:SetCar:Driver:Reserv:Items1488:driverSS', 'order0'],
    [
        'hmset',
        'Order:SetCar:Items:1488',
        {'order0': json.dumps({'chain': 'anything', 'id': 'id0'})},
    ],
    ['hmset', 'Order:RequestConfirm:Items:1488', {'order0': '20'}],
)
def test_driver_too_many_chains(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS&chain=true',
    )
    assert response.status_code == 200
    assert response.json() == load_json('DriverTooManyChains.json')


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'NoLimit', '2'],
    ['hset', '1488:STATUS_DRIVERS', 'NulLimit', '2'],
    ['hset', '777:STATUS_DRIVERS', 'NegLimit', '2'],
)
def test_no_balance_limit(taxi_driver_protocol, load_json):
    ok_json = load_json('Ok.json')
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=NoLimit',
    )
    assert response.status_code == 200
    assert response.json() == ok_json

    ok_json = load_json('Ok.json')
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=NulLimit',
    )
    assert response.status_code == 200
    assert response.json() == ok_json

    response = taxi_driver_protocol.get(
        'service/driver/check?db=777&driver=NegLimit',
    )
    assert response.status_code == 200
    assert response.json() == ok_json


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'Low', '2'],
    ['hset', '777:STATUS_DRIVERS', 'driverFF', '2'],
)
def test_driver_balance(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=Low',
    )
    assert response.status_code == 200
    assert response.json() == load_json('DriverBalanceDebt.json')

    response = taxi_driver_protocol.get(
        'service/driver/check?db=777&driver=driverFF',
    )
    assert response.status_code == 200
    assert response.json() == load_json('Ok.json')


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS', '2'],
    [
        'hset',
        'Blacklist:Cars',
        'XY234230',
        json.dumps({'Description': 'ХАХА', 'Reason': 'Ho-Ho'}),
    ],
)
def test_car_blacklisted(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS',
    )
    assert response.status_code == 200
    assert response.json() == load_json('DriverCarBlacklisted.json')


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS', '2'],
    [
        'hset',
        'Blacklist:Drivers',
        'M8209289',
        json.dumps(
            {
                'Description': 'Поддержка Собчак',
                'Reason': 'Doggy-style rules!',
            },
        ),
    ],
)
def test_driver_blacklisted(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS',
    )
    assert response.status_code == 200
    assert response.json() == load_json('DriverLicenseBlacklisted.json')


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS', '2'],
    [
        'hset',
        'Driver:TimeBlock:Items',
        'driverSS',
        json.dumps({'msg': 'Далеко посылаете техподдержку'}),
    ],
)
def test_timeblock(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS',
    )
    assert response.status_code == 200
    assert response.json() == load_json('DriverTimeBlock.json')


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS', '2'],
    ['hset', '777:STATUS_DRIVERS', 'MrNobody', '2'],
)
def test_taximeter(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS',
    )
    assert response.status_code == 200
    assert response.json() == load_json('Ok.json')

    response = taxi_driver_protocol.get(
        'service/driver/check?db=777&driver=MrNobody',
    )
    assert response.status_code == 200
    assert response.json() == load_json('DriverTaximeterVersionDisabled.json')


@pytest.mark.redis_store()
def test_many_reasons(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=anonim',
    )
    assert response.status_code == 200
    assert response.json() == load_json('ManyReasons.json')


@pytest.mark.now('2018-01-21T23:59:00Z')
@pytest.mark.config(
    DRIVER_WEARINESS_BLOCK_DRIVERS_ENABLED={'__default__': True},
)
@pytest.mark.redis_store(['hset', '1488:STATUS_DRIVERS', 'driverSS1', '2'])
def test_tired_by_hours(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS1',
    )
    assert response.status_code == 200
    assert response.json() == load_json('DriverTiredByHoursExceed.json')


@pytest.mark.now('2018-01-21T23:59:00Z')
@pytest.mark.config(
    DRIVER_WEARINESS_BLOCK_DRIVERS_ENABLED={
        '__default__': False,
        'Москва': True,
    },
)
@pytest.mark.redis_store(['hset', '1488:STATUS_DRIVERS', 'driverSS2', '2'])
def test_tired_by_no_long_rest(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS2',
    )
    assert response.status_code == 200
    assert response.json() == load_json('DriverTiredByNoLongRest.json')


@pytest.mark.now('2018-01-21T23:59:00Z')
@pytest.mark.config(
    DRIVER_WEARINESS_BLOCK_DRIVERS_ENABLED={
        '__default__': False,
        'Москва': False,
    },
)
@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS2', '2'],
    ['hset', 'Aggregator:YandexClid', '1369', 'agg1369'],
)
def test_tired_not_enabled_city(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS2',
    )
    assert response.status_code == 200
    assert response.json() == load_json('Ok.json')


@pytest.mark.now('2018-01-21T23:59:00Z')
@pytest.mark.config(
    DRIVER_WEARINESS_BLOCK_DRIVERS_ENABLED={'__default__': True},
)
@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS3', '2'],
    ['hset', 'Aggregator:YandexClid', '1369', 'agg1369'],
)
def test_tired_block_time_not_finished(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS3',
    )
    assert response.status_code == 200
    assert response.json() == load_json('Ok.json')


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driver', '2'],
    [
        'hset',
        'Blacklist:Drivers',
        'M8209289',
        json.dumps(
            {
                'Description': 'Поддержка Собчак',
                'Reason': 'Doggy-style rules!',
            },
        ),
    ],
)
@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
def test_deduplicate_reasons(
        taxi_driver_protocol, mockserver, load_json, tracker,
):
    tracker.set_position('1369_driver', 0, 55.732618, 37.588119)

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/DriverLicenseBlacklisted.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.get(
        'service/driver/check',
        params={'db': '1488', 'driver': 'driver', 'complete_check': True},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('DriverLicenseBlacklisted.json')


@pytest.mark.redis_store(['hset', '1488:STATUS_DRIVERS', 'driver', '2'])
@pytest.mark.parametrize(
    'error_code',
    [
        'DriverGradeBlock',
        'DriverInvalidExam',
        'DriverNoClasses',
        'DriverNoPermit',
        'DriverTiredHoursExceed',
        'DriverTiredNoLongRest',
        'Ok',
        'ParkDeactivated',
    ],
)
@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
def test_tracker_drivercheck(
        taxi_driver_protocol, mockserver, error_code, load_json, tracker,
):

    tracker.set_position('1369_driver', 0, 55.732618, 37.588119)

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/' + error_code + '.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.get(
        'service/driver/check',
        params={'db': '1488', 'driver': 'driver', 'complete_check': True},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'complete_response/' + error_code + '.json',
    )


@pytest.mark.redis_store(['hset', '1488:STATUS_DRIVERS', 'driver', '2'])
@pytest.mark.parametrize(
    'error_code',
    [
        'DriverInvalidExam',
        'DriverNoClasses',
        'DriverNoPermit',
        'ParkDeactivated',
        'DriverTiredHoursExceed',
        'DriverTiredNoLongRest',
        'Ok',
    ],
)
@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
@pytest.mark.experiments3(
    filename='experiments3_service_driver_check_lookup_mode.json',
)
def test_candidates_drivercheck(
        taxi_driver_protocol, mockserver, error_code, load_json, tracker,
):

    tracker.set_position('1369_driver', 0, 55.732618, 37.588119)

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/' + error_code + '.json')

    @mockserver.json_handler('/candidates/satisfy')
    def mock_satisfy(request):
        return load_json('candidates/' + error_code + '.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.get(
        'service/driver/check',
        params={'db': '1488', 'driver': 'driver', 'complete_check': True},
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'complete_response/' + error_code + '.json',
    )


@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
def test_driver_not_found(taxi_driver_protocol, mockserver, load_json):
    @mockserver.json_handler('/tracker/position')
    def mock_driver_position(request):
        return mockserver.make_response('', 404)

    response = taxi_driver_protocol.get(
        '/service/driver/check',
        params={'db': '1488', 'driver': 'driver', 'complete_check': True},
    )

    assert response.status_code == 404


@pytest.mark.config(USE_DRIVER_TRACKSTORY_DP_PERCENT=100)
@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
def test_driver_not_found_driver_trackstory(
        taxi_driver_protocol, mockserver, load_json,
):
    @mockserver.json_handler('/driver_trackstory/position')
    def mock_driver_position(request):
        return mockserver.make_response('{"message": "1231"}', 404)

    response = taxi_driver_protocol.get(
        '/service/driver/check',
        params={'db': '1488', 'driver': 'driver', 'complete_check': True},
    )

    assert response.status_code == 404


@pytest.mark.redis_store(['hset', '1488:STATUS_DRIVERS', 'driver', '2'])
@pytest.mark.parametrize(
    'point,error_code,status_code',
    [
        ({'lon': 37.588119, 'lat': 55.732618}, 'Ok', 200),
        ({'lon': 39.588119, 'lat': 65.732618}, 'DriverGeoareaNotFound', 200),
        ({'lon': 239.588119, 'lat': 65.732618}, 'BadRequest', 400),
    ],
)
@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
def test_external_driver_coordinate(
        taxi_driver_protocol,
        mockserver,
        load_json,
        point,
        error_code,
        status_code,
):
    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.get(
        'service/driver/check',
        params={
            'db': '1488',
            'driver': 'driver',
            'complete_check': True,
            'longitude': point['lon'],
            'latitude': point['lat'],
        },
        headers={'Accept-Language': 'ru'},
    )
    assert response.status_code == status_code
    assert response.json() == load_json(
        'complete_response/' + error_code + '.json',
    )


@pytest.mark.config(DRIVER_CHECK_NEW_BLOCKLIST_ENABLED=True)
@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS', '2'],
    [
        'hset',
        'Blacklist:Cars',
        'XY234230',
        json.dumps({'Description': 'ХАХА', 'Reason': 'Ho-Ho'}),
    ],
)
def test_new_blocklist_enabled(taxi_driver_protocol, load_json):
    response = taxi_driver_protocol.get(
        'service/driver/check?db=1488&driver=driverSS',
    )
    assert response.status_code == 200
    assert response.json() == load_json('Ok.json')
