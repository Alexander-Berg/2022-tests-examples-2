import json

import pytest

from user_api_switch_parametrize import PROTOCOL_SWITCH_TO_USER_API


@pytest.fixture
def couponcheck_services(mockserver):
    class context:
        uid = '123'
        expected_zone_classes = set()

    @mockserver.json_handler('/blackbox')
    def mock_blackbox(request):
        return {
            'uid': {'value': context.uid},
            'status': {'value': 'VALID'},
            'oauth': {'scope': 'yataxi:read yataxi:write yataxi:pay'},
            'aliases': {'10': 'phonish'},
            'phones': [
                {
                    'attributes': {'102': '+71111111111', '107': '1'},
                    'id': '1111',
                },
            ],
        }

    @mockserver.json_handler('/coupons/v1/couponcheck')
    def mock_couponcheck(request):
        request_data = json.loads(request.get_data())
        req_classes = [zc['class'] for zc in request_data['zone_classes']]
        assert set(req_classes) == context.expected_zone_classes
        return {
            'valid': True,
            'format_currency': True,
            'descr': 'test description',
            'details': ['some_detail'],
            'value': 100,
            'currency_code': 'rub',
        }

    return context


def check_test_response(response):
    assert response.status_code == 200
    data = response.json()
    assert data['valid'] is True
    assert data['descr'] == 'test description'


@pytest.mark.config(
    ALL_CATEGORIES=['econom', 'business', 'comfortplus', 'vip', 'minivan'],
    TARIFF_CATEGORIES_VISIBILITY={'__default__': {}},
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={
        'business': {'iphone': {'version': [5, 1, 0]}},
    },
)
def test_class_hidden_by_app(taxi_protocol, couponcheck_services):
    """
    Checks usage of TARIFF_CATEGORIES_ENABLED_BY_VERSION.
    Iphone version in TARIFF_CATEGORIES_ENABLED_BY_VERSION should be greater
    than User-Agent in request.
    """

    couponcheck_services.expected_zone_classes = {
        'econom',
        'comfortplus',
        'vip',
        'minivan',
    }
    couponcheck_services.uid = '007'

    response = taxi_protocol.post(
        '3.0/couponcheck',
        json={
            'id': '007000000000041111111111111111111',
            'city': 'Москва',
            'coupon': 'serialess000001',
            'format_currency': True,
            'payment': {'type': 'cash'},
        },
        bearer='test_token',
        headers={
            'User-Agent': (
                'ru.yandex.taxi.inhouse/4.99.8769 '
                '(iPhone; iPhone7,2; iOS 11.0; Darwin)'
            ),
        },
    )

    check_test_response(response)


yataxi_categories = [
    'express',
    'econom',
    'business',
    'comfortplus',
    'vip',
    'minivan',
    'business2',
    'pool',
    'drivers_pool',
    'child_tariff',
    'start',
    'standart',
]
yauber_categories = ['uberx', 'uberselect', 'uberblack', 'uberkids']


@pytest.mark.config(
    ALL_CATEGORIES=yataxi_categories + yauber_categories,
    UBER_CATEGORIES=yauber_categories,
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': yataxi_categories,
        'yauber': yauber_categories,
    },
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {
            'business': {
                'hide_experiment': 'business2',
                'visible_by_default': True,
                'use_legacy_experiments': True,
            },
            'comfortplus': {
                'hide_experiment': 'business2',
                'visible_by_default': False,
                'use_legacy_experiments': True,
            },
            'business2': {
                'show_experiment': 'business2',
                'visible_by_default': False,
                'use_legacy_experiments': True,
            },
            'child_tariff': {
                'show_experiment': 'child_tariff4',
                'use_legacy_experiments': True,
                'visible_by_default': False,
            },
            'pool': {
                'show_experiment': 'pool',
                'visible_by_default': True,
                'use_legacy_experiments': True,
            },
            'start': {
                'visible_by_default': False,
                'use_legacy_experiments': True,
            },
            'express': {
                'visible_by_default': True,
                'use_legacy_experiments': True,
            },
        },
    },
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
)
@pytest.mark.filldb(tariff_settings='class_not_visible')
@pytest.mark.user_experiments('child_tariff4')
@pytest.mark.user_experiments('business2')
def test_class_not_visible_legacy(taxi_protocol, couponcheck_services):
    """
    Checks usage of TARIFF_CATEGORIES_VISIBILITY while checking coupon with
    legacy experiments (user_experiments). Lower you will find same test with
    experiments3.0

    Checks this code:
      if (!s.show_experiment.empty() && experiments.count(s.show_experiment))
        return true;
      if (!s.hide_experiment.empty() && experiments.count(s.hide_experiment))
        return false;
      return s.visible_by_default;


    coupon 'allcategories':
        express, econom, business, comfortplus, vip, minivan, business2,
        pool, drivers_pool, child_tariff, start, standart,
        uberx

    tariff_settings: express, business, comfortplus, business2, vip,
                    econom, child_tariff, minivan, start, pool, poputka, uberx

    tariff_settings & coupon: express, econom, business, comfortplus, vip,
                            minivan, business2, pool, child_tariff, start,
                            uberx

    tariff_settings ^ coupon: drivers_pool, standart, poputka

    showed:
        express: tariff_settings + coupon + visible_by_default (True)
        econom: tariff_settings + coupon
        vip: tariff_settings + coupon
        minivan: tariff_settings + coupon
        business2: tariff_settings + coupon + show_experiment (active)
        child_tariff: tariff_settings + coupon + show_experiment (active)

    hidden:
        business: tariff_settings + coupon + hide_experiment (active)
        comfortplus: tariff_settings + coupon + hide_experiment (active)
        start: tariff_settings + coupon + visible_by_default (False)
        pool: tariff_settings + coupon + show_experiment (Inactive)
        drivers_pool: tariff_settings (No) + coupon
        standart: tariff_settings (No) + coupon
        poputka: tariff_settings + coupon (No)
        uberx: Uber
    """

    couponcheck_services.expected_zone_classes = {
        'minivan',
        'vip',
        'business2',
        'econom',
        'child_tariff',
        'express',
    }
    couponcheck_services.uid = '007'
    response = taxi_protocol.post(
        '3.0/couponcheck',
        json={
            'id': '007000000000041111111111111111111',
            'city': 'Москва',
            'coupon': 'allyandexoneuber',
            'format_currency': True,
            'payment': {'type': 'cash'},
        },
        bearer='test_token',
    )

    check_test_response(response)


@pytest.mark.config(
    ALL_CATEGORIES=yataxi_categories + yauber_categories,
    UBER_CATEGORIES=yauber_categories,
    APPLICATION_BRAND_CATEGORIES_SETS={
        '__default__': yataxi_categories,
        'yauber': yauber_categories,
    },
    TARIFF_CATEGORIES_VISIBILITY={
        '__default__': {
            'business': {
                'hide_experiment': 'business2',
                'visible_by_default': True,
            },
            'comfortplus': {
                'hide_experiment': 'business2',
                'visible_by_default': False,
            },
            'business2': {
                'show_experiment': 'business2',
                'visible_by_default': False,
            },
            'child_tariff': {
                'show_experiment': 'child_tariff4',
                'visible_by_default': False,
            },
            'pool': {'show_experiment': 'pool', 'visible_by_default': True},
            'start': {'visible_by_default': False},
            'express': {'visible_by_default': True},
        },
    },
    TARIFF_CATEGORIES_ENABLED_BY_VERSION={},
)
@pytest.mark.filldb(tariff_settings='class_not_visible')
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='child_tariff4',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
@pytest.mark.experiments3(
    is_config=True,
    match={'predicate': {'type': 'true'}, 'enabled': True},
    name='business2',
    consumers=['tariff_visibility_helper'],
    clauses=[
        {
            'title': 'a',
            'value': {'enabled': True},
            'predicate': {'type': 'true'},
        },
    ],
)
def test_class_not_visible_exp3(taxi_protocol, couponcheck_services):
    """
    Checks usage of TARIFF_CATEGORIES_VISIBILITY while checking coupon

    Checks this code:
      if (!s.show_experiment.empty() && experiments.count(s.show_experiment))
        return true;
      if (!s.hide_experiment.empty() && experiments.count(s.hide_experiment))
        return false;
      return s.visible_by_default;


    coupon 'allcategories':
        express, econom, business, comfortplus, vip, minivan, business2,
        pool, drivers_pool, child_tariff, start, standart,
        uberx

    tariff_settings: express, business, comfortplus, business2, vip,
                    econom, child_tariff, minivan, start, pool, poputka, uberx

    tariff_settings & coupon: express, econom, business, comfortplus, vip,
                            minivan, business2, pool, child_tariff, start,
                            uberx

    tariff_settings ^ coupon: drivers_pool, standart, poputka

    showed:
        express: tariff_settings + coupon + visible_by_default (True)
        econom: tariff_settings + coupon
        vip: tariff_settings + coupon
        minivan: tariff_settings + coupon
        business2: tariff_settings + coupon + show_experiment (active)
        child_tariff: tariff_settings + coupon + show_experiment (active)

    hidden:
        business: tariff_settings + coupon + hide_experiment (active)
        comfortplus: tariff_settings + coupon + hide_experiment (active)
        start: tariff_settings + coupon + visible_by_default (False)
        pool: tariff_settings + coupon + show_experiment (Inactive)
        drivers_pool: tariff_settings (No) + coupon
        standart: tariff_settings (No) + coupon
        poputka: tariff_settings + coupon (No)
        uberx: Uber
    """

    couponcheck_services.expected_zone_classes = {
        'minivan',
        'vip',
        'business2',
        'econom',
        'child_tariff',
        'express',
    }
    couponcheck_services.uid = '007'
    response = taxi_protocol.post(
        '3.0/couponcheck',
        json={
            'id': '007000000000041111111111111111111',
            'city': 'Москва',
            'coupon': 'allyandexoneuber',
            'format_currency': True,
            'payment': {'type': 'cash'},
        },
        bearer='test_token',
    )

    check_test_response(response)


@pytest.mark.parametrize(
    'code, content, expected_code',
    [(400, '', 500), (429, '', 429), (500, {}, 500)],
)
def test_couponcheck_via_coupons_code(
        taxi_protocol,
        mockserver,
        code,
        content,
        expected_code,
        couponcheck_services,
):
    @mockserver.handler('/coupons/v1/couponcheck')
    def mock_coupons_list(request):
        resp = content if isinstance(content, str) else json.dumps(content)
        return mockserver.make_response(resp, code)

    response = taxi_protocol.post(
        '3.0/couponcheck',
        json={
            'id': '00000000000041111111111111111111',
            'city': 'Москва',
            'coupon': 'FOO123456',
            'format_currency': True,
            'payment': {'type': 'cash'},
        },
        bearer='test_token',
    )
    assert response.status_code == expected_code


@PROTOCOL_SWITCH_TO_USER_API
@pytest.mark.parametrize(
    'extra_content,extra_expected',
    [
        ({}, {'value': 100, 'value_as_str': '100 $SIGN$$CURRENCY$'}),
        (
            {
                'valid_classes': ['econom', 'comfort'],
                'limit': 100,
                'percent': 10,
            },
            {'limit': 100, 'percent': 10, 'value': 10, 'value_as_str': '10%'},
        ),
        (
            {
                'error_code': 'ERROR_TOO_LATE',
                'valid_any': False,
                'valid': False,
            },
            {'error_code': 'ERROR_TOO_LATE', 'valid_any': False},
        ),
    ],
)
@pytest.mark.parametrize(
    'user_id',
    ['00000000000041111111111111111111', '008000000000041111111111111111123'],
)
def test_couponcheck_via_coupons(
        tvm2_client,
        taxi_protocol,
        mockserver,
        couponcheck_services,
        extra_content,
        extra_expected,
        user_id,
        user_api_switch_on,
):
    content = {
        'valid': True,
        'format_currency': True,
        'descr': 'description',
        'details': ['some_detail'],
        'value': 100,
        'currency_code': 'rub',
    }

    ticket = 'secret'
    user_agent = 'client_ua'
    tvm2_client.set_ticket(json.dumps({'40': {'ticket': ticket}}))

    @mockserver.json_handler('/coupons/v1/couponcheck')
    def mock_couponcheck(request):
        assert request.headers['X-Ya-Service-Ticket'] == ticket
        assert request.headers['User-Agent'] == user_agent
        content.update(extra_content)
        return content

    @mockserver.json_handler('/user-api/users/get')
    def mock_user_get(request):
        assert request.json == {
            'fields': [
                '_id',
                'phone_id',
                'device_id',
                'yandex_uid',
                'yandex_uid_type',
                'yandex_uuid',
                'authorized',
                'token_only',
                'has_ya_plus',
                'has_cashback_plus',
                'apns_token',
                'gcm_token',
                'application',
                'sourceid',
            ],
            'id': user_id,
            'lookup_uber': False,
            'primary_replica': False,
        }
        return {
            'id': user_id,
            'authorized': True,
            'device_id': 'dummy-device-id',
            'phone_id': '5714f45e9895600000000000',
            'token_only': True,
            'yandex_uid': (
                '' if user_id == '008000000000041111111111111111123' else '123'
            ),
        }

    response = taxi_protocol.post(
        '3.0/couponcheck',
        json={
            'id': user_id,
            'city': 'Москва',
            'coupon': 'FOO123456',
            'format_currency': True,
            'payment': {'type': 'cash'},
        },
        bearer='test_token',
        headers={'User-Agent': user_agent},
    )
    if user_id == '008000000000041111111111111111123':
        assert response.status_code == 401
    else:
        expected = {
            'currency_rules': {
                'code': 'rub',
                'sign': '₽',
                'template': '$VALUE$ $SIGN$$CURRENCY$',
                'text': 'rub',
            },
            'descr': 'description',
            'details': ['some_detail'],
            'valid': content['valid'],
        }
        expected.update(extra_expected)

        response_json = response.json()
        assert response_json == expected

    if user_api_switch_on:
        assert mock_user_get.times_called == 1
    else:
        assert mock_user_get.times_called == 0
