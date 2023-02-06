# pylint: disable=too-many-lines
import datetime
import json

import pytest

from tests_coupons import util

YANDEX_UID = '4001'


@pytest.mark.config(COUPONS_SERVICE_ENABLED=False)
async def test_coupons_disabled(taxi_coupons):
    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request([YANDEX_UID], YANDEX_UID, 'coupon'),
    )
    assert response.status_code == 429


async def test_4xx(taxi_coupons):
    response = await util.make_activate_request(taxi_coupons, data=None)
    assert response.status_code == 400

    response = await util.make_activate_request(taxi_coupons, data={})
    assert response.status_code == 400


@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.config(
    UAFS_COUPONS_FETCH_GLUE=True, UAFS_COUPONS_USE_GLUE_IN_TAXI_STATS=True,
)
async def test_simple_200(load_json, taxi_coupons, local_services, mockserver):
    @mockserver.json_handler('/user-statistics/v1/orders')
    def _mock_user_statistics(request):
        assert request.json == load_json(
            'simple_200_expected_statistics_request.json',
        )
        assert 'X-Ya-Service-Ticket' in request.headers
        return load_json('simple_200_statistics_response.json')

    @mockserver.handler('/uantifraud/v1/glue')
    def _mock_uafs(request):
        assert request.json == {
            'sources': ['taxi', 'eats'],
            'passport_uid': '4001',
        }
        return mockserver.make_response(
            json.dumps(
                {
                    'sources': {
                        'taxi': {'passport_uids': ['puid1', 'puid2', 'puid3']},
                        'eats': {'passport_uids': ['eats_uid1', 'eats_uid2']},
                    },
                },
            ),
            200,
        )

    local_services.add_card()
    expected = load_json('expected_activate_responses.json')
    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request([YANDEX_UID], YANDEX_UID, 'MYYACODE'),
    )
    assert response.status_code == 200
    assert expected['invalid'] == response.json()

    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request([YANDEX_UID], YANDEX_UID, 'firstpromocode'),
    )
    assert response.status_code == 200
    assert expected['valid'] == response.json()


@pytest.mark.now('2019-03-06T11:30:00+0300')
async def test_percent_100(load_json, taxi_coupons, local_services):
    local_services.add_card()
    expected = load_json('expected_activate_responses.json')
    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request([YANDEX_UID], YANDEX_UID, 'promocode100'),
    )
    assert response.status_code == 200
    assert expected['valid100'] == response.json()


@pytest.mark.parametrize('collections_tag', util.USER_COUPONS_DB_MODE_PARAMS)
@pytest.mark.now('2019-03-06T11:30:00+0300')
async def test_activated_promo(
        taxi_coupons, mongodb, local_services, collections_tag,
):
    collections = util.tag_to_user_coupons_for_write(mongodb, collections_tag)

    local_services.add_card()
    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request([YANDEX_UID], YANDEX_UID, 'firstpromocode'),
    )
    assert response.status_code == 200
    response_coupon = response.json()['coupon']
    assert not response_coupon['selected']
    assert response_coupon['status'] == 'valid'

    for collection in collections:
        user_coupons = collection.find_one(
            {'yandex_uid': YANDEX_UID, 'brand_name': 'yataxi'},
        )
        codes = [promo['code'] for promo in user_coupons['promocodes']]

        expected_codes = ['firstpromocode', 'secondpromocode']
        assert set(expected_codes) == set(codes)

    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request(['401', YANDEX_UID], '401', 'firstpromocode'),
    )
    assert response.status_code == 200
    response_coupon = response.json()['coupon']
    assert not response_coupon['selected']
    assert response_coupon['status'] == 'valid'

    for collection in collections:
        assert not collection.find_one(
            {'yandex_uid': '401', 'brand_name': 'yataxi'},
        )

    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request(['401', YANDEX_UID], '401', 'secondpromocode'),
    )
    assert response.status_code == 200
    response_coupon = response.json()['coupon']
    assert response_coupon['selected']
    assert response_coupon['status'] == 'valid'

    for collection in collections:
        assert not collection.find_one(
            {'yandex_uid': '401', 'brand_name': 'yataxi'},
        )


@pytest.mark.parametrize('collections_tag', util.USER_COUPONS_DB_MODE_PARAMS)
async def test_invalid(taxi_coupons, mongodb, local_services, collections_tag):
    collections = util.tag_to_user_coupons_for_write(mongodb, collections_tag)

    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request([YANDEX_UID], YANDEX_UID, 'MYYACODE'),
    )
    assert response.status_code == 200
    response_coupon = response.json()['coupon']
    assert not response_coupon['selected']
    assert response_coupon['status'] == 'invalid'

    for collection in collections:
        user_coupons = collection.find_one(
            {'yandex_uid': YANDEX_UID, 'brand_name': 'yataxi'},
        )
        codes = [promo['code'] for promo in user_coupons['promocodes']]

        expected_codes = ['firstpromocode', 'secondpromocode']
        assert set(expected_codes) == set(codes)


@pytest.mark.parametrize('collections_tag', util.USER_COUPONS_DB_MODE_PARAMS)
@pytest.mark.now('2019-03-06T11:30:00+0300')
async def test_existing(
        taxi_coupons, mongodb, local_services, collections_tag,
):
    local_services.add_card()
    collections = util.tag_to_user_coupons_for_write(mongodb, collections_tag)

    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request([YANDEX_UID], YANDEX_UID, 'validpromocode'),
    )
    assert response.status_code == 200
    response_coupon = response.json()['coupon']
    assert response_coupon['selected']
    assert response_coupon['status'] == 'valid'

    for collection in collections:
        user_coupons = collection.find_one(
            {'yandex_uid': YANDEX_UID, 'brand_name': 'yataxi'},
        )
        codes = [promo['code'] for promo in user_coupons['promocodes']]

        expected_codes = [
            'firstpromocode',
            'secondpromocode',
            'validpromocode',
        ]
        assert set(expected_codes) == set(codes)


@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.parametrize(
    'coupon, is_unique', [('validpromocode', False), ('promocode100', True)],
)
async def test_new(taxi_coupons, mongodb, local_services, coupon, is_unique):
    local_services.add_card()
    response = await util.make_activate_request(
        taxi_coupons, data=util.mock_request(['4004', '4002'], '4004', coupon),
    )
    assert response.status_code == 200
    response_coupon = response.json()['coupon']
    assert response_coupon['selected']
    assert response_coupon['status'] == 'valid'

    user_coupons = mongodb.user_coupons.find_one(
        {'yandex_uid': '4004', 'brand_name': 'yataxi'},
    )
    codes = [promo['code'] for promo in user_coupons['promocodes']]
    assert set(codes) == {coupon}

    promocode_doc = user_coupons['promocodes'][0]
    assert 'series_id' in promocode_doc
    if is_unique:
        assert 'promocode_id' in promocode_doc


SERVICES_TITLES_CONFIG = {
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
}


@pytest.mark.now('2017-03-13T11:30:00+0300')
# pass as parameters for eats_local_server mock
@pytest.mark.parametrize(
    (
        'valid',
        'eats_result_code',
        'error_code',
        'promocode_type',
        'services',
        'yandex_uids',
    ),
    [
        (False, 500, None, 'fixed', ['eats'], [YANDEX_UID]),
        (False, 200, 'not_found', 'fixed', ['eats'], [YANDEX_UID]),
    ],
)
@pytest.mark.parametrize(
    'ui_titles_config_not_empty',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                COUPONS_SERVICES_UI_TITLES=SERVICES_TITLES_CONFIG,
            ),
            id='titles_config_not_empty',
        ),
        pytest.param(False, id='titles_config_empty'),
    ],
)
async def test_activate_basic_invalid(
        taxi_coupons,
        mongodb,
        local_services,
        eats_local_server,
        eats_result_code,
        ui_titles_config_not_empty,
):
    coupon_code = 'FOO1111119'

    request = util.mock_request([YANDEX_UID], YANDEX_UID, coupon_code)
    response = await util.make_activate_request(taxi_coupons, data=request)
    assert response.status_code == 200
    content = response.json()

    expected_code = 'ERROR_INVALID_CODE'
    if ui_titles_config_not_empty:
        expected_code = (
            'ERROR_EXTERNAL_INVALID_CODE'
            if eats_result_code == 200
            else 'ERRROR_EXTERNAL_EATS_SERVICE_FAIL'
        )

    assert content['coupon']['error']['code'] == expected_code

    entry = mongodb.coupon_frauders.find_one(YANDEX_UID)
    assert entry is not None
    assert entry == {
        '_id': YANDEX_UID,
        'coupons': [coupon_code.lower()],
        'created': datetime.datetime(2017, 3, 13, 8, 30),
    }

    entry = mongodb.coupons_antispam.find_one('couponcheck_series_foo')
    assert entry == {
        '_id': 'couponcheck_series_foo',
        'attempt_timestamps': [datetime.datetime(2017, 3, 13, 8, 30)],
        'ignore_tag': None,
        'updated': datetime.datetime(2017, 3, 13, 8, 30),
    }


@pytest.mark.now('2017-03-13T11:30:00+0300')
async def test_activate_basic_fraud_ban(taxi_coupons, mongodb, local_services):
    for index in range(11):
        request = util.mock_request(
            [YANDEX_UID], YANDEX_UID, f'FOO{index:06d}',
        )
        response = await util.make_activate_request(taxi_coupons, data=request)
        assert response.status_code == 200
        content = response.json()
        assert content['coupon']['error']['code'] == 'ERROR_INVALID_CODE'

    request = util.mock_request([YANDEX_UID], YANDEX_UID, 'FOO123455')
    response = await util.make_activate_request(taxi_coupons, data=request)
    assert response.status_code == 429


@pytest.mark.now('2017-03-13T11:30:00+0300')
# pass as parameters for eats_local_server mock
@pytest.mark.parametrize(
    (
        'expected_code',
        'valid',
        'eats_result_code',
        'error_code',
        'promocode_type',
        'services',
        'yandex_uids',
    ),
    [
        pytest.param(
            'ERRROR_EXTERNAL_EATS_SERVICE_FAIL',
            False,
            500,
            None,
            'fixed',
            ['eats'],
            [YANDEX_UID],
            id='500',
        ),
        pytest.param(
            'ERROR_EXTERNAL_INVALID_CODE',
            False,
            200,
            'not_found',
            'fixed',
            ['eats'],
            [YANDEX_UID],
            id='validation failed',
        ),
        pytest.param(
            'ERROR_EXTERNAL_VALIDATION_FAILED',
            True,
            200,
            None,
            'fixed',
            ['space-taxi'],
            [YANDEX_UID],
            id='promocode service not in exp',
        ),
    ],
)
@pytest.mark.parametrize(
    'ui_titles_config_not_empty',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                COUPONS_SERVICES_UI_TITLES=SERVICES_TITLES_CONFIG,
            ),
            id='titles_config_not_empty',
        ),
        pytest.param(False, id='titles_config_empty'),
    ],
)
@pytest.mark.filldb(coupons_antispam='bruteforce')
async def test_activate_basic_fraud_ban_when_bruteforcing(
        taxi_coupons,
        mongodb,
        local_services,
        eats_local_server,
        eats_result_code,
        expected_code,
        ui_titles_config_not_empty,
):
    for index in range(2):
        request = util.mock_request(
            [YANDEX_UID], YANDEX_UID, f'FOO{index:06d}',
        )
        response = await util.make_activate_request(taxi_coupons, data=request)
        assert response.status_code == 200
        content = response.json()

        if not ui_titles_config_not_empty:
            expected_code = 'ERROR_INVALID_CODE'

        assert content['coupon']['error']['code'] == expected_code

    request = util.mock_request([YANDEX_UID], YANDEX_UID, 'FOO123455')
    response = await util.make_activate_request(taxi_coupons, data=request)
    assert response.status_code == 429

    entry = mongodb.coupon_frauders.find_one(YANDEX_UID)
    assert entry is not None
    assert entry['created'] == datetime.datetime(2017, 6, 11, 8, 30)


@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.filldb(promocode_usages2='user_limit')
async def test_activate_user_limit_exceeded(
        taxi_coupons, mongodb, local_services,
):
    request = util.mock_request([YANDEX_UID], YANDEX_UID, 'firstpromocode')
    response = await util.make_activate_request(taxi_coupons, data=request)
    content = response.json()['coupon']

    assert content['error']['code'] == 'ERROR_USER_LIMIT_EXCEEDED'


@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.filldb(promocode_usages='count_exceeded')
async def test_activate_count_exceeded(taxi_coupons, mongodb, local_services):
    request = util.mock_request([YANDEX_UID], YANDEX_UID, 'secondpromocode')
    response = await util.make_activate_request(taxi_coupons, data=request)
    content = response.json()['coupon']

    assert content['error']['code'] == 'ERROR_COUNT_EXCEEDED'


@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.filldb(promocode_series='first_usage_by_classes')
async def test_activate_first_usage_by_classes_mock(
        taxi_coupons, mongodb, local_services, user_statistics_services,
):
    user_statistics_services.set_detailed_rides(83)
    user_statistics_services.set_phone_id(util.PHONE_ID)

    request = util.mock_request([YANDEX_UID], YANDEX_UID, 'firstpromocode')
    response = await util.make_activate_request(taxi_coupons, data=request)
    content = response.json()['coupon']

    assert content['error']['code'] == 'ERROR_FIRST_RIDE_BY_CLASSES'


@pytest.mark.now('2017-03-13T11:30:00+0300')
async def test_activate_first_limit_exc_by_rides(
        taxi_coupons, mongodb, local_services, user_statistics_services,
):
    user_statistics_services.user_statistics = {
        'data': [
            {
                'identity': {'type': 'phone_id', 'value': util.PHONE_ID},
                'counters': [
                    {
                        'properties': [
                            {'name': 'tariff_class', 'value': tariff_class},
                            {'name': 'payment_type', 'value': 'cash'},
                        ],
                        'value': 1,
                        'counted_from': '2020-09-01T11:01:55+0000',
                        'counted_to': '2020-09-03T09:24:18.807+0000',
                    }
                    for tariff_class in ('econom', 'vip')
                ],
            },
        ],
    }
    request = util.mock_request([YANDEX_UID], YANDEX_UID, 'firstpromocode')
    response = await util.make_activate_request(taxi_coupons, data=request)
    content = response.json()['coupon']

    assert content['error']['code'] == 'ERROR_FIRST_LIMIT_EXCEEDED'


@pytest.mark.now('2017-03-13T11:30:00+0300')
async def test_activate_first_limit_exc_by_device_id(
        taxi_coupons, mongodb, local_services_card, user_statistics_services,
):
    user_statistics_services.set_phone_id(util.PHONE_ID)
    user_statistics_services.set_total_rides(0)
    user_statistics_services.add_counter(
        identity={'type': 'device_id', 'value': 'device_id'}, value=9001,
    )

    request = util.mock_request([YANDEX_UID], YANDEX_UID, 'firstpromocode')
    response = await util.make_activate_request(taxi_coupons, data=request)
    content = response.json()['coupon']

    assert content['error']['code'] == 'ERROR_FIRST_LIMIT_EXCEEDED'


@pytest.mark.parametrize(
    'app_name, empty_device_id_ignored',
    [('iphone', True), ('android', False)],
)
@pytest.mark.config(
    DISABLE_DEVICE_ID_CHECK_BY_VERSION={
        'moscow': {'iphone': {'from': [4, 47, 0], 'to': [4, 47, 0]}},
    },
)
@pytest.mark.parametrize('allow_empty_device_id', [True, False])
@pytest.mark.now('2017-03-13T11:30:00+0300')
async def test_no_device_id(
        experiments3,
        taxi_coupons,
        mongodb,
        local_services,
        app_name,
        empty_device_id_ignored,
        allow_empty_device_id,
):
    experiments3.add_experiment(
        match={'predicate': {'type': 'true'}, 'enabled': True},
        name='coupons_allow_empty_device_id',
        consumers=['coupons/check'],
        clauses=[
            {
                'value': {'enabled': True},
                'predicate': {
                    'init': {
                        'arg_name': 'platform_version',
                        'arg_type': 'version',
                        'value': (
                            '11.1.0' if allow_empty_device_id else '12.0.0'
                        ),
                    },
                    'type': 'gte',
                },
            },
        ],
        default_value={'enabled': False},
    )

    # need to do it after experiments3.add_experiment
    await taxi_coupons.invalidate_caches()

    local_services.add_card()
    request = util.mock_request(
        ['4010'], '4010', 'firstpromocode', app_name=app_name,
    )
    local_services.user_api.pop('device_id')
    response = await util.make_activate_request(taxi_coupons, data=request)
    assert response.status_code == 200
    content = response.json()['coupon']
    assert content['status'] == (
        'valid'
        if empty_device_id_ignored or allow_empty_device_id
        else 'invalid'
    )


@pytest.mark.parametrize(
    'code, error_type, description',
    [
        pytest.param(
            'MEAL777',
            'ERROR_LAVKA_PROMOCODE',
            'Промокод можно использовать только в Лавке',
            id='upper case check',
        ),
        pytest.param(
            'meal888',
            'ERROR_LAVKA_PROMOCODE',
            'Промокод можно использовать только в Лавке',
            id='upper case check',
        ),
        pytest.param(
            'eda123456',
            'ERROR_LAVKA_PROMOCODE',
            'Промокод можно использовать только в Лавке',
            id='lower case check',
        ),
        pytest.param(
            'EDA123456',
            'ERROR_LAVKA_PROMOCODE',
            'Промокод можно использовать только в Лавке',
            id='lower case check',
        ),
    ],
)
@pytest.mark.config(COUPONS_LAVKA_PREFIXES=['eda', 'MEAL'])
async def test_lavka_prefixes(
        load_json, taxi_coupons, local_services, code, error_type, description,
):
    response = await util.make_activate_request(
        taxi_coupons, data=util.mock_request([YANDEX_UID], YANDEX_UID, code),
    )
    assert response.status_code == 200

    coupon = response.json()['coupon']
    assert coupon['code'] == code.lower()
    assert coupon['status'] == 'invalid'
    assert not coupon['selected']

    error = coupon['error']
    assert error['code'] == error_type
    assert error['description'] == description


@pytest.mark.now('2019-03-06T11:30:00+0300')
async def test_metrics_exist(
        load_json, taxi_coupons, local_services, taxi_coupons_monitor,
):
    local_services.add_card()
    expected = load_json('expected_activate_responses.json')
    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request([YANDEX_UID], YANDEX_UID, 'MYYACODE'),
    )
    assert response.status_code == 200
    assert expected['invalid'] == response.json()

    metrics_name = 'coupons-activate-statistics'
    metrics = await taxi_coupons_monitor.get_metrics(metrics_name)

    assert metrics_name in metrics.keys()


BILLING_SERVICE_NAME_MAP_BY_BRAND = {
    '__default__': 'unknown',
    'yataxi': 'card',
    'yango': 'card',
    'yauber': 'uber',
}


@pytest.mark.config(
    BILLING_SERVICE_NAME_MAP_BY_BRAND=BILLING_SERVICE_NAME_MAP_BY_BRAND,
    APPLICATION_MAP_BRAND=util.APPLICATION_MAP_BRAND,
    COUPONS_CARDSTORAGE_REQUESTS_PARAMS={
        '__default__': {
            'timeout_ms': 10000,
            'retries': 3,
            'pass_renew_after': False,
        },
        'couponactivate': {
            'timeout_ms': 12000,
            'retries': 2,
            'pass_renew_after': True,
        },
    },
)
@pytest.mark.parametrize(
    'app_name',
    ['iphone', 'yango_android', 'uber_iphone', 'mobileweb_android'],
)
async def test_cardstorage_request(
        taxi_coupons, mockserver, local_services, app_name,
):
    local_services.check_service_type(
        BILLING_SERVICE_NAME_MAP_BY_BRAND,
        util.APPLICATION_MAP_BRAND,
        app_name,
    )

    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request(
            [YANDEX_UID], YANDEX_UID, 'firstpromocode', app_name=app_name,
        ),
    )
    assert response.status_code == 200

    assert local_services.mock_cardstorage.has_calls

    util.check_cardstorage_requests(
        local_services.cardstorage_requests,
        expected_num_requests=2,
        expected_num_requests_wo_renew_after=1,
        expected_timeout_ms=12000,
    )


@pytest.mark.now('2019-03-06T11:30:00+0300')
async def test_services(load_json, taxi_coupons, local_services):
    local_services.add_card()

    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request([YANDEX_UID], YANDEX_UID, 'servicespromocode'),
    )
    assert response.status_code == 200
    response_json = response.json()

    expected = load_json('expected_activate_responses.json')[
        'valid_with_services'
    ]
    paths_to_sort = {'coupon.services'}
    actual_json = util.sort_json(response_json, paths_to_sort)
    expected_json = util.sort_json(expected, paths_to_sort)
    assert actual_json == expected_json


@pytest.mark.now('2019-03-06T11:30:00+0300')
async def test_empty_services(load_json, taxi_coupons, local_services):
    local_services.add_card()

    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request(
            [YANDEX_UID], YANDEX_UID, 'emptyservicespromocode',
        ),
    )
    assert response.status_code == 200
    response_json = response.json()

    expected = load_json('expected_activate_responses.json')[
        'invalid_with_empty_services'
    ]
    assert response_json == expected


@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.parametrize(
    'code,payment_method,method_id,valid_payment_method',
    [
        # "payment_methods": ["applepay", "cash", "card"]
        ('paymentmethods1', 'applepay', None, True),
        ('paymentmethods1', 'cash', None, True),
        ('paymentmethods1', 'card', 'card_id', True),
        ('paymentmethods1', 'card', 'ya_card_id', True),
        ('paymentmethods1', 'googlepay', None, False),
        ('paymentmethods1', 'coop_account', 'business-123', False),
        # "payment_methods": ["business_account"]
        ('bizpaymentmethod1', 'coop_account', 'business-123', True),
        ('bizpaymentmethod1', 'coop_account', 'family-123', False),
        ('bizpaymentmethod1', 'coop_account', 'some-123', False),
        # "payment_methods": []
        ('emptypaymentmethods1', 'coop_account', 'some-123', True),
    ],
)
async def test_activate_payment_methods(
        taxi_coupons,
        local_services,
        code,
        payment_method,
        method_id,
        valid_payment_method,
):
    local_services.add_card_and_ya_card()
    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request(
            [YANDEX_UID],
            YANDEX_UID,
            code,
            payment_type=payment_method,
            payment_method_id=method_id,
        ),
    )
    assert response.status_code == 200
    content = response.json()
    assert (
        content['coupon']['status'] == 'valid'
        if valid_payment_method
        else 'invalid'
    )

    description_string = 'Сработает на следующую поездку по любому тарифу'
    util.check_coupon(
        code, description_string, valid_payment_method, content['coupon'],
    )


PROMOCODE_PATTERNS_CONFIG = [
    {
        'application_mode': 'promocodes_in_superapp_mvp',
        'pattern': '^[a-zA-Z0-9-]{4,20}$',
    },
]


@pytest.mark.config(COUPONS_PROMOCODE_PATTERNS=PROMOCODE_PATTERNS_CONFIG)
# pass as parameters for eats_local_server mock
@pytest.mark.parametrize(
    (
        'valid',
        'eats_result_code',
        'error_code',
        'promocode_type',
        'services',
        'yandex_uids',
    ),
    [(True, 200, None, 'fixed', ['eats'], [YANDEX_UID])],
)
@pytest.mark.parametrize('code', ['birthday-i6vejehag', 'birthdayi6vejehag'])
@pytest.mark.parametrize(
    'titles_config_not_empty',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(
                COUPONS_SERVICES_UI_TITLES=SERVICES_TITLES_CONFIG,
            ),
            id='titles_config_not_empty',
        ),
        pytest.param(False, id='titles_config_empty'),
    ],
)
@pytest.mark.now('2019-03-06T11:30:00+0300')
async def test_regex_pattern(
        load_json,
        taxi_coupons,
        local_services,
        eats_local_server,
        valid,
        eats_result_code,
        error_code,
        promocode_type,
        services,
        yandex_uids,
        titles_config_not_empty,
        code,
):
    local_services.add_card()

    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request(yandex_uids, yandex_uids[0], code),
    )

    assert response.status_code == 200

    coupon = response.json()['coupon']
    assert coupon['code'] == code

    is_superapp_promocode = '-' in code

    if is_superapp_promocode and not titles_config_not_empty:
        assert coupon['status'] != 'valid'
        assert coupon['error']['code'] == 'ERROR_INVALID_CODE'
    else:
        assert coupon['status'] == 'valid'


@pytest.mark.config(
    COUPONS_USER_AGENT_RESTRICTIONS={
        'hon30': '^.+\\(HUAWEI; (BMH|EBG)-AN10\\)$',
    },
)
@pytest.mark.parametrize(
    'code, need_check_ua',
    [
        pytest.param('prefixhonsuffix', False),
        pytest.param('prefixhon30suffix', False),
        pytest.param('hon30', False),
        pytest.param('hon30suffix', True),
    ],
)
@pytest.mark.parametrize(
    'user_agent, ua_match',
    [
        pytest.param(
            'yandex-taxi/3.151.0.121403 Android/9 (HUAWEI; CLT-L29)',
            False,
            id='other_huawei',
        ),
        pytest.param(
            'yandex-taxi/3.113.0.85658 Android/9 (OnePlus; ONEPLUS A5010)',
            False,
            id='other_android',
        ),
        pytest.param(
            'ru.yandex.taxi/9.99.9 (iPhone; x86_64; iOS 12.2; Darwin)',
            False,
            id='iphone',
        ),
        pytest.param(
            'yandex-taxi/3.151.0.121403 Android/9 (HUAWEI; BMH-AN10)',
            True,
            id='honor_30',
        ),
        pytest.param(
            'yandex-taxi/3.151.0.121403 Android/9 (HUAWEI; EBG-AN10)',
            True,
            id='honor_30_pro',
        ),
    ],
)
@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.skip(reason='flapping test, will be fixed in TAXIBACKEND-41551')
async def test_reserve_user_agent(
        taxi_coupons,
        mongodb,
        local_services,
        code,
        need_check_ua,
        user_agent,
        ua_match,
):
    request = util.mock_request(['4001'], '4001', code)

    local_services.add_card()
    response = await util.make_activate_request(
        taxi_coupons, data=request, headers={'User-Agent': user_agent},
    )

    assert response.status_code == 200
    content = response.json()['coupon']

    if not need_check_ua or ua_match:
        assert content['status'] == 'valid'
    else:
        assert content['status'] == 'invalid'
        assert (
            content['error']['code'] == 'ERROR_MANUAL_ACTIVATION_IS_REQUIRED'
        )


@pytest.mark.parametrize(
    'yandex_uids,current_yandex_uid,version_in,version_out',
    [
        pytest.param(['4001'], '4001', None, '4001:3', id='none_version_in'),
        pytest.param(
            ['4001'], '4001', '4001:1', '4001:3', id='update_version',
        ),
        pytest.param(
            ['4001'], '4001', '4001:2', '4001:3', id='update_version',
        ),
        pytest.param(['4002'], '4002', None, '4002:1', id='new_version'),
        pytest.param(
            ['4001', '4002'],
            '4002',
            '4001:1',
            '4001:2,4002:1',
            id='new_version',
        ),
    ],
)
@pytest.mark.filldb(user_coupons='version')
@pytest.mark.now('2019-03-06T11:30:00+0300')
async def test_version(
        taxi_coupons,
        local_services,
        mongodb,
        yandex_uids,
        current_yandex_uid,
        version_in,
        version_out,
):
    if version_in:
        encode_version = util.encode_version(version_in)
    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request(
            yandex_uids,
            current_yandex_uid,
            'firstpromocode',
            version=encode_version if version_in else None,
        ),
    )
    assert response.status == 200
    assert util.decode_version(response.json()['version']) == version_out


@pytest.mark.now('2017-03-06T11:30:00+0300')
async def test_volatile_series_value(load_json, taxi_coupons, local_services):
    local_services.add_card()
    expected = load_json('expected_activate_responses.json')
    response = await util.make_activate_request(
        taxi_coupons,
        data=util.mock_request([YANDEX_UID], YANDEX_UID, 'foopromocode'),
    )
    assert response.status_code == 200
    assert expected['volatile'] == response.json()


@pytest.mark.now('2017-03-06T11:30:00+0300')
@pytest.mark.config(
    COUPONS_EXTERNAL_VALIDATION_SERVICES=['eats'],
    UAFS_COUPONS_FETCH_GLUE=True,
    UAFS_COUPONS_PASS_GLUE_TO_EATS_COUPONS=True,
)
@pytest.mark.config(
    COUPONS_EXTERNAL_SERVICES_FORWARD_ERRORS={
        'forward_codes_for_services': ['eats'],
        'forward_description_for_services': ['eats'],
    },
)
async def test_new_param_to_eats_coupons(
        load_json, taxi_coupons, local_services, mockserver,
):
    local_services.add_card()

    @mockserver.json_handler('/eats-coupons/internal/v1/coupons/validate')
    def mock_eats_coupons_validate(req):
        assert req.json['source_handler'] == 'activate'
        return mockserver.make_response(
            json.dumps(
                {
                    'valid': False,
                    'valid_any': False,
                    'descriptions': [],
                    'details': [],
                    'error_description': 'Some error from eats validator',
                },
            ),
            status=200,
        )

    @mockserver.json_handler('/uantifraud/v1/glue')
    def _mock_uafs(req):
        return {
            'sources': {
                'taxi': {'passport_uids': ['taxi_uid1', 'taxi_uid2']},
                'eats': {
                    'passport_uids': ['eats_uid1', 'eats_uid2', 'eats_uid3'],
                },
            },
        }

    req = util.mock_request([YANDEX_UID], YANDEX_UID, 'edapromic2')
    req['service'] = 'eats'
    await util.make_activate_request(taxi_coupons, data=req)
    assert mock_eats_coupons_validate.times_called == 1
