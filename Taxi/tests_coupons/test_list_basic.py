import json

import pytest

from tests_coupons import util
from tests_coupons.referral import util as referral_util


@pytest.mark.config(COUPONS_SERVICE_ENABLED=False)
@pytest.mark.skip(reason='flapping test, will be fixed in TAXIBACKEND-41551')
async def test_coupons_disabled(taxi_coupons):
    request = util.mock_request_list(['4001'])
    response = await util.make_list_request(taxi_coupons, request)
    assert response.status_code == 429


async def test_coupons_list_4xx(taxi_coupons):
    response = await util.make_list_request(taxi_coupons, None)
    assert response.status_code == 400

    response = await util.make_list_request(taxi_coupons, {})
    assert response.status_code == 400


@pytest.mark.now('2019-03-06T11:30:00+0300')
async def test_coupons_empty_list(taxi_coupons, local_services_card):
    request = util.mock_request_list(['4042'], 'iphone')
    response = await util.make_list_request(taxi_coupons, request)

    assert response.status_code == 200
    assert response.json()['coupons'] == []

    assert local_services_card.mock_cardstorage.times_called == 0


@pytest.mark.parametrize(
    'uids,application_name,expected_codes',
    [
        pytest.param(
            ['4001', '4002', '4003'],
            'iphone',
            ['percentreferral', 'secondpromocode', 'firstpromocode'],
            id='fetch_coupons_from_different_yandex_uids',
        ),
        # TODO: brand_coupons_split: delete after migrate coupons
        pytest.param(
            ['4001', '4002', '4003'],
            'uber_android',
            ['percentreferral', 'ubersecondpromocode', 'uberfirstpromocode'],
            marks=[pytest.mark.config(COUPONS_SOFT_FILTER_BRAND=['yauber'])],
            id='soft_fetch_coupons_with_empty_brand_name',
        ),
        pytest.param(
            ['4001', '4002', '4003'],
            'uber_android',
            ['ubersecondpromocode', 'uberfirstpromocode'],
            id='strong_fetch_coupons_by_brand_name',
        ),
        pytest.param(
            ['4001', '4002', '4007'],
            'iphone',
            ['percentreferral', 'secondpromocode', 'firstpromocode'],
            id='fetch_coupons_with_repeated_codes',
        ),
        pytest.param(
            ['4007', '4008'],
            'iphone',
            ['percentreferral', 'secondpromocode', 'xcode'],
        ),
    ],
)
async def test_coupons_list_simple(
        taxi_coupons, uids, application_name, expected_codes, local_services,
):
    request = util.mock_request_list(uids, application_name)
    response = await util.make_list_request(taxi_coupons, request)

    assert response.status_code == 200
    response_json = response.json()

    response_codes = [x['code'] for x in response_json['coupons']]
    assert response_codes == expected_codes


@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.pgsql(
    referral_util.REFERRALS_DB_NAME,
    files=referral_util.PGSQL_REFERRAL,
    queries=referral_util.SQLS_REFERRAL_CONSUMER_CONFIG_PERCENT,
)
@pytest.mark.parametrize('collections_tag', util.USER_COUPONS_DB_MODE_PARAMS)
@pytest.mark.parametrize(
    'uids,valid_codes',
    [
        (
            ['4001', '4002', '4003'],
            ['percentreferral', 'secondpromocode', 'firstpromocode'],
        ),
        (['4007', '4008'], ['percentreferral', 'secondpromocode']),
    ],
)
async def test_coupons_validation(
        taxi_coupons,
        local_services,
        uids,
        valid_codes,
        mongodb,
        collections_tag,
):
    local_services.add_card()
    util.tag_to_user_coupons_for_read(mongodb, collections_tag)

    request = util.mock_request_list(uids)
    response = await util.make_list_request(taxi_coupons, request)
    assert response.status_code == 200
    response_json = response.json()

    valid_resp_codes = []
    for code in response_json['coupons']:
        if code['status'] == 'valid':
            valid_resp_codes.append(code['code'])

    assert set(valid_codes) == set(valid_resp_codes)


@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.config(COUPONS_EXTERNAL_VALIDATION_SERVICES=['grocery', 'eats'])
@pytest.mark.parametrize(
    'external_code, external_response, is_valid, yandex_uid',
    [
        pytest.param(500, {}, True, '4017', id='skip_external_service_error'),
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
            '4017',
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
        yandex_uid,
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
    request = util.mock_request_list([yandex_uid])
    response = await util.make_list_request(taxi_coupons, request)
    assert response.status_code == 200
    assert _mock_grocery_coupons.times_called == 1
    assert _mock_eats_coupons.times_called == 1

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
        taxi_coupons, mongodb, promocodes, local_services,
):
    uid = util.generate_virtual_user_coupons(promocodes, 'yataxi', mongodb)
    request = util.mock_request_list([uid])
    response = await util.make_list_request(taxi_coupons, request)

    assert response.status_code == 200
    response_json = response.json()

    codes = [x['code'] for x in response_json['coupons']]
    assert codes == ['xcode']


@pytest.mark.pgsql(
    referral_util.REFERRALS_DB_NAME,
    files=referral_util.PGSQL_REFERRAL,
    queries=referral_util.SQLS_REFERRAL_CONSUMER_CONFIG_PERCENT,
)
@pytest.mark.now('2019-01-01T00:00:00+0300')
@pytest.mark.parametrize(
    'promocodes',
    [
        [
            'firstpromocode',
            'secondpromocode',
            'percentreferral',
            'xcode',
            'strangecategories',
            'servicespromocode',
            'emptyservicespromocode',
        ],
    ],
)
async def test_coupon_strings(
        taxi_coupons, mongodb, promocodes, load_json, local_services,
):
    local_services.add_card()
    uid = util.generate_virtual_user_coupons(promocodes, 'yataxi', mongodb)
    request = util.mock_request_list([uid])
    response = await util.make_list_request(taxi_coupons, request)
    assert response.status_code == 200
    response_json = response.json()

    expected = load_json('expected_response_strings.json')
    paths_to_sort = {'coupons.services'}
    actual_json = util.sort_json(response_json, paths_to_sort)
    expected_json = util.sort_json(expected, paths_to_sort)
    assert actual_json == expected_json


@pytest.mark.now('2019-01-01T00:00:00+0300')
@pytest.mark.parametrize(
    'promocodes', [['servicespromocode', 'emptyservicespromocode']],
)
async def test_coupon_strings_with_services(
        taxi_coupons, mongodb, promocodes, load_json, local_services,
):
    local_services.add_card()
    uid = util.generate_virtual_user_coupons(promocodes, 'yataxi', mongodb)

    request = util.mock_request_list([uid], services=['grocery'])
    response = await util.make_list_request(taxi_coupons, request)

    assert response.status_code == 200
    response_json = response.json()

    expected = load_json('expected_response_strings_with_services.json')
    paths_to_sort = {'coupons.services'}
    actual_json = util.sort_json(response_json, paths_to_sort)
    expected_json = util.sort_json(expected, paths_to_sort)
    assert actual_json == expected_json


@pytest.mark.now('2019-01-01T00:00:00+0300')
@pytest.mark.parametrize('promocodes', [[]])
async def test_coupon_strings_with_empty_services(
        taxi_coupons, mongodb, promocodes, local_services,
):
    local_services.add_card()
    uid = util.generate_virtual_user_coupons(promocodes, 'yataxi', mongodb)

    request = util.mock_request_list([uid], services=[])
    response = await util.make_list_request(taxi_coupons, request)

    assert response.status_code == 400


@pytest.mark.translations(
    override_uber={
        'coupons.coupon.title.unavailable': {'ru': 'Uber unavailable'},
    },
)
@pytest.mark.now('2019-01-01T00:00:00+0300')
async def test_coupon_strings_override(mongodb, taxi_coupons, local_services):
    local_services.add_card()
    uid = util.generate_virtual_user_coupons(['xcode'], 'yauber', mongodb)

    request = util.mock_request_list([uid])
    request['application']['name'] = 'uber_iphone'
    response = await util.make_list_request(taxi_coupons, request)

    assert response.status_code == 200
    content = response.json()
    assert content['coupons'][0]['title'] == 'Uber unavailable'


async def test_metrics_exist(
        taxi_coupons, taxi_coupons_monitor, local_services,
):
    request = util.mock_request_list(['4001', '4002', '4003'], 'iphone')
    response = await util.make_list_request(taxi_coupons, request)
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
    COUPONS_CARDSTORAGE_REQUESTS_PARAMS={
        '__default__': {
            'timeout_ms': 10000,
            'retries': 2,
            'pass_renew_after': False,
        },
        'couponlist': {
            'timeout_ms': 15000,
            'retries': 3,
            'pass_renew_after': True,
        },
    },
)
@pytest.mark.parametrize(
    'app_name',
    ['iphone', 'yango_android', 'uber_iphone', 'mobileweb_android'],
)
async def test_cardstorage_request(
        taxi_coupons, mongodb, local_services, mockserver, app_name,
):
    brand_name = APPLICATION_MAP_BRAND.get(app_name, 'unknown')
    uid = util.generate_virtual_user_coupons(
        ['firstpromocode'], brand_name, mongodb,
    )

    local_services.check_service_type(
        BILLING_SERVICE_NAME_MAP_BY_BRAND, APPLICATION_MAP_BRAND, app_name,
    )

    response = await util.make_list_request(
        taxi_coupons, util.mock_request_list([uid], app_name),
    )
    assert response.status_code == 200

    assert local_services.mock_cardstorage.has_calls

    util.check_cardstorage_requests(
        local_services.cardstorage_requests,
        expected_num_requests=3,
        expected_num_requests_wo_renew_after=1,
        expected_timeout_ms=15000,
    )


@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.config(APPLICATION_MAP_BRAND=APPLICATION_MAP_BRAND)
@pytest.mark.parametrize(
    'payment_method,method_id,valid_payment_methods',
    [
        # user_coupons:
        # [
        #   "bizpaymentmethod1",
        #   "emptypaymentmethods1",
        #   "paymentmethods1"
        # ]
        # Coupons statuses are kept in valid_payment_methods
        ('applepay', None, [False, True, True]),
        ('cash', None, [False, True, True]),
        ('card', 'card_id', [False, True, True]),
        ('card', 'ya_card_id', [False, True, True]),
        ('googlepay', None, [False, True, False]),
        ('coop_account', 'business-123', [True, True, False]),
        ('coop_account', 'family-123', [False, True, False]),
        ('coop_account', 'some-123', [False, True, False]),
    ],
)
async def test_list_payment_methods(
        taxi_coupons,
        local_services,
        payment_method,
        method_id,
        valid_payment_methods,
):
    local_services.add_card_and_ya_card()

    request = util.mock_request_list(
        ['4015'], payment_type=payment_method, payment_method_id=method_id,
    )
    response = await util.make_list_request(taxi_coupons, request)
    assert response.status_code == 200
    content = response.json()
    content['coupons'].sort(key=lambda x: x['code'])

    for valid, coupon in zip(valid_payment_methods, content['coupons']):
        assert coupon['status'] == 'valid' if valid else 'invalid'

        description_string = (
            'Сработает на следующую поездку'
            if coupon['selected']
            else '1 поездка'
        ) + ' по любому тарифу'
        util.check_coupon(coupon['code'], description_string, valid, coupon)


@pytest.mark.skip(reason='broken test, will be fixed in TAXIBACKEND-40710')
@pytest.mark.config(
    COUPONS_SERVICES_UI_TITLES={
        'taxi': {
            'title_for_one': 'coupons.ui.block_title.for_one.taxi',
            'title_for_many': 'coupons.ui.block_title.for_many.taxi',
        },
        'eats': {
            'title_for_one': 'coupons.ui.block_title.for_one.eda',
            'title_for_many': 'coupons.ui.block_title.for_many.eda',
        },
        'grocery': {
            'title_for_one': 'coupons.ui.block_title.for_one.lavka',
            'title_for_many': 'coupons.ui.block_title.for_many.lavka',
        },
    },
)
@pytest.mark.parametrize(
    'promocodes,promocode_services,service_in_splitters_order',
    [
        pytest.param(['onlytaxi1'], [['taxi']], ['taxi'], id='taxi_promocode'),
        pytest.param(
            ['onlylavka1'], [['grocery']], ['grocery'], id='lavka_promocode',
        ),
        pytest.param(
            ['servicespromocode'],
            [['taxi', 'grocery']],
            ['taxi'],
            id='services_promocode',
        ),
        pytest.param(
            ['onlylavka1', 'servicespromocode'],
            [['grocery'], ['taxi', 'grocery']],
            ['taxi', 'grocery'],
            id='two_promocodes',
        ),
    ],
)
async def test_promocodes_ui_splitters(
        taxi_coupons,
        promocodes,
        mongodb,
        promocode_services,
        service_in_splitters_order,
        local_services,
):
    uid = util.generate_virtual_user_coupons(promocodes, 'yataxi', mongodb)
    request = util.mock_request_list([uid], 'iphone')
    response = await util.make_list_request(taxi_coupons, request)
    assert response.status_code == 200
    response_json = response.json()

    assert len(response_json['coupons']) == len(promocodes)
    for i, coupon in enumerate(response_json['coupons']):
        assert set(coupon['services']) == set(promocode_services[i])

    assert 'ui' in response_json
    assert 'splitters' in response_json['ui']
    splitters = response_json['ui']['splitters']

    assert len(splitters) == len(service_in_splitters_order)

    for splitter in splitters:
        assert splitter['service'] in service_in_splitters_order
        assert 'title' in splitter


@pytest.mark.config(COUPONS_SERVICES_UI_TITLES={})
@pytest.mark.parametrize(
    'uids,application_name',
    [pytest.param(['4001'], 'iphone', id='taxi_promocode')],
)
async def test_config_no_ui_splitters(
        taxi_coupons, uids, application_name, local_services,
):
    request = util.mock_request_list(uids, application_name)
    response = await util.make_list_request(taxi_coupons, request)
    assert response.status_code == 200
    response_json = response.json()

    assert 'ui' not in response_json


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

    request = util.mock_request_list(['4001'], 'iphone')
    response = await util.make_list_request(taxi_coupons, request)
    assert response.status_code == 200
    await afs_couponlist_finished.wait_call()
    assert mock_antifraud.times_called == 1


@pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)
@pytest.mark.parametrize(
    'promocode, yandex_uid, is_series_in_config',
    [
        ('eatswithreason1234', '4026', True),
        ('eatswithreason1234', '4026', False),
    ],
)
async def test_description_from_reason(
        local_services,
        taxi_coupons,
        promocode,
        yandex_uid,
        taxi_config,
        is_series_in_config,
):
    if is_series_in_config:
        taxi_config.set_values(
            {'COUPONS_DESCRIPTION_FROM_REASON_FOR_SERIES': ['eatspromocode2']},
        )
    else:
        taxi_config.set_values(
            {'COUPONS_DESCRIPTION_FROM_REASON_FOR_SERIES': []},
        )

    local_services.add_card()
    application_name = 'eats_iphone'
    request = util.mock_request_list(
        [yandex_uid], application_name, services=['eats'],
    )
    response = await util.make_list_request(taxi_coupons, request)
    assert response.status_code == 200

    text = response.json()['coupons'][0]['action']['descriptions'][0]['text']
    if is_series_in_config:
        assert text == 'Ресторан Большая кувшинка извиняется'
    else:
        assert text == '2 заказов в ресторане (описание из серии)'
