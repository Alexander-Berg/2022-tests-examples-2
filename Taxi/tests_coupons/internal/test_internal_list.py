# pylint: disable=too-many-lines
import json

import pytest

from tests_coupons import util
from tests_coupons.referral import util as referral_util


@pytest.mark.config(COUPONS_SERVICE_ENABLED=False)
@pytest.mark.parametrize(
    'phone_id, headers, services',
    [
        pytest.param(
            '5bbb5faf15870bd76635d5e2', None, ['taxi'], id='taxi_flow',
        ),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            ['eats'],
            marks=pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
            id='eats_flow',
        ),
    ],
)
async def test_coupons_disabled(taxi_coupons, phone_id, headers, services):
    request = util.mock_request_internal_list(
        ['4001'], phone_id=phone_id, services=services,
    )
    response = await util.make_internal_list_request(
        taxi_coupons, request, headers,
    )
    assert response.status_code == 429


@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.parametrize(
    'phone_id, headers, services, tokens, service',
    [
        pytest.param(
            '5bbb5faf15870bd76635d5e2',
            None,
            ['taxi'],
            {},
            'taxi',
            id='taxi_flow',
        ),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            ['eats'],
            {'apns_token': 'apns_token'},
            'eats',
            marks=pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
            id='eats_flow',
        ),
    ],
)
async def test_coupons_empty_list(
        taxi_coupons,
        local_services_card,
        phone_id,
        headers,
        services,
        tokens,
        service,
):
    request = util.mock_request_internal_list(
        ['4042'], phone_id=phone_id, services=services, service=service,
    )
    request.update(tokens)
    response = await util.make_internal_list_request(
        taxi_coupons, request, headers,
    )

    assert response.status_code == 200
    assert response.json()['coupons'] == []

    assert local_services_card.mock_cardstorage.times_called == 0


@pytest.mark.parametrize(
    'phone_id, headers, services, service',
    [
        pytest.param(
            '5bbb5faf15870bd76635d5e2', None, ['taxi'], 'taxi', id='taxi_flow',
        ),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            ['eats'],
            'eats',
            marks=(
                pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
                pytest.mark.filldb(promocode_series='eats_flow'),
            ),
            id='eats_flow',
        ),
    ],
)
@pytest.mark.parametrize(
    'uids, application_name,expected_codes',
    [
        pytest.param(
            ['4001', '4002', '4003'],
            'iphone',
            ['secondpromocode', 'firstpromocode'],
            id='fetch_coupons_from_different_yandex_uids',
        ),
        # TODO: brand_coupons_split: delete after migrate coupons
        pytest.param(
            ['4001', '4002', '4003'],
            'uber_android',
            [],
            marks=[pytest.mark.config(COUPONS_SOFT_FILTER_BRAND=['yauber'])],
            id='soft_fetch_coupons_with_empty_brand_name',
        ),
        pytest.param(
            ['4001', '4002', '4003'],
            'uber_android',
            [],
            id='strong_fetch_coupons_by_brand_name',
        ),
        pytest.param(
            ['4001', '4002', '4007'],
            'iphone',
            ['secondpromocode', 'firstpromocode'],
            id='fetch_coupons_with_repeated_codes',
        ),
        pytest.param(['4007', '4008'], 'iphone', ['secondpromocode']),
    ],
)
async def test_coupons_list_simple(
        taxi_coupons,
        uids,
        application_name,
        expected_codes,
        local_services,
        phone_id,
        headers,
        services,
        service,
):
    request = util.mock_request_internal_list(
        uids,
        application_name=application_name,
        phone_id=phone_id,
        services=services,
        service=service,
    )
    response = await util.make_internal_list_request(
        taxi_coupons, request, headers,
    )

    assert response.status_code == 200
    response_json = response.json()

    response_codes = [x['code'] for x in response_json['coupons']]
    assert response_codes == expected_codes

    if 'secondpromocode' in expected_codes:
        for coupon in response_json['coupons']:
            if coupon['code'] == 'firstpromocode':
                assert coupon['reason_type'] == 'referral_reward'
            if coupon['code'] == 'secondpromocode':
                assert coupon['series_meta'] == {
                    'keyNull': None,
                    'keyObj': {
                        'keyArr': [1, 2, 3],
                        'keyInnerObj': {'keyBool': True, 'keyNum': 321},
                    },
                    'keyStr': 'hello',
                }
                assert coupon['expire_at'] == '2020-03-01T00:00:00+00:00'
                assert coupon['value'] == 400.0
                assert coupon['series_id'] == 'secondpromocode'
                assert coupon['currency_code'] == 'RUB'


@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.pgsql(
    referral_util.REFERRALS_DB_NAME,
    files=referral_util.PGSQL_REFERRAL,
    queries=referral_util.SQLS_REFERRAL_CONSUMER_CONFIG_PERCENT,
)
@pytest.mark.parametrize(
    'phone_id, headers, services, service, device_id, uids, valid_codes',
    [
        pytest.param(
            '5bbb5faf15870bd76635d5e2',
            None,
            ['taxi'],
            'taxi',
            None,
            ['4001', '4002', '4003', '4007', '4008'],
            [
                'percentreferral',
                'secondpromocode',
                'firstpromocode',
                'percentreferral',
                'secondpromocode',
            ],
            id='taxi_flow',
        ),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            ['eats'],
            'eats',
            'device_id',
            ['4022'],
            ['edapromic2'],
            marks=(
                pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
                pytest.mark.filldb(promocode_series='eats_flow'),
            ),
            id='eats_flow',
        ),
    ],
)
async def test_coupons_validation(
        taxi_coupons,
        local_services,
        uids,
        valid_codes,
        phone_id,
        headers,
        services,
        service,
        device_id,
):
    local_services.add_card()
    request = util.mock_request_internal_list(
        uids,
        phone_id=phone_id,
        services=services,
        service=service,
        brand_names=['yataxi', 'eats'],
    )
    if device_id:
        request['device_id'] = device_id

    response = await util.make_internal_list_request(
        taxi_coupons, request, headers,
    )
    assert response.status_code == 200
    response_json = response.json()

    valid_resp_codes = []
    for code in response_json['coupons']:
        if code['status'] == 'valid':
            valid_resp_codes.append(code['code'])

    assert set(valid_codes) == set(valid_resp_codes)

    for coupon in response_json['coupons']:
        if coupon['code'] == 'percentreferral':
            assert coupon['percent'] == 10
            assert coupon['limit'] == 300.0
            assert coupon['currency_code'] == 'RUB'


@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.config(COUPONS_EXTERNAL_VALIDATION_SERVICES=['grocery', 'eats'])
@pytest.mark.parametrize(
    'phone_id, headers, services, service, device_id, lavka_times_called,'
    ' eats_times_called',
    [
        pytest.param(
            '5bbb5faf15870bd76635d5e2',
            None,
            ['grocery'],
            'grocery',
            None,
            1,
            0,
            id='taxi_flow',
        ),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            ['eats'],
            'eats',
            'device_id',
            0,
            1,
            marks=pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
            id='eats_flow',
        ),
    ],
)
@pytest.mark.parametrize(
    'external_code, external_response, is_valid',
    [
        pytest.param(500, {}, True, id='skip_external_service_error'),
        pytest.param(
            200,
            {
                'valid': False,
                'valid_any': True,
                'descriptions': [],
                'details': [],
                'error_description': 'Some error from lavka',
            },
            False,
            id='show_error_from_external_validation',
        ),
    ],
)
async def test_list_external_validation(
        taxi_coupons,
        local_services,
        mockserver,
        external_code,
        external_response,
        is_valid,
        phone_id,
        headers,
        services,
        service,
        device_id,
        lavka_times_called,
        eats_times_called,
):
    @mockserver.json_handler('/grocery-coupons/internal/v1/coupons/validate')
    def _mock_grocery_coupons(request):
        return mockserver.make_response(
            json.dumps(external_response), status=external_code,
        )

    @mockserver.json_handler('/eats-coupons/internal/v1/coupons/validate')
    def _mock_eats_coupons(request):
        assert request.json['series_id'] is not None
        assert request.json['source_handler'] == 'list'
        return mockserver.make_response(
            json.dumps(external_response), status=external_code,
        )

    local_services.add_card()
    request = util.mock_request_internal_list(
        ['4017'], phone_id=phone_id, services=services, service=service,
    )
    if device_id:
        request['device_id'] = device_id

    response = await util.make_internal_list_request(
        taxi_coupons, request, headers,
    )
    assert response.status_code == 200
    assert _mock_grocery_coupons.times_called == lavka_times_called
    assert _mock_eats_coupons.times_called == eats_times_called

    response_json = response.json()
    assert len(response_json['coupons']) == 1

    coupon = response_json['coupons'][0]
    assert coupon['status'] == 'valid' if is_valid else 'invalid'

    error = coupon.get('error')
    if is_valid:
        assert not error
    else:
        assert error['code'] == 'ERROR_EXTERNAL_VALIDATION_FAILED'
        assert error['description'] == external_response['error_description']


@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.config(COUPONS_EXTERNAL_VALIDATION_SERVICES=['eats'])
@pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)
@pytest.mark.config(
    COUPONS_TERMINAL_PROMOCODE_STATUSES=['ERROR_EXTERNAL_INVALID_CODE'],
)
@pytest.mark.parametrize(
    'parse_valid_any',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(COUPONS_RESTRICT_EATS_PROMOCODES=True),
            id='parse_valid_any',
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(COUPONS_RESTRICT_EATS_PROMOCODES=False),
            id='not_parse_valid_any',
        ),
    ],
)
@pytest.mark.parametrize(
    'valid_any',
    [
        pytest.param(True, id='restricted_coupon'),
        pytest.param(False, id='invalid_coupon'),
    ],
)
async def test_list_external_eats_parse_valid_any(
        taxi_coupons, local_services, mockserver, valid_any, parse_valid_any,
):
    @mockserver.json_handler('/eats-coupons/internal/v1/coupons/validate')
    def _mock_eats_coupons(request):
        assert request.json['series_id'] is not None
        assert request.json['source_handler'] == 'list'
        return mockserver.make_response(
            json.dumps(
                {
                    'valid': False,
                    'valid_any': valid_any,
                    'descriptions': [],
                    'details': [],
                    'error_description': 'Some error from eats validator',
                },
            ),
            status=200,
        )

    local_services.add_card()
    request = util.mock_request_internal_list(
        ['4017'], phone_id=None, services=['eats'], service='eats',
    )
    request['device_id'] = 'device_id'

    response = await util.make_internal_list_request(
        taxi_coupons,
        request,
        {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
    )
    assert response.status_code == 200
    assert _mock_eats_coupons.times_called == 1

    response_json = response.json()
    if not parse_valid_any:
        assert len(response_json['coupons']) == 1
        coupon = response_json['coupons'][0]
        assert coupon['status'] == 'invalid'
        assert coupon['error'] == {
            'code': 'ERROR_EXTERNAL_VALIDATION_FAILED',
            'description': 'Some error from eats validator',
        }
        return

    if valid_any:
        assert len(response_json['coupons']) == 1
        coupon = response_json['coupons'][0]
        assert coupon['status'] == 'restricted'
        assert coupon['error'] == {
            'code': 'ERROR_EXTERNAL_RESTRICTED_EATS_CODE',
            'description': 'Some error from eats validator',
        }
    else:
        assert not response_json['coupons']


@pytest.mark.config(
    COUPONS_TERMINAL_PROMOCODE_STATUSES=['ERROR_CREDITCARD_REQUIRED'],
)
@pytest.mark.pgsql(
    referral_util.REFERRALS_DB_NAME,
    files=referral_util.PGSQL_REFERRAL,
    queries=referral_util.SQLS_REFERRAL_CONSUMER_CONFIG_PERCENT,
)
@pytest.mark.now('2019-01-01T00:00:00+0300')
@pytest.mark.parametrize(
    'phone_id, headers, services, service, device_id',
    [
        pytest.param(
            '5bbb5faf15870bd76635d5e2',
            None,
            ['taxi'],
            'taxi',
            None,
            id='taxi_flow',
        ),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            ['eats'],
            'eats',
            'device_id',
            marks=pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
            id='eats_flow',
        ),
    ],
)
@pytest.mark.parametrize(
    'promocodes',
    [
        [
            'firstpromocode',
            'secondpromocode',
            'percentreferral',
            'xcode',
            'strangecategories',
        ],
    ],
)
async def test_coupon_filtering(
        taxi_coupons,
        mongodb,
        promocodes,
        local_services,
        phone_id,
        headers,
        services,
        service,
        device_id,
):
    uid = util.generate_virtual_user_coupons(promocodes, 'yataxi', mongodb)
    request = util.mock_request_internal_list(
        [uid], phone_id=phone_id, services=services, service=service,
    )
    if device_id:
        request['device_id'] = device_id
    response = await util.make_internal_list_request(
        taxi_coupons, request, headers,
    )

    assert response.status_code == 200
    response_json = response.json()

    codes = [x['code'] for x in response_json['coupons']]
    assert codes == []


@pytest.mark.pgsql(
    referral_util.REFERRALS_DB_NAME,
    files=referral_util.PGSQL_REFERRAL,
    queries=referral_util.SQLS_REFERRAL_CONSUMER_CONFIG_PERCENT,
)
@pytest.mark.now('2019-01-01T00:00:00+0300')
@pytest.mark.parametrize(
    'phone_id,'
    'headers,'
    'services,'
    'service,'
    'device_id,'
    'expected_response_file,'
    'promocodes',
    [
        pytest.param(
            '5bbb5faf15870bd76635d5e2',
            None,
            ['taxi'],
            'taxi',
            None,
            'expected_internal_list_response_strings.json',
            [
                'firstpromocode',
                'secondpromocode',
                'percentreferral',
                'xcode',
                'strangecategories',
                'servicespromocode',
                'emptyservicespromocode',
            ],
            id='taxi_flow',
        ),
    ],
)
async def test_coupon_strings(
        taxi_coupons,
        mongodb,
        promocodes,
        load_json,
        local_services,
        phone_id,
        headers,
        services,
        service,
        device_id,
        expected_response_file,
):
    local_services.add_card()
    uid = util.generate_virtual_user_coupons(promocodes, 'yataxi', mongodb)
    request = util.mock_request_internal_list(
        [uid], phone_id=phone_id, services=services, service=service,
    )
    if device_id:
        request['device_id'] = device_id

    response = await util.make_internal_list_request(
        taxi_coupons, request, headers,
    )
    assert response.status_code == 200
    response_json = response.json()

    expected = load_json(expected_response_file)
    paths_to_sort = {'coupons.services'}
    actual_json = util.sort_json(response_json, paths_to_sort)
    expected_json = util.sort_json(expected, paths_to_sort)
    assert actual_json == expected_json


@pytest.mark.now('2019-01-01T00:00:00+0300')
@pytest.mark.parametrize(
    'phone_id,'
    'headers,'
    'services,'
    'service,'
    'device_id,'
    'promocodes,'
    'expected_response_file',
    [
        pytest.param(
            '5bbb5faf15870bd76635d5e2',
            None,
            ['grocery'],
            'grocery',
            None,
            ['servicespromocode', 'emptyservicespromocode'],
            'expected_internal_list_response_strings_with_services.json',
            id='grocery_flow',
        ),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            ['eats'],
            'eats',
            'device_id',
            ['edapromic2'],
            'expected_internal_list_response_strings_with_services_eats.json',
            marks=pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
            id='eats_flow',
        ),
    ],
)
async def test_coupon_strings_with_services(
        taxi_coupons,
        mongodb,
        promocodes,
        load_json,
        local_services,
        phone_id,
        headers,
        services,
        service,
        device_id,
        expected_response_file,
):
    local_services.add_card()
    uid = util.generate_virtual_user_coupons(promocodes, 'yataxi', mongodb)

    request = util.mock_request_internal_list(
        [uid], services=services, phone_id=phone_id, service=service,
    )
    if device_id:
        request['device_id'] = device_id
    response = await util.make_internal_list_request(
        taxi_coupons, request, headers,
    )

    assert response.status_code == 200
    response_json = response.json()

    expected = load_json(expected_response_file)
    paths_to_sort = {'coupons.services'}
    actual_json = util.sort_json(response_json, paths_to_sort)
    expected_json = util.sort_json(expected, paths_to_sort)
    assert actual_json == expected_json


@pytest.mark.now('2019-01-01T00:00:00+0300')
@pytest.mark.parametrize(
    'phone_id, headers, service',
    [
        pytest.param('5bbb5faf15870bd76635d5e2', None, 'taxi', id='taxi_flow'),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            'eats',
            marks=pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
            id='eats_flow',
        ),
    ],
)
@pytest.mark.parametrize('promocodes', [[]])
async def test_coupon_strings_with_empty_services(
        taxi_coupons,
        mongodb,
        promocodes,
        local_services,
        phone_id,
        headers,
        service,
):
    local_services.add_card()
    uid = util.generate_virtual_user_coupons(promocodes, 'yataxi', mongodb)

    request = util.mock_request_internal_list(
        [uid], services=[], phone_id=phone_id, service=service,
    )
    response = await util.make_internal_list_request(
        taxi_coupons, request, headers,
    )

    assert response.status_code == 400


@pytest.mark.parametrize(
    'phone_id, headers, services, service',
    [
        pytest.param(
            '5bbb5faf15870bd76635d5e2', None, ['taxi'], 'taxi', id='taxi_flow',
        ),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            ['eats'],
            'eats',
            marks=pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
            id='eats_flow',
        ),
    ],
)
async def test_metrics_exist(
        taxi_coupons,
        taxi_coupons_monitor,
        local_services,
        phone_id,
        headers,
        services,
        service,
):
    request = util.mock_request_internal_list(
        ['4001', '4002', '4003'],
        application_name='iphone',
        phone_id=phone_id,
        services=services,
        service=service,
    )
    response = await util.make_internal_list_request(
        taxi_coupons, request, headers,
    )
    assert response.status_code == 200

    metrics_name = 'coupons-list-statistics'
    metrics = await taxi_coupons_monitor.get_metrics(metrics_name)

    assert metrics_name in metrics.keys()


BILLING_SERVICE_NAME_MAP_BY_BRAND = {
    '__default__': 'unknown',
    'yataxi': 'card',
    'yango': 'card',
    'yauber': 'uber',
}
APPLICATION_MAP_BRAND = {
    '__default__': 'unknown',
    'iphone': 'yataxi',
    'yango_android': 'yango',
    'uber_iphone': 'yauber',
}


@pytest.mark.config(
    BILLING_SERVICE_NAME_MAP_BY_BRAND=BILLING_SERVICE_NAME_MAP_BY_BRAND,
    APPLICATION_MAP_BRAND=APPLICATION_MAP_BRAND,
)
@pytest.mark.parametrize(
    'phone_id, headers, services, service',
    [
        pytest.param(
            '5bbb5faf15870bd76635d5e2', None, ['taxi'], 'taxi', id='taxi_flow',
        ),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            ['eats'],
            'eats',
            marks=pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
            id='eats_flow',
        ),
    ],
)
@pytest.mark.parametrize(
    'app_name',
    ['iphone', 'yango_android', 'uber_iphone', 'mobileweb_android'],
)
async def test_cardstorage_request(
        app_name,
        taxi_coupons,
        mongodb,
        local_services,
        mockserver,
        phone_id,
        headers,
        services,
        service,
):
    brand_name = APPLICATION_MAP_BRAND.get(app_name, 'unknown')
    uid = util.generate_virtual_user_coupons(
        ['firstpromocode'], brand_name, mongodb,
    )

    local_services.check_service_type(
        BILLING_SERVICE_NAME_MAP_BY_BRAND, APPLICATION_MAP_BRAND, app_name,
    )

    request = util.mock_request_internal_list(
        [uid],
        application_name=app_name,
        phone_id=phone_id,
        services=services,
        service=service,
    )
    response = await util.make_internal_list_request(
        taxi_coupons, request, headers,
    )

    assert local_services.mock_cardstorage.has_calls
    assert response.status_code == 200


@pytest.mark.experiments3(
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='afs_notify_handler_call_coupon_list',
    consumers=['coupons/couponlist'],
    clauses=[],
    default_value={},
)
async def test_check_sending_afs_event(
        taxi_coupons, local_services, testpoint, mockserver,
):
    @testpoint('afs-couponlist-event-passed')
    def afs_couponlist_finished(data):
        pass

    @mockserver.json_handler('/antifraud/v1/events/protocol/couponlist')
    def mock_antifraud(request):
        assert request.json['user_id'] == 'user_id'
        assert request.json['phone_id'] == '5bbb5faf15870bd76635d5e2'
        assert request.json['device_id'] == 'device_id'
        return {}

    request = util.mock_request_internal_list(
        ['4001'],
        application_name='iphone',
        phone_id='5bbb5faf15870bd76635d5e2',
    )

    response = await util.make_internal_list_request(taxi_coupons, request)
    assert response.status_code == 200
    await afs_couponlist_finished.wait_call()
    assert mock_antifraud.times_called == 1


@pytest.mark.config(
    COUPON_FRAUD_REQUIRE_CREDITCARD_BY_ZONES={'__default__': False},
)
@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.parametrize(
    'phone_id, headers, services, service, device_id, yandex_uid',
    [
        pytest.param(
            '5bbb5faf15870bd76635d5e2',
            None,
            ['grocery'],
            'grocery',
            None,
            '4020',
            id='grocery_flow',
        ),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            ['eats'],
            'eats',
            'device_id',
            '4025',
            marks=(
                pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
                pytest.mark.filldb(promocode_series='eats_flow'),
            ),
            id='eats_flow',
        ),
    ],
)
@pytest.mark.parametrize(
    'country, expected_error',
    [
        (None, 'ERROR_INVALID_COUNTRY'),
        ('rus', 'ERROR_INVALID_COUNTRY'),
        ('isr', None),
    ],
)
async def test_no_error_when_country_sent(
        taxi_coupons,
        local_services,
        country,
        expected_error,
        phone_id,
        headers,
        services,
        service,
        device_id,
        yandex_uid,
):
    request = util.mock_request_internal_list(
        [yandex_uid],
        application_name='iphone',
        services=services,
        phone_id=phone_id,
        service=service,
    )
    request['payment']['type'] = ''
    del request['selected_class']
    del request['payment']['payment_method_id']

    if country is not None:
        request['country'] = country

    if device_id:
        request['device_id'] = device_id

    response = await util.make_internal_list_request(
        taxi_coupons, request, headers,
    )

    assert response.status_code == 200

    assert 'coupons' in response.json()
    assert len(response.json()['coupons']) == 1

    if expected_error is not None:
        assert response.json()['coupons'][0]['error']['code'] == expected_error
    else:
        assert 'error' not in response.json()['coupons'][0]


@pytest.mark.parametrize(
    'phone_id, services, service, app_name, uids, expected_codes',
    [
        pytest.param(
            '5bbb5faf15870bd76635d5e2',
            ['eats', 'taxi'],
            'eats',
            'eats_iphone',
            ['4001'],
            ['secondpromocode', 'firstpromocode'],
            id='eats_taxi_related',
            marks=pytest.mark.config(
                APPLICATION_BRAND_RELATED_BRANDS={'eats': ['yataxi']},
            ),
        ),
        pytest.param(
            '5bbb5faf15870bd76635d5e2',
            ['eats', 'taxi'],
            'eats',
            'eats_iphone',
            ['4001'],
            [],
            id='not_related',
            marks=pytest.mark.config(APPLICATION_BRAND_RELATED_BRANDS={}),
        ),
    ],
)
async def test_related_brands(
        local_services,
        taxi_coupons,
        phone_id,
        services,
        service,
        app_name,
        uids,
        expected_codes,
):
    request = util.mock_request_internal_list(
        uids,
        application_name=app_name,
        phone_id=phone_id,
        services=services,
        service=service,
    )
    response = await util.make_internal_list_request(
        taxi_coupons,
        request,
        {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
    )

    assert response.status_code == 200
    assert 'coupons' in response.json()
    assert len(response.json()['coupons']) == len(expected_codes)
    codes = []
    for coupon in response.json()['coupons']:
        codes.append(coupon['code'])
    assert codes == expected_codes


@pytest.mark.parametrize(
    'brand_names, app_name, expected_codes',
    [
        pytest.param(
            None,
            'eats_iphone',
            ['secondpromocode', 'firstpromocode'],
            id='without_brand_name',
            marks=pytest.mark.config(
                APPLICATION_MAP_BRAND={'eats_iphone': 'eats'},
            ),
        ),
        pytest.param(
            ['eats'],
            'eats_iphone',
            ['secondpromocode', 'firstpromocode'],
            id='brand_matches_application',
            marks=pytest.mark.config(
                APPLICATION_MAP_BRAND={'eats_iphone': 'eats'},
            ),
        ),
        pytest.param(
            ['eats'],
            'lavka_iphone',
            ['secondpromocode', 'firstpromocode'],
            id='brand_doesnt_match_application',
            marks=pytest.mark.config(
                APPLICATION_MAP_BRAND={'lavka_iphone': 'eats'},
            ),
        ),
        pytest.param(
            ['lavka'],
            'lavka_iphone',
            [],
            id='empty_list_by_brand',
            marks=pytest.mark.config(
                APPLICATION_MAP_BRAND={'lavka_iphone': 'lavka'},
            ),
        ),
        pytest.param(
            None,
            'lavka_iphone',
            [],
            id='empty_list_by_config',
            marks=pytest.mark.config(
                APPLICATION_MAP_BRAND={'lavka_iphone': 'lavka'},
            ),
        ),
        pytest.param(
            ['eats', 'lavka', 'yataxi'],
            'lavka_iphone',
            ['secondpromocode', 'firstpromocode'],
            id='brand_list',
            marks=pytest.mark.config(
                APPLICATION_MAP_BRAND={'lavka_iphone': 'lavka'},
            ),
        ),
    ],
)
async def test_brand_name_filter(
        local_services, taxi_coupons, app_name, brand_names, expected_codes,
):
    request = util.mock_request_internal_list(
        yandex_uids=['4024'],
        application_name=app_name,
        phone_id='5bbb5faf15870bd76635d5e2',
        services=['taxi'],
        service='eats',
        brand_names=brand_names,
    )
    response = await util.make_internal_list_request(
        taxi_coupons,
        request,
        {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
    )

    assert response.status_code == 200
    assert 'coupons' in response.json()
    assert len(response.json()['coupons']) == len(expected_codes)
    codes = []
    for coupon in response.json()['coupons']:
        codes.append(coupon['code'])
    assert codes == expected_codes
