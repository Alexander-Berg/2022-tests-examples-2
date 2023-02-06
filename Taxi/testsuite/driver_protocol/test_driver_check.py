import json

import pytest

ACCEPT_LANGUAGE = 'Accept-Language'
USER_AGENT = 'User-Agent'

HEADERS = {ACCEPT_LANGUAGE: 'ru', USER_AGENT: 'Taximeter 8.31 (456)'}


@pytest.fixture
def reposition(mockserver):
    class Handlers:
        @mockserver.json_handler('/reposition_api/v1/service/state')
        def mock_state(request):
            assert request.headers['Content-Type'] == 'application/json'
            return {'has_session': False}

    return Handlers()


@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
def test_authorization(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    response = taxi_driver_protocol.post('driver/check')
    assert response.status_code == 401

    response = taxi_driver_protocol.post('driver/check?db=abc&session=qwerty')
    assert response.status_code == 401

    response = taxi_driver_protocol.post('driver/check?db=1488&session=qwerty')
    assert response.status_code != 401

    response = taxi_driver_protocol.post(
        'driver/check', params={'db': '1488', 'session': 'qwerty'},
    )
    assert response.status_code != 401


@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
def test_input_point(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty', headers=HEADERS,
    )
    assert response.status_code == 400

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        headers=HEADERS,
        json={'point': {'lon': 37.588119, 'lat': 'Bad lat'}},
    )
    assert response.status_code == 400

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        headers=HEADERS,
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
    )
    assert response.status_code == 200


@pytest.mark.now('2018-09-30T12:30:00+0300')
@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
@pytest.mark.parametrize(
    'error_code',
    [
        'DriverGradeBlock',
        'DriverInvalidExam',
        'DriverNoClasses',
        'DriverNoPermit',
        'ParkDeactivated',
        'DriverTiredHoursExceed',
        'DriverTiredNoLongRest',
        'Ok',
    ],
)
def test_tracker_drivercheck(
        taxi_driver_protocol,
        mockserver,
        error_code,
        load_json,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/' + error_code + '.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('response/' + error_code + '.json')


@pytest.mark.now('2018-09-30T12:30:00+0300')
@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
@pytest.mark.experiments3(
    filename='experiments3_driver_check_lookup_mode.json',
)
@pytest.mark.parametrize(
    'error_code',
    [
        'DriverInvalidExam',
        'DriverNoClasses',
        'DriverNoPermit',
        'ParkDeactivated',
        'DriverTiredHoursExceed',
        'DriverTiredNoLongRest',
        'DriverMetricsActivityBlock',
        'Ok',
    ],
)
def test_candidates_drivercheck(
        taxi_driver_protocol,
        mockserver,
        error_code,
        load_json,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/' + error_code + '.json')

    @mockserver.json_handler('/candidates/satisfy')
    def mock_satisfy(request):
        return load_json('candidates/' + error_code + '.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('response/' + error_code + '.json')


@pytest.mark.now('2018-09-30T12:30:00+0300')
@pytest.mark.config(
    TAXIMETER_QC_SETTINGS={'sync_mode': 'off'}, USE_NO_PERMIT_RESTRICTION=True,
)
@pytest.mark.parametrize('error_code', ['DriverNoPermit'])
def test_tracker_drivercheck_restriction(
        taxi_driver_protocol,
        mockserver,
        error_code,
        load_json,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/' + error_code + '.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'response/' + error_code + 'Restriction.json',
    )


@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
@pytest.mark.parametrize(
    'error_code, result',
    [
        ('DriverMetricsActivityBlock', 'DriverMetricsActivityBlock'),
        ('DriverMetricsActionsBlock', 'DriverMetricsActionsBlock'),
    ],
)
def test_tracker_drivercheck_dm(
        taxi_driver_protocol,
        mockserver,
        error_code,
        result,
        load_json,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/' + error_code + '.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('response/' + result + '.json')


@pytest.mark.config(
    DRIVER_TAGS_DIAGNOSTICS_DESCRIPTION={
        'moscow': {
            'bad_car': {'tanker_key': 'BadCar', 'type': 'blocked'},
            'silver_crown': {
                'image_key': 'some_key',
                'tanker_key': 'HighPriority',
                'type': 'high_priority',
            },
            'salon_gryaz': {
                'tanker_key': 'LowPriority',
                'type': 'low_priority',
            },
        },
    },
    TAXIMETER_QC_SETTINGS={'sync_mode': 'off'},
)
@pytest.mark.parametrize(
    'response, result',
    [
        ('Ok', 'Ok'),
        ('DriverTagsConfigMissedTag', 'Ok'),
        ('DriverTagsHighPriority', 'DriverTagsHighPriority'),
        ('DriverTagsLowPriority', 'DriverTagsLowPriority'),
        ('DriverTagsBlock', 'DriverTagsBlock'),
    ],
)
def test_notify_by_tags_in_drivercheck(
        taxi_driver_protocol,
        mockserver,
        response,
        result,
        load_json,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/' + response + '.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('response/' + result + '.json')


@pytest.mark.config(
    DRIVER_TAGS_DIAGNOSTICS_DESCRIPTION={
        'moscow': {
            'bad_car': {'tanker_key': 'BadCar', 'type': 'blocked'},
            'silver_crown': {
                'image_key': 'some_key',
                'tanker_key': 'HighPriority',
                'type': 'high_priority',
            },
            'salon_gryaz': {
                'tanker_key': 'LowPriority',
                'type': 'low_priority',
            },
        },
    },
    TAXIMETER_QC_SETTINGS={'sync_mode': 'dry-run'},
)
@pytest.mark.parametrize(
    'response, result',
    [
        ('DriverTagsHighPriority', 'DriverTagsHighPriority'),
        ('DriverTagsLowPriority', 'DriverTagsLowPriority'),
        ('DriverTagsBlock', 'DriverTagsBlock'),
    ],
)
def test_multiple_restrictions(
        taxi_driver_protocol,
        mockserver,
        response,
        result,
        load_json,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/' + response + '.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json('qc/dkk-dkvu.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )

    assert response.status_code == 200
    assert response.json() == load_json('response/' + result + 'Multiple.json')


@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
def test_selfemployed_block(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1369', 'qwerty', 'Vasya')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/DriverNoPermit.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1369&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    expected = {
        'code': 'SelfemployedBlock',
        'message': 'Станьте самозанятым',
        'title': 'Вы не самозанятый',
    }
    assert not response_json['can_take_orders']
    assert expected in response_json['reasons']
    assert len(response_json['restrictions']) == 1
    assert response_json['restrictions'][0]['code'] == 'DriverNoCar'
    assert response_json['restrictions'][0]['title'] == 'Нет авто'
    assert (
        response_json['restrictions'][0]['actions']['primary']['url']
        == 'taximeter://screen/about_driver?screen_type=park'
    )


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driver', '2'],
    ['hset', 'Aggregator:YandexClid', '1369', 'agg1369'],
    ['hset', 'Aggregator:Balance:agg1369', '1488', '-200'],
    ['hset', 'Aggregator:agg1369', 'BalanceLimitAlert', '-100'],
)
@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
def test_aggregator(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('response/ParkAggregatorDebt.json')


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'Low', '1'],
    ['hset', '1488:STATUS_DRIVERS', 'MrNobody', '1'],
    ['hset', '1488:STATUS_DRIVERS', 'MrNobodyTwo', '1'],
)
@pytest.mark.config(
    TAXIMETER_QC_SETTINGS={'sync_mode': 'off'},
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'min': '9.00',
            'current': '9.00',
            'disabled': ['9.74'],
            'feature_support': {},
        },
    },
)
def test_taximeter(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'abcdef', 'Low')
    driver_authorizer_service.set_session('1488', 'ghijkl', 'MrNobody')
    driver_authorizer_service.set_session('1488', 'rewq', 'MrNobodyTwo')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=abcdef',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    response_json = response.json()
    expected_json = load_json('response/DriverBalanceDebt.json')
    assert response_json['can_take_orders'] == expected_json['can_take_orders']
    assert response_json['reasons'] == expected_json['reasons']
    assert len(response_json['restrictions']) == 1
    assert response_json['restrictions'][0]['code'] == 'DriverNoCar'
    assert response_json['restrictions'][0]['title'] == 'Нет авто'
    assert (
        response_json['restrictions'][0]['actions']['primary']['url']
        == 'taximeter://screen/about_driver?screen_type=park'
    )

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=ghijkl',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 404

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=rewq',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers={ACCEPT_LANGUAGE: 'ru', USER_AGENT: 'Taximeter 9.74 (1234)'},
    )
    assert response.status_code == 200
    response_json = response.json()
    expected_json = load_json('response/DriverTaximeterVersionDisabled.json')
    assert response_json['can_take_orders'] == expected_json['can_take_orders']
    assert response_json['reasons'] == expected_json['reasons']
    assert len(response_json['restrictions']) == 1
    assert response_json['restrictions'][0]['code'] == 'DriverNoCar'
    assert response_json['restrictions'][0]['title'] == 'Нет авто'
    assert (
        response_json['restrictions'][0]['actions']['primary']['url']
        == 'taximeter://screen/about_driver?screen_type=park'
    )


@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
def test_geoarea_not_found(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 11.111111, 'lat': 11.111111}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('response/DriverGeoareaNotFound.json')


@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
def test_yandex_not_provider(taxi_driver_protocol, driver_authorizer_service):
    driver_authorizer_service.set_session('777', 'qwerty', 'NoProviders')

    response = taxi_driver_protocol.post(
        'driver/check?db=777&session=qwerty',
        json={'point': {'lon': 11.111111, 'lat': 11.111111}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json()['can_take_orders']


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS', '1'],
    [
        'hset',
        'Blacklist:Cars',
        'XY234230',
        json.dumps({'Description': 'car_blacklisted'}),
    ],
)
@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
def test_driver_car_blacklisted_in_taximeter_redis(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'response/RedisDriverCarBlacklisted.json',
    )


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS', '1'],
    [
        'hset',
        'Blacklist:Drivers',
        'M8209289',
        json.dumps({'Description': 'license_blacklisted'}),
    ],
)
@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
def test_driver_license_blacklisted_in_taximeter_redis(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'response/RedisDriverLicenseBlacklisted.json',
    )


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS', '1'],
    [
        'hset',
        'Blacklist:Drivers',
        'M8209289',
        json.dumps(
            {
                'Description': 'license_blacklisted',
                'Reason': 'license_blacklisted',
            },
        ),
    ],
)
@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
def test_driver_license_blacklisted_in_taximeter_redis_with_reason(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'response/RedisDriverLicenseBlacklistedWithReason.json',
    )


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS', '1'],
    [
        'hset',
        'Driver:TimeBlock:Items',
        'driverSS',
        json.dumps({'msg': 'timeblock'}),
    ],
)
@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
def test_driver_timeblock_in_taximeter_redis(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('response/RedisDriverTimeblock.json')


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS', '1'],
    [
        'hset',
        'Blacklist:Cars',
        'XY234230',
        json.dumps({'Description': 'car_blacklisted'}),
    ],
)
@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
def test_deduplicate_reasons(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Two reasons with same code: from taximeter and from tracker
    No attribute till
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/DriverCarBlacklisted.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'response/RedisDriverCarBlacklisted.json',
    )


@pytest.mark.parametrize(
    'reason,error',
    [
        ('bad_signature', 'DriverLicenseSignatureBlockBadClient'),
        ('fake_gps', 'DriverLicenseSignatureBlockBadDevice'),
        ('emulator', 'DriverLicenseSignatureBlockBadDevice'),
        ('hook', 'DriverLicenseSignatureBlockBadDevice'),
        ('gps_switch', 'DriverLicenseSignatureBlockAbuseDevice'),
        ('net_switch', 'DriverLicenseSignatureBlockAbuseDevice'),
        ('plane_switch', 'DriverLicenseSignatureBlockAbuseDevice'),
        ('driver_not_found', 'DriverLicenseSignatureBlockBadClient'),
    ],
)
@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
def test_fraud_drivercheck(
        taxi_driver_protocol,
        mockserver,
        reason,
        error,
        load_json,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return {
            'antifraud': {'reason': reason},
            'classes': [{'allowed': True, 'class': 'econom'}],
        }

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json('response/' + error + '.json')


@pytest.mark.config(
    QC_INFO_URLS={'__default__': '', 'dkk': 'dkk_url', 'dkvu': 'dkvu_url'},
)
@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'current': '8.30',
            'disabled': [],
            'feature_support': {
                'activity_reuse_order_details': '8.92',
                'chair_categories': '8.55',
                'driver_support_zendesk': '9.24',
                'gzip_push': '9.99',
                'json_geoareas': '8.30',
                'qc_default': '8.10',
                'subvention': '8.33',
            },
            'min': '8.30',
        },
        'taximeter-uber': {
            'feature_support': {'use_uber_scheme_over_taximeter': '8.35'},
        },
    },
)
@pytest.mark.parametrize(
    'user_agent',
    [
        'Taximeter 8.31 (1234)',
        'Taximeter-uber 8.31 (1234)',
        'Taximeter-uber 8.35 (12345)',
    ],
)
@pytest.mark.parametrize(
    'qc_status,resp',
    [
        (
            'qc/dkvu_assessor_reject.json',
            'response/RestrictionsDkvuAssessorReject.json',
        ),
        ('qc/dkvu_need_pass.json', 'response/RestrictionsDkvuNeedPass.json'),
        ('qc/dkvu_next_pass.json', 'response/RestrictionsDkvuNextPass.json'),
    ],
)
@pytest.mark.now('2018-09-30T12:30:00+0300')
def test_restrictions_one_exam(
        taxi_driver_protocol,
        mockserver,
        load_json,
        qc_status,
        resp,
        driver_authorizer_service,
        user_agent,
):
    """
    Test checks:
    1) logic & response for needed check and next check
    2) will be send only restrictions for active experiments
    (response from api/state/check contains info about `dkk` and `dkvu`,
    but only active experiment for `dkvu`, so response will contain
    only `dkvu`)
    """
    app_type = 'uberdriver' if 'uber' in user_agent else 'taximeter'
    driver_authorizer_service.set_client_session(
        app_type, '1488', 'qwerty', 'driver',
    )

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json(qc_status)

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers={USER_AGENT: user_agent, ACCEPT_LANGUAGE: 'ru'},
    )
    assert response.status_code == 200, response.text
    actual_json = response.json()
    expected_json = load_json(resp)

    replace_to_uber = '8.35' in user_agent and 'uber' in user_agent
    if replace_to_uber:
        new_json = json.dumps(expected_json).replace(
            'taximeter://', 'taximeteruber://',
        )
        expected_json = json.loads(new_json)
    assert actual_json == expected_json


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'feature_support': {'qc_default': '8.10', 'qc_dkvu': '9.10'},
        },
    },
    QC_INFO_URLS={'__default__': '', 'dkk': 'dkk_url', 'dkvu': 'dkvu_url'},
)
@pytest.mark.parametrize(
    'qc_status,resp',
    [
        (
            'qc/dkvu_assessor_reject.json',
            'response/RestrictionsDkvuAssessorRejectUnsupported.json',
        ),
        (
            'qc/dkvu_need_pass.json',
            'response/RestrictionsDkvuNeedPassUnsupported.json',
        ),
        ('qc/dkvu_next_pass.json', 'response/RestrictionsDkvuNextPass.json'),
    ],
)
@pytest.mark.now('2018-09-30T12:30:00+0300')
def test_restrictions_one_exam_unsupported(
        taxi_driver_protocol,
        mockserver,
        load_json,
        qc_status,
        resp,
        driver_authorizer_service,
):
    """
    Test checks:
    1) logic & response for needed check and next check
    2) will be send only restrictions for active experiments
    (response from api/state/check contains info about `dkk` and `dkvu`,
    but only active experiment for `dkvu`, so response will contain
    only `dkvu`)
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json(qc_status)

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json(resp)


@pytest.mark.driver_experiments('cached_qc_cpp', 'compare_cached_qc_cpp')
@pytest.mark.config(
    QC_INFO_URLS={'__default__': '', 'dkk': 'dkk_url', 'dkvu': 'dkvu_url'},
    QC_CPP_MIN_TAXIMETER_VERSION='8.30',
)
@pytest.mark.parametrize(
    'qc_status,resp,qc_wrong_status',
    [
        (
            'qc/dkvu_assessor_reject.json',
            'response/RestrictionsDkvuAssessorReject.json',
            'qc/dkvu_need_pass.json',
        ),
        (
            'qc/dkvu_need_pass.json',
            'response/RestrictionsDkvuNeedPass.json',
            'qc/dkvu_assessor_reject.json',
        ),
        (
            'qc/dkvu_next_pass.json',
            'response/RestrictionsDkvuNextPass.json',
            'qc/dkvu_need_pass.json',
        ),
    ],
)
@pytest.mark.now('2018-09-30T12:30:00+0300')
def test_restrictions_one_exam_qc_cpp(
        taxi_driver_protocol,
        mockserver,
        load_json,
        qc_status,
        resp,
        qc_wrong_status,
        config,
        driver_authorizer_service,
):
    """
    Test checks:
    1) logic & response for needed check and next check
    2) will be send only restrictions for active experiments
    (response from api/state/check contains info about `dkk` and `dkvu`,
    but only active experiment for `dkvu`, so response will contain
    only `dkvu`)
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/cpp-qcs/api/v1/state')
    def mock_qc_cpp_status(request):
        return load_json(qc_status)

    config.set(QC_CPP_URL=mockserver.url('cpp-qcs'))

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json(qc_wrong_status)

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json(resp)

    # check exception on QC
    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status_exc(request):
        return ''

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json(resp)

    # check exception on QC-cpp
    @mockserver.json_handler('/cpp-qcs/api/v1/state')
    def mock_qc_cpp_status_exc(request):
        return ''

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )

    assert response.status_code == 200
    content = response.json()
    assert content == {'can_take_orders': True, 'reasons': []}


def test_restrictions_two_exam(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Test checks:
    1) 'can_take_orders': false, when one of restriction's level is ERROR
    2) descripton according to pending status of dkvu
    (used tanker key ...description.pending)
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json('qc/dkk-dkvu.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/RestrictionsDkkDkvu.json')


@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'dry-run'})
def test_restrictions_as_warning(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Test checks:
    1) 'can_take_orders': true, when no one of restriction's level is ERROR
    2) dkvu on Warning level due to experiment
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json('qc/dkk-dkvu.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/RestrictionsDkkDkvuAsWarnings.json')


@pytest.mark.config(QC_CANDIDATES_BLOCK_SKIP_EXAMS=['dkvu'])
def test_tariff_qc_exam(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Test checks:
    1) 'can_take_orders': true, when no one of restriction's level is ERROR
    2) dkvu on Warning level due to experiment
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json('qc/dkk-dkvu.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/RestrictionsDkkDkvuAsWarnings.json')


@pytest.mark.config(QC_CANDIDATES_BLOCK_SKIP_EXAMS=['dkvu'])
@pytest.mark.experiments3(
    name='treat_qc_tariffs_as_error',
    consumers=['driver_protocol/driver_check'],
    match={
        'consumers': ['driver_protocol/driver_check'],
        'predicate': {'type': 'true'},
        'enabled': True,
    },
    clauses=[],
    default_value={'exams': ['dkvu']},
)
def test_treat_tariff_qc_exam_as_error(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Test checks:
    1) 'can_take_orders': true, when no one of restriction's level is ERROR
    2) dkvu on Warning level due to experiment
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json('qc/dkk-dkvu.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/RestrictionsDkkDkvu.json')


@pytest.mark.now('2020-03-24T12:00:00.00+0000')
@pytest.mark.config(
    TAXIMETER_QC_SETTINGS=dict(sync_mode='on'),
    TAXIMETER_QC_COUNTRIES={
        '__default__': dict(block=[], visible=[], disable=[]),
        'covid19': dict(block=['rus'], visible=[], disable=[]),
        'covid19_info': dict(block=['rus'], visible=[], disable=[]),
    },
)
@pytest.mark.parametrize(
    'check_time, expected_response',
    [
        (None, 'RestrictionsCovid19'),
        ('2020-03-23T23:59:59.00+0000', 'RestrictionsCovid19'),
        ('2020-03-24T02:59:59.00+0000', 'RestrictionsCovid19Info'),
    ],
)
def test_covid19_restrictions(
        taxi_driver_protocol,
        mockserver,
        redis_store,
        load_json,
        driver_authorizer_service,
        check_time,
        expected_response,
):
    """
    Driver will retrieve covid19, covid19_info restrictions
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    if check_time:
        redis_store.set('COVID19:1488:driver', check_time)

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if request.args['type'] == 'driver':
            return load_json('qc/dkk-dkvu.json')
        return load_json('qc/car-state.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json(f'response/{expected_response}.json')


@pytest.mark.now('2020-03-24T12:00:00.00+0000')
@pytest.mark.config(
    TAXIMETER_QC_SETTINGS=dict(sync_mode='on'),
    QC_CHECK_CONFIG_3_0_ENABLE=True,
    TAXIMETER_QC_COUNTRIES={
        '__default__': dict(block=[], visible=[], disable=[]),
        'covid19': dict(block=[], visible=['rus'], disable=[]),
        'covid19_info': dict(block=[], visible=['rus'], disable=[]),
    },
)
@pytest.mark.experiments3(
    filename='experiments3_qc_exam_enabled_country_replacement1.json',
)
@pytest.mark.parametrize(
    'check_time, expected_response',
    [
        (None, 'RestrictionsCovid19'),
        ('2020-03-23T23:59:59.00+0000', 'RestrictionsCovid19'),
        ('2020-03-24T02:59:59.00+0000', 'RestrictionsCovid19Info'),
    ],
)
def test_covid19_restrictions_config3_0(
        taxi_driver_protocol,
        mockserver,
        redis_store,
        load_json,
        driver_authorizer_service,
        check_time,
        expected_response,
):
    """
    Driver will retrieve covid19, covid19_info restrictions
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    if check_time:
        redis_store.set('COVID19:1488:driver', check_time)

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if request.args['type'] == 'driver':
            return load_json('qc/dkk-dkvu.json')
        return load_json('qc/car-state.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json(f'response/{expected_response}.json')


@pytest.mark.config(
    TAXIMETER_QC_SETTINGS=dict(sync_mode='on'),
    TAXIMETER_QC_COUNTRIES={
        '__default__': {'block': [], 'visible': [], 'disable': []},
        'dkk': {'block': ['rus'], 'visible': [], 'disable': []},
        'dkvu': {'block': ['rus'], 'visible': [], 'disable': []},
        'branding': {'block': [], 'visible': ['rus'], 'disable': []},
    },
)
def test_restrictions_sync_dkb_on(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Driver will retrieve dkb restrictions
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if request.args['type'] == 'driver':
            return load_json('qc/dkk-dkvu.json')
        return load_json('qc/car-state.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/RestrictionsDkkDkvuDkb.json')


@pytest.mark.config(
    TAXIMETER_QC_SETTINGS=dict(sync_mode='on'),
    QC_CHECK_CONFIG_3_0_ENABLE=True,
    TAXIMETER_QC_COUNTRIES={
        '__default__': {'block': [], 'visible': ['rus'], 'disable': []},
    },
)
@pytest.mark.experiments3(
    filename='experiments3_qc_exam_enabled_country_replacement2.json',
)
def test_restrictions_sync_dkb_on_config3_0(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Driver will retrieve dkb restrictions
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if request.args['type'] == 'driver':
            return load_json('qc/dkk-dkvu.json')
        return load_json('qc/car-state.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/RestrictionsDkkDkvuDkb.json')


@pytest.mark.config(
    TAXIMETER_QC_SETTINGS=dict(sync_mode='on'),
    TAXIMETER_QC_DRIVERS={
        '__default__': {'block': [], 'visible': [], 'disable': []},
        'branding': {'block': [], 'visible': ['driver'], 'disable': []},
    },
)
def test_restrictions_sync_dkb_dry_run_with_exp(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Test checks:
    Driver will retrieve dkb restrictions
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if request.args['type'] == 'driver':
            return load_json('qc/dkk-dkvu.json')
        return load_json('qc/car-state.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/RestrictionsDkkDkvuDkb.json')


@pytest.mark.config(
    TAXIMETER_QC_SETTINGS=dict(sync_mode='on'),
    QC_CHECK_CONFIG_3_0_ENABLE=True,
    TAXIMETER_QC_DRIVERS={
        '__default__': {'block': [], 'visible': ['driver'], 'disable': []},
    },
)
@pytest.mark.experiments3(
    filename='experiments3_qc_exam_enabled_driver_replacement.json',
)
def test_restrictions_sync_dkb_dry_run_with_exp_config3_0(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Test checks:
    Driver will retrieve dkb restrictions
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if request.args['type'] == 'driver':
            return load_json('qc/dkk-dkvu.json')
        return load_json('qc/car-state.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    print(content)
    assert content == load_json('response/RestrictionsDkkDkvuDkb.json')


@pytest.mark.config(
    TAXIMETER_QC_SETTINGS={'sync_mode': 'on', 'sync_dkb': 'dry-run'},
)
def test_restrictions_sync_dkb_dry_run_no_exp(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Test checks:
    Driver won't retrieve dkb restrictions on dry-run if experiment not enabled
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if request.args['type'] == 'driver':
            return load_json('qc/dkk-dkvu.json')
        return load_json('qc/car-state.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/RestrictionsDkkDkvu.json')


@pytest.mark.config(
    TAXIMETER_QC_SETTINGS=dict(sync_mode='on'),
    TAXIMETER_QC_COUNTRIES={
        '__default__': {'block': [], 'visible': [], 'disable': []},
        'dkk': {'block': ['rus'], 'visible': [], 'disable': []},
        'dkvu': {'block': ['rus'], 'visible': [], 'disable': []},
        'sts': {'block': ['rus'], 'visible': [], 'disable': []},
    },
)
def test_restrictions_sync_sts_on(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Driver will retrieve sts restrictions
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if request.args['type'] == 'driver':
            return load_json('qc/dkk-dkvu.json')
        return load_json('qc/car-state.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/RestrictionsDkkDkvuSts.json')


@pytest.mark.config(
    TAXIMETER_QC_SETTINGS=dict(sync_mode='on'),
    TAXIMETER_QC_COUNTRIES={
        '__default__': {'block': [], 'visible': ['rus'], 'disable': []},
    },
    QC_CHECK_CONFIG_3_0_ENABLE=True,
)
@pytest.mark.experiments3(
    filename='experiments3_qc_exam_enabled_country_replacement3.json',
)
def test_restrictions_sync_sts_on_config3_0(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Driver will retrieve sts restrictions
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if request.args['type'] == 'driver':
            return load_json('qc/dkk-dkvu.json')
        return load_json('qc/car-state.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/RestrictionsDkkDkvuSts.json')


@pytest.mark.config(
    TAXIMETER_QC_SETTINGS=dict(sync_mode='on'),
    TAXIMETER_QC_COUNTRIES=dict(
        __default__=dict(block=[], visible=[], disable=[]),
        dkk=dict(block=['rus', 'kaz'], visible=[], disable=[]),
        dkvu=dict(block=['rus', 'kaz'], visible=[], disable=[]),
        sts=dict(block=['rus', 'kaz'], visible=[], disable=[]),
    ),
    TAXIMETER_QC_TAGS=dict(
        __default__=dict(block=[], visible=[], disable=[]),
        sts=dict(block=[], visible=[], disable=['skip_qc_sts_tag']),
    ),
)
@pytest.mark.driver_tags_match(
    dbid='1488', uuid='driver', tags=['skip_qc_sts_tag'],
)
@pytest.mark.parametrize(
    'tags_enabled, park, driver, expected_response',
    [
        (True, '1488', 'driver', 'RestrictionsDkkDkvu.json'),
        (False, '1488', 'driver', 'RestrictionsDkkDkvuSts.json'),
        (True, '1489', 'driverSSSS', 'RestrictionsDkkDkvuSts.json'),
    ],
)
def test_skip_restrictions_by_tag(
        taxi_driver_protocol,
        mockserver,
        load_json,
        driver_authorizer_service,
        config,
        tags_enabled,
        park,
        driver,
        expected_response,
):
    config.set_values(dict(QC_CHECK_TAGS_ENABLED=tags_enabled))

    driver_authorizer_service.set_session(park, 'qwerty', driver)

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if request.args['type'] == 'driver':
            return load_json('qc/dkk-dkvu.json')
        return load_json('qc/car-state.json')

    response = taxi_driver_protocol.post(
        f'driver/check?db={park}&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/' + expected_response)


on_filename = 'experiments3_qc_exam_enabled_country_replacement_tags_on.json'
off_filename = 'experiments3_qc_exam_enabled_country_replacement_tags_off.json'


@pytest.mark.config(
    TAXIMETER_QC_SETTINGS=dict(sync_mode='on'),
    QC_CHECK_CONFIG_3_0_ENABLE=True,
    TAXIMETER_QC_COUNTRIES={
        '__default__': {'block': [], 'visible': ['rus', 'kaz'], 'disable': []},
    },
)
@pytest.mark.driver_tags_match(
    dbid='1488', uuid='driver', tags=['skip_qc_sts_tag'],
)
@pytest.mark.parametrize(
    'tags_enabled, park, driver, expected_response',
    [
        pytest.param(
            True,
            '1488',
            'driver',
            'RestrictionsDkkDkvu.json',
            marks=(pytest.mark.experiments3(filename=on_filename)),
        ),
        pytest.param(
            False,
            '1488',
            'driver',
            'RestrictionsDkkDkvuSts.json',
            marks=(pytest.mark.experiments3(filename=off_filename)),
        ),
        pytest.param(
            True,
            '1489',
            'driverSSSS',
            'RestrictionsDkkDkvuSts.json',
            marks=(pytest.mark.experiments3(filename=on_filename)),
        ),
    ],
)
def test_skip_restrictions_by_tag_config3_0(
        taxi_driver_protocol,
        mockserver,
        load_json,
        driver_authorizer_service,
        config,
        tags_enabled,
        park,
        driver,
        expected_response,
):
    driver_authorizer_service.set_session(park, 'qwerty', driver)

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if request.args['type'] == 'driver':
            return load_json('qc/dkk-dkvu.json')
        return load_json('qc/car-state.json')

    response = taxi_driver_protocol.post(
        f'driver/check?db={park}&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/' + expected_response)


@pytest.mark.config(
    TAXIMETER_QC_SETTINGS=dict(sync_mode='on'),
    TAXIMETER_QC_PARKS={
        '__default__': {'block': [], 'visible': [], 'disable': []},
        'sts': {'block': ['1488'], 'visible': [], 'disable': []},
    },
)
@pytest.mark.driver_experiments('use_car_sts_parks')
def test_restrictions_sync_sts_dry_run_with_exp(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Test checks:
    Driver will retrieve sts restrictions
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if request.args['type'] == 'driver':
            return load_json('qc/dkk-dkvu.json')
        return load_json('qc/car-state.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/RestrictionsDkkDkvuSts.json')


@pytest.mark.config(
    TAXIMETER_QC_SETTINGS=dict(sync_mode='on'),
    QC_CHECK_CONFIG_3_0_ENABLE=True,
    TAXIMETER_QC_PARKS={
        '__default__': {'block': [], 'visible': ['1488'], 'disable': []},
    },
)
@pytest.mark.experiments3(
    filename='experiments3_qc_exam_enabled_park_replacement.json',
)
@pytest.mark.driver_experiments('use_car_sts_parks')
def test_restrictions_sync_sts_dry_run_with_exp_config3_0(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Test checks:
    Driver will retrieve sts restrictions
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if request.args['type'] == 'driver':
            return load_json('qc/dkk-dkvu.json')
        return load_json('qc/car-state.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/RestrictionsDkkDkvuSts.json')


@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'on'})
def test_restrictions_sync_sts_dry_run_no_exp(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Test checks:
    Driver won't retrieve sts restrictions on dry-run if experiment not enabled
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if request.args['type'] == 'driver':
            return load_json('qc/dkk-dkvu.json')
        return load_json('qc/car-state.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/RestrictionsDkkDkvu.json')


@pytest.mark.config(
    TAXIMETER_QC_SETTINGS={'sync_mode': 'on', 'sync_dkk': 'on'},
)
def test_restrictions_sync_dkk_on(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Driver will retrieve dkk restrictions from car-dkk
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if request.args['type'] == 'driver':
            return load_json('qc/dkk-dkvu.json')
        return load_json('qc/car-state.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/RestrictionsCarDkkDkvu.json')


@pytest.mark.config(
    TAXIMETER_QC_SETTINGS={'sync_mode': 'on', 'sync_dkk': 'dry-run'},
)
@pytest.mark.driver_experiments('use_car_dkk')
def test_restrictions_sync_dkk_dry_run_with_exp(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Test checks:
    Driver will retrieve dkk-car restrictions
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if request.args['type'] == 'driver':
            return load_json('qc/dkk-dkvu.json')
        return load_json('qc/car-state.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/RestrictionsCarDkkDkvu.json')


@pytest.mark.config(
    TAXIMETER_QC_SETTINGS={'sync_mode': 'on', 'sync_dkk': 'dry-run'},
)
def test_restrictions_sync_dkk_dry_run_no_exp(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Test checks:
    Driver won't retrieve car-dkk restrictions on dry-run
        if experiment not enabled
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if request.args['type'] == 'driver':
            return load_json('qc/dkk-dkvu.json')
        return load_json('qc/car-state.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/RestrictionsDkkDkvu.json')


def test_restrictions_dkvu_pass_dkk_not(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Test checks:
    1) 'can_take_orders': false, when one of restriction's level is ERROR
    2) descripton according to pending status of dkvu
    (used tanker key ...description.pending)
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json('qc/dkk_need_pass.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json(
        'response/RestrictionsDkvuPassedDkkNeedPass.json',
    )


@pytest.mark.config(
    QC_CHECK_SUPPORTED_EXAMS=['rqc'], QC_CHECK_ENTITY_EXAMS={'car': ['rqc']},
)
def test_restrictions_rqc_business_off(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Test checks:
    1) 'can_take_orders': false, when one of restriction's level is ERROR
    2) descripton according to pending status of rqc
    (used tanker key ...description.pending)
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json('qc/rqc_business_off.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/RestrictionsRqcBusinessOff.json')


@pytest.mark.now('2018-08-07T08:40:00.000000Z')
def test_restrictions_dkk_ok_has_pass_reason(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Test checks:
    1) descripton according to ok status of dkk with remarks
    (used tanker key ...description.description_ok_next_pass_reason)
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json('qc/dkk-reason.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json('response/RestrictionsDkkNextPassReason.json')


def test_fallback_translation(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    Test checks:
    1) driver has 'fa' locale
    2) use park locale 'ro', when no translation for driver locale
    3) use country locale 'ka', when no translation for park locale
    4) otherwise try steps 1-3 for default key
    5) otherwise use default fallback locale (now ru (Russian))

    If translation is empty (see fallback in l10n) - error
    (see case with exams.default.description)
    """
    driver_authorizer_service.set_session('1234', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json('qc/dkk_need_pass.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1234&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers={ACCEPT_LANGUAGE: 'fa', USER_AGENT: HEADERS[USER_AGENT]},
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json(
        'response/RestrictionsFallbackTranslation.json',
    )


@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
@pytest.mark.now('2018-09-30T12:30:00+0300')
@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS1', '1'],
    [
        'hset',
        'Blacklist:Cars',
        'XY234230',
        json.dumps({'Description': 'car_blacklisted'}),
    ],
)
def test_driver_car_blacklisted_in_taximeter_redis_on_restrictions(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    driverSS1 has Taximeter version 8.63 >=
    QC_RESTRICTIONS_MIN_TAXIMETER_VERSION
    (see it in dbdrivers.json in default directory).
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS1')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers={ACCEPT_LANGUAGE: 'ru', USER_AGENT: 'Taximeter 8.63 (456)'},
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'response/RedisDriverCarBlacklistedWithRestrictions.json',
    )


@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
@pytest.mark.now('2018-09-30T12:30:00+0300')
@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS1', '1'],
    [
        'hset',
        'Blacklist:Cars',
        'XY234230:1488',
        json.dumps({'Description': 'car_blacklisted'}),
    ],
)
def test_driver_car_blacklisted_in_taximeter_redis_by_park(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS1')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers={ACCEPT_LANGUAGE: 'ru', USER_AGENT: 'Taximeter 8.63 (456)'},
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'response/RedisDriverCarBlacklistedWithRestrictions.json',
    )


@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
@pytest.mark.now('2018-09-30T12:30:00+0300')
@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS1', '1'],
    [
        'hset',
        'Blacklist:Cars',
        'XY234230:1588',
        json.dumps({'Description': 'car_blacklisted'}),
    ],
)
def test_driver_car_not_blacklisted_in_taximeter_redis_by_park(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS1')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers={ACCEPT_LANGUAGE: 'ru', USER_AGENT: 'Taximeter 8.63 (456)'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('response/Ok.json')


@pytest.mark.now('2018-09-30T12:30:00+0300')
@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS', '1'],
    [
        'hset',
        'Blacklist:Cars',
        'XY234230',
        json.dumps({'Description': 'car_blacklisted'}),
    ],
)
def test_driver_car_blacklisted_in_taximeter_redis_old_version(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json('qc/dkk-dkvu.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'response/RedisDriverCarBlacklisted.json',
    )


@pytest.mark.now('2018-09-30T12:30:00+0300')
@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS1', '1'],
    [
        'hset',
        'Blacklist:Cars',
        'XY234230',
        json.dumps(
            {'Description': 'car_blacklisted', 'Reason': 'car_blacklisted'},
        ),
    ],
)
def test_driver_car_blacklisted_in_taximeter_redis_restrictions_reason(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS1')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json('qc/dkk-dkvu.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers={ACCEPT_LANGUAGE: 'ru', USER_AGENT: 'Taximeter 8.63 (456)'},
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'response/RedisDriverCarBlacklistedWithReason.json',
    )


@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
@pytest.mark.now('2018-09-30T12:30:00+0300')
@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS1', '1'],
    [
        'hset',
        'Blacklist:Drivers',
        'M8209289',
        json.dumps(
            {
                'Description': 'license_blacklisted',
                'Reason': 'license_blacklisted',
            },
        ),
    ],
)
def test_driver_license_blacklisted_in_taximeter_redis_on_restrictions(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    driverSS1 has Taximeter version 8.63 >=
    QC_RESTRICTIONS_MIN_TAXIMETER_VERSION
    (see it in dbdrivers.json in default directory).
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS1')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers={ACCEPT_LANGUAGE: 'ru', USER_AGENT: 'Taximeter 8.63 (456)'},
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'response/RedisDriverLicenseBlacklistedWithRestrictions.json',
    )


@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
@pytest.mark.now('2018-09-30T12:30:00+0300')
@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS1', '1'],
    [
        'hset',
        'Blacklist:Drivers',
        'M8209289:1488',
        json.dumps(
            {
                'Description': 'license_blacklisted',
                'Reason': 'license_blacklisted',
            },
        ),
    ],
)
def test_driver_license_blacklisted_in_taximeter_redis_by_park(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    driverSS1 has Taximeter version 8.63 >=
    QC_RESTRICTIONS_MIN_TAXIMETER_VERSION
    (see it in dbdrivers.json in default directory).
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS1')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers={ACCEPT_LANGUAGE: 'ru', USER_AGENT: 'Taximeter 8.63 (456)'},
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'response/RedisDriverLicenseBlacklistedWithRestrictions.json',
    )


@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
@pytest.mark.now('2018-09-30T12:30:00+0300')
@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driverSS1', '1'],
    [
        'hset',
        'Blacklist:Drivers',
        'M8209289:1588',
        json.dumps(
            {
                'Description': 'license_blacklisted',
                'Reason': 'license_blacklisted',
            },
        ),
    ],
)
def test_driver_license_not_blacklisted_in_taximeter_redis_by_park(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    driverSS1 has Taximeter version 8.63 >=
    QC_RESTRICTIONS_MIN_TAXIMETER_VERSION
    (see it in dbdrivers.json in default directory).
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS1')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers={ACCEPT_LANGUAGE: 'ru', USER_AGENT: 'Taximeter 8.63 (456)'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('response/Ok.json')


@pytest.mark.now('2018-09-30T12:30:00+0300')
@pytest.mark.redis_store(
    ['hset', '1489:STATUS_DRIVERS', 'driverSSS', '1'],
    [
        'hset',
        'Blacklist:Drivers',
        'M8209289',
        json.dumps(
            {
                'Description': 'license_blacklisted',
                'Reason': 'license_blacklisted',
            },
        ),
    ],
)
def test_driver_license_blacklisted_fullscreen_icon_min_ver(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    driverSSS has Taximeter version 8.67 >=
    QC_FULLSCREEN_ICON_MIN_TAXIMETER_VERSION
    (see it in dbdrivers.json in default directory).
    """
    driver_authorizer_service.set_session('1489', 'qwerty', 'driverSSS')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json('qc/dkk-dkvu.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1489&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers={ACCEPT_LANGUAGE: 'ru', USER_AGENT: 'Taximeter 8.67 (456)'},
    )
    assert response.status_code == 200
    assert response.json() == load_json(
        'response/RedisDriverLicenseBlacklistedFullscreenIconMinVer.json',
    )


@pytest.mark.now('2018-09-30T12:30:00+0300')
@pytest.mark.parametrize(
    'collection, key, value, expected_response',
    [
        # Temporary driver without reason
        (
            'Blacklist:Drivers',
            'M8209289',
            {
                'Description': 'license_blacklisted',
                'TillDate': '2018-10-02T14:05:00Z',
            },
            '8_63_DriverLicenseBlacklistedTemp.json',
        ),
        (
            'Blacklist:Drivers',
            'M8209289',
            {
                'Description': 'license_blacklisted',
                'TillDate': '2018-09-30T09:30:00Z',
            },
            '8_63_DriverLicenseBlacklistedTempLate.json',
        ),
        # Temporary driver with reason
        (
            'Blacklist:Drivers',
            'M8209289',
            {
                'Description': 'license_blacklisted',
                'TillDate': '2018-10-02T14:05:00Z',
                'Reason': 'Ну захотелось',
            },
            '8_63_DriverLicenseBlacklistedTempWithReason.json',
        ),
        (
            'Blacklist:Drivers',
            'M8209289',
            {
                'Description': 'license_blacklisted',
                'TillDate': '2018-09-30T09:30:00Z',
                'Reason': 'Ну захотелось',
            },
            '8_63_DriverLicenseBlacklistedTempWithReasonLate.json',
        ),
        # Temporary driver expired
        (
            'Blacklist:Drivers',
            'M8209289',
            {
                'Description': 'license_blacklisted',
                'TillDate': '2017-04-03T14:05:00Z',
                'Reason': 'Ну захотелось',
            },
            'Ok.json',
        ),
        # Assessor driver blacklisted
        (
            'Blacklist:Drivers',
            'M8209289',
            {
                'Db': 'accessor',
                'Description': 'license_blacklisted',
                'Message': {
                    'keys': [
                        'dkvu_blacklist_reason_fake_license',
                        'dkvu_blacklist_reason_bad_photo',
                    ],
                },
            },
            '8_63_DriverLicenseBlacklistedDkvu.json',
        ),
        # Support on special language
        (
            'Blacklist:Drivers',
            'M8209289',
            {
                'Description': 'license_blacklisted',
                'Message': {'text': 'you are an idiot', 'locale': 'en'},
            },
            '8_63_DriverLicenseBlacklistedSupportEnglish.json',
        ),
        # Temporary car without reason
        (
            'Blacklist:Cars',
            'XY234230',
            {
                'Description': 'car_blacklisted',
                'TillDate': '2018-10-02T14:05:00Z',
            },
            '8_63_DriverCarBlacklistedTemp.json',
        ),
        (
            'Blacklist:Cars',
            'XY234230',
            {
                'Description': 'car_blacklisted',
                'TillDate': '2018-09-30T09:30:00Z',
            },
            '8_63_DriverCarBlacklistedTempLate.json',
        ),
        # Temporary car with reason
        (
            'Blacklist:Cars',
            'XY234230',
            {
                'Description': 'car_blacklisted',
                'TillDate': '2018-10-02T14:05:00Z',
                'Reason': 'Ну захотелось',
            },
            '8_63_DriverCarBlacklistedTempWithReason.json',
        ),
        (
            'Blacklist:Cars',
            'XY234230',
            {
                'Description': 'car_blacklisted',
                'TillDate': '2018-09-30T09:30:00Z',
                'Reason': 'Ну захотелось',
            },
            '8_63_DriverCarBlacklistedTempWithReasonLate.json',
        ),
        # Temporary car expired
        (
            'Blacklist:Cars',
            'XY234230',
            {
                'Description': 'car_blacklisted',
                'TillDate': '2017-04-03T14:05:00Z',
                'Reason': 'Ну захотелось',
            },
            'Ok.json',
        ),
        # Assessor car blacklisted
        (
            'Blacklist:Cars',
            'XY234230',
            {
                'Db': 'accessor',
                'Description': 'car_blacklisted',
                'Message': {
                    'keys': [
                        'dkk_blacklist_reason_car_defect',
                        'dkk_blacklist_reason_bad_photo',
                    ],
                },
            },
            '8_63_DriverCarBlacklistedDkk.json',
        ),
        # Support on special language
        (
            'Blacklist:Cars',
            'XY234230',
            {
                'Description': 'car_blacklisted',
                'Message': {'text': 'you are an idiot', 'locale': 'en'},
            },
            '8_63_DriverCarBlacklistedSupportEnglish.json',
        ),
    ],
)
def test_redis_blacklist_8_63(
        taxi_driver_protocol,
        mockserver,
        redis_store,
        collection,
        key,
        value,
        expected_response,
        load_json,
        driver_authorizer_service,
):
    """
    driverSS1 has Taximeter version 8.63 >=
    QC_RESTRICTIONS_MIN_TAXIMETER_VERSION
    (see it in dbdrivers.json in default directory).
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS1')
    redis_store.hset(collection, key, json.dumps(value))

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json('qc/empty_dkk-dkvu.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers={ACCEPT_LANGUAGE: 'ru', USER_AGENT: 'Taximeter 8.63 (456)'},
    )

    assert response.status_code == 200
    assert response.json() == load_json('response/' + expected_response)


@pytest.mark.redis_store(
    [
        'hset',
        'Driver:TimeBlock:Items',
        'driverSS1',
        json.dumps({'msg': 'timeblock'}),
    ],
)
@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
def test_driver_timeblock_in_taximeter_redis_8_63(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
    driverSS1 has Taximeter version 8.63 >=
    QC_RESTRICTIONS_MIN_TAXIMETER_VERSION
    (see it in dbdrivers.json in default directory).
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS1')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers={ACCEPT_LANGUAGE: 'ru', USER_AGENT: 'Taximeter 8.63 (456)'},
    )
    assert response.status_code == 200
    assert response.json() == load_json('response/RedisDriverTimeblock.json')


def test_restrictions_exams_car_documents_icons_min_version(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    """
     driver_8.68 has Taximeter version 8.68 >=
     QC_DKK_DKVU_ICONS_MIN_TAXIMETER_VERSION
     (see it in dbdrivers.json in default directory).
     """
    driver_authorizer_service.set_session('1489', 'qwerty', 'driver_8.68')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json('qc/dkk-dkvu.json')

    response = taxi_driver_protocol.post(
        'driver/check?db=1489&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers={ACCEPT_LANGUAGE: 'ru', USER_AGENT: 'Taximeter 8.68 (456)'},
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json(
        'response/RestrictionsDkkDkvu_Client_8_68.json',
    )


@pytest.mark.config(
    GDPR_COUNTRIES=['lt', 'fr'],
    NEED_ACCEPT_GDPR=True,
    TAXIMETER_QC_SETTINGS={'sync_mode': 'off'},
)
@pytest.mark.translations(
    taximeter_messages={
        'gdpr.url.title': {'ru': 'default url title'},
        'gdpr.url.title.lt': {'ru': 'Lithuania url title'},
        'gdpr.url.content': {'ru': 'default url content'},
        'gdpr.url.content.lt': {'ru': 'Lithuania url content'},
    },
)
@pytest.mark.parametrize(
    'lat, lon, expected_title, expected_content',
    [
        # russia
        (55.971204, 37.413673, None, None),
        # france
        (48.856614, 2.3522219, 'default url title', 'default url content'),
        # lithuania
        (54.6871555, 25.2796514, 'lt url title', 'lt url content'),
    ],
)
def test_gdpr(
        lat,
        lon,
        expected_title,
        expected_content,
        taxi_driver_protocol,
        mockserver,
        load_json,
        driver_authorizer_service,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driverSS')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': lon, 'lat': lat}},
        headers=HEADERS,
    )
    assert response.status_code == 200
    response = response.json()
    if expected_title is None:
        assert 'policies_params' not in response
    else:
        policy = response['policies'][0]
        policy['url_title'] == expected_title
        policy['url_content'] == expected_content


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driver', '1'],
    [
        'hset',
        'Driver:TimeBlock:Items',
        'driver',
        json.dumps({'msg': 'timeblock'}),
    ],
)
@pytest.mark.parametrize(
    'mode', ['dkvu_error', 'dkk_pending', 'dkk_passed', 'dkk_need_pass'],
)
@pytest.mark.now('2018-08-08T12:30:00+0300')
def test_error_restriction_on_dkk_pending_no_experiments(
        taxi_driver_protocol,
        mockserver,
        load_json,
        mode,
        driver_authorizer_service,
):
    """
    Test crutch for TAXIMETERBACK-4713
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if mode == 'dkvu_error':
            qc_status_response = load_json('qc/dkk-dkvu.json')
        elif mode == 'dkk_need_pass':
            qc_status_response = load_json(
                'qc/dkk-error-restriction-on-need-pass.json',
            )
        else:
            qc_status_response = load_json(
                'qc/dkk-error-restriction-on-dkk-pending.json',
            )
        if mode == 'dkk_passed':
            qc_status_response['items'][0]['exams'][1].pop('present')
        return qc_status_response

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    if mode == 'dkvu_error':
        assert content == load_json(
            'response/ErrorRestrictionOnDkkPending_'
            'Pending_DkvuError_NoExp.json',
        )
    elif mode == 'dkk_pending':
        assert content == load_json(
            'response/ErrorRestrictionOnDkkPending_Pending_NoExperiment.json',
        )
    elif mode == 'dkk_need_pass':
        assert content == load_json(
            'response/ErrorRestrictionOnDkkPending_NeedPass.json',
        )
    else:
        assert mode == 'dkk_passed'
        assert content == load_json(
            'response/ErrorRestrictionOnDkkPending_DkkPassed.json',
        )


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driver', '1'],
    [
        'hset',
        'Driver:TimeBlock:Items',
        'driver',
        json.dumps({'msg': 'timeblock'}),
    ],
)
@pytest.mark.driver_experiments('error_restriction_on_dkk_pending')
@pytest.mark.parametrize(
    'mode', ['dkvu_error', 'dkk_pending', 'dkk_passed', 'dkk_need_pass'],
)
@pytest.mark.now('2018-08-08T12:30:00+0300')
def test_error_restriction_on_dkk_pending(
        taxi_driver_protocol,
        mockserver,
        load_json,
        mode,
        driver_authorizer_service,
):
    """
    Test crutch for TAXIMETERBACK-4713
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if mode == 'dkvu_error':
            qc_status_response = load_json('qc/dkk-dkvu.json')
        elif mode == 'dkk_need_pass':
            qc_status_response = load_json(
                'qc/dkk-error-restriction-on-need-pass.json',
            )
        else:
            qc_status_response = load_json(
                'qc/dkk-error-restriction-on-dkk-pending.json',
            )
        if mode == 'dkk_passed':
            qc_status_response['items'][0]['exams'][1].pop('present')
        return qc_status_response

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    if mode == 'dkvu_error':
        assert content == load_json(
            'response/ErrorRestrictionOnDkkPending_Pending_DkvuError.json',
        )
    elif mode == 'dkk_pending':
        assert content == load_json(
            'response/ErrorRestrictionOnDkkPending_Pending.json',
        )
    elif mode == 'dkk_need_pass':
        assert content == load_json(
            'response/ErrorRestrictionOnDkkPending_NeedPass.json',
        )
    else:
        assert mode == 'dkk_passed'
        assert content == load_json(
            'response/ErrorRestrictionOnDkkPending_DkkPassed.json',
        )


@pytest.mark.redis_store(
    ['hset', '1488:STATUS_DRIVERS', 'driver', '1'],
    [
        'hset',
        'Driver:TimeBlock:Items',
        'driver',
        json.dumps({'msg': 'timeblock'}),
    ],
)
@pytest.mark.driver_experiments('error_restriction_on_dkk_pending')
@pytest.mark.driver_experiments('remove_time_block_on_dkk_reasons')
@pytest.mark.parametrize(
    'mode', ['dkvu_error', 'dkk_pending', 'dkk_passed', 'dkk_need_pass'],
)
@pytest.mark.now('2018-08-08T12:30:00+0300')
def test_error_restriction_on_dkk_pending_remove_time_block(
        taxi_driver_protocol,
        mockserver,
        load_json,
        mode,
        driver_authorizer_service,
):
    """
    Test crutch for TAXIMETERBACK-4713
    """
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        if mode == 'dkvu_error':
            qc_status_response = load_json('qc/dkk-dkvu.json')
        elif mode == 'dkk_need_pass':
            qc_status_response = load_json(
                'qc/dkk-error-restriction-on-need-pass.json',
            )
        else:
            qc_status_response = load_json(
                'qc/dkk-error-restriction-on-dkk-pending.json',
            )
        if mode == 'dkk_passed':
            qc_status_response['items'][0]['exams'][1].pop('present')
        return qc_status_response

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    if mode == 'dkvu_error':
        sample = load_json(
            'response/ErrorRestrictionOnDkkPending_Pending_DkvuError.json',
        )
        sample['reasons'] = []
        assert content == sample
    elif mode == 'dkk_pending':
        sample = load_json(
            'response/ErrorRestrictionOnDkkPending_Pending.json',
        )
        sample['reasons'] = []
        assert content == sample
    elif mode == 'dkk_need_pass':
        sample = load_json(
            'response/ErrorRestrictionOnDkkPending_NeedPass.json',
        )
        sample['reasons'] = []
        assert content == sample
    else:
        assert mode == 'dkk_passed'
        assert content == load_json(
            'response/ErrorRestrictionOnDkkPending_DkkPassed.json',
        )


FNS_SETTINGS = {
    'drivercheck_restrictions_ver': '8.82 (456)',
    'drivercheck_restrictions_action': 'taximeter://open_app?package=fns.app',
}


@pytest.mark.parametrize(
    'show_restrictions_to_unbounded',
    (
        pytest.param(
            True,
            marks=pytest.mark.config(
                TAXIMETER_FNS_SELF_EMPLOYMENT_SETTINGS=dict(
                    FNS_SETTINGS, show_restrictions_to_unbounded=True,
                ),
            ),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(
                TAXIMETER_FNS_SELF_EMPLOYMENT_SETTINGS=dict(
                    FNS_SETTINGS, show_restrictions_to_unbounded=False,
                ),
            ),
        ),
        pytest.param(
            None,
            marks=pytest.mark.config(
                TAXIMETER_FNS_SELF_EMPLOYMENT_SETTINGS=FNS_SETTINGS,
            ),
        ),
    ),
)
@pytest.mark.config(TAXIMETER_QC_SETTINGS={'sync_mode': 'off'})
@pytest.mark.parametrize(
    'session_id,agent,has_restrict',
    [
        ('s1', 'Taximeter 8.82 (456)', True),
        ('s2', 'Taximeter 8.81 (456)', False),
    ],
)
def test_restrictions_selfemployed_unbound(
        taxi_driver_protocol,
        mockserver,
        session_id,
        agent,
        has_restrict,
        driver_authorizer_service,
        show_restrictions_to_unbounded,
):
    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    driver_authorizer_service.set_session('1577', 's1', 'driver1577_1')
    driver_authorizer_service.set_session('1577', 's2', 'driver1577_2')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1577&session={}'.format(session_id),
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers={ACCEPT_LANGUAGE: 'ru', USER_AGENT: agent},
    )
    assert response.status_code == 200, response.text
    content = response.json()

    assert (
        any(r for r in content['reasons'] if r['code'] == 'SelfemployedBlock')
        is not has_restrict
    )

    assert any(
        r
        for r in content.get('restrictions', [])
        if r['code'] == 'SelfemployedBlock'
    ) is (has_restrict and bool(show_restrictions_to_unbounded))


@pytest.mark.config(TAXIMETER_QC_SETTINGS=dict(sync_mode='off'))
@pytest.mark.now('2020-04-28T18:52:00+0000')
@pytest.mark.parametrize(
    'scenario',
    [
        'DeliveryExams',
        'DeliveryExamsAndNoPermit',
        'DeliveryExamsEconomNoPermit',
        'DeliveryExamsEconomOk',
    ],
)
def test_class_exams_restriction(
        taxi_driver_protocol,
        mockserver,
        load_json,
        driver_authorizer_service,
        scenario,
):
    driver_authorizer_service.set_session('1488', 'qwerty', 'driver')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json(f'tracker/{scenario}.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=qwerty',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()
    assert content == load_json(f'response/{scenario}.json')


@pytest.mark.config(
    TAXIMETER_FNS_SELF_EMPLOYMENT_SETTINGS={
        'show_restrictions_to_unbounded': True,
        'drivercheck_restrictions_ver': '8.82 (456)',
        'drivercheck_restrictions_action': (
            'taximeter://open_app?package=fns.app'
        ),
    },
    TAXIMETER_QC_SETTINGS={'sync_mode': 'off'},
)
@pytest.mark.now('2019-02-19T12:31:23+0000')
def test_restrictions_selfemployed_invalid_bankprops(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1578', 's1', 'driver1578_1')

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1578&session=s1',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()

    assert any(
        r
        for r in content.get('restrictions', [])
        if r['code'] == 'SelfemployedBadRequisites'
    )
    assert content == load_json('response/RestrictionsInvalidBankprops.json')


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_BUILD={
        '__default__': {
            'min': '8.78',
            'current': '8.78',
            'disabled': ['8.80'],
            'feature_support': {},
        },
    },
    TAXIMETER_QC_SETTINGS={'sync_mode': 'off'},
)
def test_low_taximeter_version(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session(
        '1488', 'session', 'driverLowVersion',
    )

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=session',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers={ACCEPT_LANGUAGE: 'ru', USER_AGENT: 'Taximeter 8.80 (123)'},
    )
    assert response.status_code == 200
    assert response.json()['can_take_orders'] is False
    codes = []
    for reason in response.json()['reasons']:
        codes.append(reason['code'])
    assert 'DriverTaximeterVersionDisabled' in codes


@pytest.mark.config(
    TAXIMETER_VERSION_SETTINGS_BY_ZONE={
        'moscow': {'taximeter': {'min': '8.81'}},
    },
    TAXIMETER_QC_SETTINGS={'sync_mode': 'off'},
)
@pytest.mark.experiments3(
    name='taximeter_version_settings_by_zone',
    consumers=['driver_protocol/driver_check'],
    match={
        'consumers': ['driver_protocol/driver_check'],
        'predicate': {'type': 'true'},
        'enabled': True,
    },
    clauses=[],
    default_value={},
)
def test_taximeter_version_in_zone(
        taxi_driver_protocol, mockserver, driver_authorizer_service,
):
    driver_authorizer_service.set_session(
        '1488', 'session', 'driverLowVersion',
    )

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return json.dumps({'classes': []})

    response = taxi_driver_protocol.post(
        'driver/check?db=1488&session=session',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers={ACCEPT_LANGUAGE: 'ru', USER_AGENT: 'Taximeter 8.80 (123)'},
    )
    assert response.status_code == 200
    assert response.json()['can_take_orders'] is False
    codes = []
    for reason in response.json()['reasons']:
        codes.append(reason['code'])
    assert 'DriverTaximeterVersionDisabled' in codes


def form_driver_photos_status_response(status, reason):
    resp = {
        'status': f'{status}',
        'description_key': f'diagnostic_driverphoto_{status}_description',
        'text_key': f'diagnostic_driverphoto_{status}_text',
        'title_key': 'diagnostic_driverphoto_title',
        'action_key': 'diagnostic_driverphoto_action',
    }
    if reason:
        resp[
            'description_key'
        ] = f'diagnostic_driverphoto_{reason}_description'

    return resp


@pytest.mark.parametrize(
    ('status', 'reason'),
    [('approved', None), ('rejected', 'foreign_objects')],
)
@pytest.mark.experiments3(filename='experiments3_check_photo_status.json')
@pytest.mark.now('2019-11-15T12:31:23+0000')
def test_photo_status(
        taxi_driver_protocol,
        mockserver,
        status,
        reason,
        load_json,
        driver_authorizer_service,
):
    def to_capital_camel(s):
        return ''.join([r.capitalize() for r in s.split('_')])

    driver_authorizer_service.set_session('1578', 's351', 'driverSS1')

    @mockserver.json_handler('/udriver_photos/driver-photos/v1/photos/status')
    def mock_udriver_photos(request):
        return form_driver_photos_status_response(status, reason)

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok.json')

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json('qc/empty_dkk-dkvu.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1578&session=s351',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()

    if status == 'rejected':
        code = f'diagnostic_driverphoto_{reason}_description'
    else:
        code = f'diagnostic_driverphoto_{status}_description'
    if 'restrictions' in content:
        only_tested_restriction = [
            r for r in content['restrictions'] if r['code'] == code
        ]
        assert any(only_tested_restriction)
        content['restrictions'] = only_tested_restriction

    if status == 'rejected':
        assert content == load_json(
            f'response/PhotoStatus{to_capital_camel(reason)}.json',
        )
    else:
        assert content == load_json(
            f'response/PhotoStatus{to_capital_camel(status)}.json',
        )


@pytest.mark.experiments3(filename='experiments3_check_photo_status.json')
@pytest.mark.now('2019-11-15T12:31:23+0000')
def test_photo_status_business(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    driver_authorizer_service.set_session('1578', 's351', 'driverSS1')

    @mockserver.json_handler('/udriver_photos/driver-photos/v1/photos/status')
    def mock_udriver_photos(request):
        return form_driver_photos_status_response('approved', None)

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok_business.json')

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json('qc/empty_dkk-dkvu.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1578&session=s351',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()

    if 'restrictions' in content:
        only_tested_restriction = [
            r
            for r in content['restrictions']
            if r['code'].startswith(
                'diagnostic_driverphoto_approved_description',
            )
        ]
        assert any(only_tested_restriction)


@pytest.mark.experiments3(filename='experiments3_check_photo_status.json')
@pytest.mark.now('2019-11-15T12:31:23+0000')
def test_photo_status_premium(
        taxi_driver_protocol, mockserver, load_json, driver_authorizer_service,
):
    def to_capital_camel(s):
        return ''.join([r.capitalize() for r in s.split('_')])

    driver_authorizer_service.set_session('1578', 's351', 'driverSS1')

    @mockserver.json_handler('/udriver_photos/driver-photos/v1/photos/status')
    def mock_udriver_photos(request):
        return form_driver_photos_status_response('need_high_class', None)

    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json('tracker/Ok_premium.json')

    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json('qc/empty_dkk-dkvu.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    response = taxi_driver_protocol.post(
        'driver/check?db=1578&session=s351',
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers=HEADERS,
    )
    assert response.status_code == 200, response.text
    content = response.json()

    if 'restrictions' in content:
        only_tested_restriction = [
            r
            for r in content['restrictions']
            if r['code'].startswith('diagnostic_driverphoto')
        ]
        assert any(only_tested_restriction)


@pytest.mark.config(
    DRIVER_DIAGNOSTICS_UBERDRIVER_ZONE_MSG=True,
    DRIVER_DIAGNOSTICS_UBERDRIVER_NO_EXAMS_BLOCK=True,
    DISPATCH_SETTINGS_BACKEND_CPP_CACHE_UPDATE_ENABLED=True,
    CANDIDATES_FILTER_UBERDRIVER_INVISIBLE_TAGS=['uberdriver_block'],
)
@pytest.mark.now('2018-09-30T12:30:00+0300')
@pytest.mark.parametrize(
    'tracker_file', ['Ok', 'DeliveryExams', 'UberdriverInvisibleBlock'],
)
def test_uberdriver_bad_zone(
        taxi_driver_protocol,
        load_json,
        mockserver,
        driver_authorizer_service,
        tracker_file,
):
    """
    Test checks:
    there's only the restriction "uberdriver_zone" if the driver is out of
    uberdriver dispatch zone
    """
    has_invisible_block = tracker_file == 'UberdriverInvisibleBlock'

    @mockserver.json_handler('/dispatch_settings/v2/categories/fetch')
    def _mock_category_fetch(_):
        return {
            'categories': [],
            'groups': [
                {
                    'group_name': 'base',
                    'tariff_names': ['__default__base__', 'econom'],
                },
            ],
        }

    @mockserver.json_handler('/dispatch_settings/v1/settings/fetch')
    def mock_dispatch_settings(request):
        settings = load_json('dispatch_settings_uberdriver.json')
        if has_invisible_block:
            assert settings['settings'][0]['parameters'][0]['values'][
                'DISPATCH_DRIVER_TAGS_BLOCK'
            ] == ['uberdriver']
            settings['settings'][0]['parameters'][0]['values'][
                'DISPATCH_DRIVER_TAGS_BLOCK'
            ] = []  # disable visible block by uberdriver
        return settings

    driver_authorizer_service.set_client_session(
        'uberdriver', '1488', 'qwerty', 'driver',
    )

    # tracker returns no available classes
    @mockserver.json_handler('/tracker/service/driver-categories')
    def mock_driver_categories(request):
        return load_json(f'tracker/{tracker_file}.json')

    @mockserver.json_handler('/tracker/driver-status')
    def mock_status_get(request):
        return {'taximeter_status': 2}

    # no qc checks required
    @mockserver.json_handler('/qcs/api/v1/state')
    def mock_qc_status(request):
        return load_json('qc/empty_dkk-dkvu.json')

    taxi_driver_protocol.invalidate_caches()

    response = taxi_driver_protocol.post(
        'driver/check',
        params={'db': '1488', 'session': 'qwerty'},
        json={'point': {'lon': 37.588119, 'lat': 55.732618}},
        headers={ACCEPT_LANGUAGE: 'ru', USER_AGENT: 'Taximeter-Uber 9.40'},
    )
    response_json = response.json()

    assert response.status_code == 200
    if not has_invisible_block:
        assert not response_json['can_take_orders']
        restriction = {
            'actions': None,
            'code': 'uberdriver_zone',
            'description': 'Чтобы снова получать заказы вернитесь в Омск',
            'fullscreen_icon': '',
            'level': 'ERROR',
            'modified': '2018-09-30T09:30:00+0000',
            'status_icon': 'red_cross',
            'text': 'В этой зоне Uber Driver не работает',
            'title': 'Заказы недоступны',
        }
        assert restriction in response_json['restrictions']
    else:
        assert response_json['can_take_orders']
        assert not response_json.get('restrictions')
