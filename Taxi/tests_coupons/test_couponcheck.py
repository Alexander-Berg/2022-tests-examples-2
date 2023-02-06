# pylint: disable=too-many-lines
import pytest

from tests_coupons import util

COUPONCHECK_HANDLER = 'v1/couponcheck'
COUPONCHECK_BULK_HANDLER = 'internal/couponcheck/bulk'

CHECK_HANDLERS_PARAMETRIZE = pytest.mark.parametrize(
    'handler', [COUPONCHECK_HANDLER, COUPONCHECK_BULK_HANDLER],
)


def make_request(handler, coupon, **kwargs):
    if handler == COUPONCHECK_HANDLER:
        return util.mock_request_couponcheck(coupon, **kwargs)
    if handler == COUPONCHECK_BULK_HANDLER:
        return util.mock_request_couponcheck_bulk([coupon], **kwargs)
    raise 'unsupported handler'


def get_coupon(handler, response):
    data = response.json()
    if handler == COUPONCHECK_HANDLER:
        return data
    if handler == COUPONCHECK_BULK_HANDLER:
        assert len(data['coupons']) == 1
        return data['coupons'][0]
    raise 'unsupported handler'


@CHECK_HANDLERS_PARAMETRIZE
@pytest.mark.now('2017-03-13T11:30:00+0300')
async def test_invalid_phone_id(taxi_coupons, handler):
    request = make_request(
        handler, 'coupon123', payment_info={'type': 'cash'}, phone_id='',
    )
    response = await taxi_coupons.post(handler, request)
    assert response.status_code == 400


@CHECK_HANDLERS_PARAMETRIZE
@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)
@pytest.mark.filldb(promocode_series='eats_flow')
async def test_eats_flow_with_personal_phone_id(
        taxi_coupons, local_services_card, handler,
):
    request = make_request(
        handler,
        'eatspromo',
        payment_info={'type': 'cash'},
        service='eats',
        phone_id=None,
    )
    response = await taxi_coupons.post(
        handler,
        request,
        headers={'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
    )
    assert response.status_code == 200
    assert get_coupon(handler, response)['valid'] is True


@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.config(COUPONS_SEPARATE_FLOWS=True)
@pytest.mark.filldb(promocode_series='eats_flow')
async def test_grocery_flow_with_personal_phone_id(
        taxi_coupons, local_services_card,
):
    request = util.mock_request_couponcheck(
        'grocerynew', {'type': 'cash'}, service='grocery', phone_id=None,
    )
    response = await taxi_coupons.post(
        'v1/couponcheck',
        request,
        headers={'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['valid'] is True


@CHECK_HANDLERS_PARAMETRIZE
@pytest.mark.parametrize(
    'phone_id, headers, service',
    [
        pytest.param('5bbb5faf15870bd76635d5e2', {}, None),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            'eats',
            marks=[
                pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
                pytest.mark.filldb(promocode_series='eats_flow'),
            ],
            id='eats',
        ),
    ],
)
@pytest.mark.parametrize(
    'coupon_code, expected_description',
    [
        ('ufn99232688', ['Promo code expired on 03/01/2017']),
        # We do not check luhn anymore
        ('ufn99232687', ['Invalid code']),
        (
            'uff99232688',
            ['Promocode has not been activated. Please contact support'],
        ),
        ('uff99232687', ['Invalid code']),
        ('tigran091', ['Promo code expired on 03/01/2017']),
        (
            'tigran092',
            ['Promocode has not been activated. Please contact support'],
        ),
        ('tigran093', ['Invalid code']),
        ('expiredcode', ['Promo code expired on 03/11/2017']),
        ('expiredseries', ['Promo code expired on 03/01/2017']),
    ],
)
@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.config(
    COUPON_FRAUD_REQUIRE_CREDITCARD_BY_ZONES={'__default__': False},
)
async def test_late(
        coupon_code,
        mockserver,
        expected_description,
        taxi_coupons,
        local_services_card,
        phone_id,
        headers,
        service,
        handler,
):
    request = make_request(
        handler,
        coupon_code,
        payment_info={'type': 'cash'},
        locale='en',
        phone_id=phone_id,
        service=service,
    )
    response = await taxi_coupons.post(handler, json=request, headers=headers)

    assert response.status_code == 200
    assert get_coupon(handler, response)['details'] == expected_description


@CHECK_HANDLERS_PARAMETRIZE
@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.config(
    COUPON_FRAUD_REQUIRE_CREDITCARD_BY_ZONES={'__default__': False},
)
@pytest.mark.parametrize(
    'phone_id, headers, service',
    [
        pytest.param('5bbb5faf15870bd76635d5e2', {}, None),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            'eats',
            marks=(
                pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
                pytest.mark.filldb(promocode_series='eats_flow'),
            ),
            id='eats',
        ),
    ],
)
@pytest.mark.parametrize(
    'applications,app',
    [
        (['iphone'], 'iphone'),
        ([], 'iphone'),
        (['yango_iphone'], 'yango_iphone'),
        ([], 'yango_iphone'),
    ],
)
async def test_app(
        mongodb,
        taxi_coupons,
        local_services_card,
        applications,
        app,
        phone_id,
        headers,
        service,
        handler,
):
    """
    promocode_series APP contains 'applications' field
    """
    mongodb.promocode_series.update(
        {'_id': 'app'}, {'$set': {'applications': applications}},
    )

    request = make_request(
        handler,
        'APP123455',
        payment_info={'type': 'cash'},
        locale='en',
        phone_id=phone_id,
        service=service,
    )
    request['application']['name'] = app
    response = await taxi_coupons.post(handler, request, headers=headers)
    assert response.status_code == 200
    coupon = get_coupon(handler, response)
    assert coupon == {
        'currency_code': 'RUB',
        'descr': '100 $SIGN$$CURRENCY$ discount for the next ride',
        'details': ['Expires: 05/01/2017'],
        'format_currency': True,
        'series': 'app',
        'series_purpose': 'marketing',
        'valid': True,
        'value': 100.0,
        'expire_at': '2017-05-01T00:00:00+00:00',
    }


@CHECK_HANDLERS_PARAMETRIZE
@pytest.mark.parametrize(
    'code, expected_valid, descr',
    [
        (
            'serialess000001',
            True,
            '500 $SIGN$$CURRENCY$ discount on the next 2 rides '
            'in tariffs Comfort, Econom',
        ),
        (
            'rjatbrfrfj',
            True,
            '500 $SIGN$$CURRENCY$ discount on the next 2 rides '
            'in tariff Comfort',
        ),
    ],
)
@pytest.mark.parametrize(
    'phone_id, headers, service',
    [
        pytest.param('5bbb5faf15870bd76635d5e2', {}, None),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            'eats',
            marks=(
                pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
                pytest.mark.filldb(promocode_series='eats_flow'),
            ),
            id='eats',
        ),
    ],
)
async def test_class(
        taxi_coupons,
        code,
        expected_valid,
        descr,
        local_services_card,
        phone_id,
        headers,
        service,
        handler,
):
    """
    Checks correct handling of 'classes' field in db_promocode_series
    ('serialess000001' & 'serialess000002' contains field 'classes',
    see db.promocode_series and
    'rjatbrfrfj' is promocode from series 'serialess000002' see db.promocodes).
    Also checks translation: serialess000001 contains 2 classes,
    serialess000002 - 1 class

    NOTE: historically 'business' class means Comfort service level,
    and translation will try to find 'name.comfort' key in Tanker
    (at the current time),
    And 'vip' class means Business
    """
    request = make_request(
        handler,
        code,
        payment_info={'type': 'cash'},
        locale='en',
        phone_id=phone_id,
        service=service,
    )
    response = await taxi_coupons.post(handler, json=request, headers=headers)

    assert response.status_code == 200
    coupon = get_coupon(handler, response)
    assert coupon['valid'] == expected_valid
    assert coupon['descr'] == descr


@CHECK_HANDLERS_PARAMETRIZE
async def test_unsupported_classes_in_zone(
        taxi_coupons, local_services_card, handler,
):
    """
    Checks at least 1 promocode's class is allowable in given zone
    'serialess000001' (see db_promocode_series) contains ['econom', 'business']
    db_tariff_settings_unsupported_classes_in_zone contains only 'vip' class
    """
    request = make_request(
        handler, 'serialess000001', payment_info={'type': 'cash'}, locale='en',
    )
    request['zone_classes'] = []
    response = await taxi_coupons.post(handler, json=request)

    assert response.status_code == 200
    data = get_coupon(handler, response)
    assert data['valid'] is False
    assert data['descr'] == '500 $SIGN$$CURRENCY$ discount on the next 2 rides'
    assert data['details'] == (
        ['Discount on this service class is not valid in your region']
    )
    assert data['error_code'] == 'ERROR_UNSUPPORTED_ZONE_CLASSES'


@CHECK_HANDLERS_PARAMETRIZE
@pytest.mark.config(
    COUPON_FRAUD_REQUIRE_CREDITCARD_BY_ZONES={'__default__': True},
)
@pytest.mark.parametrize(
    'service',
    [
        pytest.param(None),
        pytest.param(
            'eats',
            marks=(
                pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
                pytest.mark.filldb(promocode_series='eats_flow'),
            ),
            id='eats',
        ),
    ],
)
@pytest.mark.parametrize(
    'code, payment, is_owner, expected_valid, expected_message',
    [
        (
            'withphoneid',
            {'type': 'cash'},
            True,
            False,
            [
                'Add a bank card and use it to pay for '
                'rides to take advantage of '
                'promo codes and discounts',
            ],
        ),
        (
            'withphoneid',
            {'type': 'cash'},
            False,
            False,
            ['Promocode has not been activated. Please contact support'],
        ),
        (
            'support',
            {'type': 'card', 'method_id': 'card_id'},
            True,
            True,
            ['Rides left: 2', 'Expires: 03/01/2099'],
        ),
        (
            'support',
            {'type': 'cash'},
            False,
            False,
            ['Promocode has not been activated. Please contact support'],
        ),
    ],
)
async def test_phone_binding(
        taxi_coupons,
        local_services,
        code,
        payment,
        is_owner,
        expected_valid,
        expected_message,
        service,
        handler,
):
    # Test that even if user have a bad card, and coupon is binded,
    # we will allow to use this coupon only if it's for support
    # ('for_support': True in db.promocode_series).
    # Here user 008 is a coupon owner but he does not have a card.
    # User 007 is not an owner, but her/his cards are valid.

    request = make_request(
        handler,
        code,
        payment_info=payment,
        locale='en',
        service=service,
        phone_id=None,
    )

    headers = {}
    if service:
        if is_owner:
            headers = {'X-Eats-User': 'personal_phone_id=123456789'}
        else:
            headers = {
                'X-Eats-User': 'personal_phone_id=100000000000000000000001',
            }
            local_services.add_card()
    else:
        if is_owner:
            request['phone_id'] = '5714f45e9895600000000001'
        else:
            request['phone_id'] = '5714f45e9895600000000000'
            local_services.add_card()

    response = await taxi_coupons.post(handler, json=request, headers=headers)

    assert response.status_code == 200
    coupon = get_coupon(handler, response)
    assert coupon['valid'] is expected_valid
    if expected_message:
        assert coupon['details'] == expected_message


@CHECK_HANDLERS_PARAMETRIZE
@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.config(
    COUPON_FRAUD_REQUIRE_CREDITCARD_BY_ZONES={'__default__': False},
)
async def test_first_usage_per_classes_ok(
        taxi_coupons, mockserver, local_services_card, handler,
):
    request = util.mock_request_couponcheck(
        'FOO123456', {'type': 'cash'}, locale='en',
    )

    response = await taxi_coupons.post('v1/couponcheck', json=request)
    assert response.status_code == 200
    content = response.json()
    assert content == {
        'currency_code': 'RUB',
        'descr': (
            '100 $SIGN$$CURRENCY$ discount for the'
            ' next ride in tariffs Comfort, Econom'
        ),
        'details': ['Expires: 05/01/2017'],
        'format_currency': True,
        'series': 'foo1',
        'series_purpose': 'marketing',
        'valid': True,
        'valid_classes': ['econom', 'business'],
        'value': 100.0,
        'expire_at': '2017-05-01T00:00:00+00:00',
    }


@CHECK_HANDLERS_PARAMETRIZE
@pytest.mark.translations(
    client_messages={
        'couponcheck.details_invalid.first_ride_by_tariff': {
            'ru': 'Вы уже совершали первую поездку по данному тарифу',
        },
    },
)
@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.config(
    COUPON_FRAUD_REQUIRE_CREDITCARD_BY_ZONES={'__default__': False},
)
@pytest.mark.parametrize(
    'filter_config',
    [{}, {'eats': []}, {'eats': ['CheckFirstUsage']}, {'test': []}],
)
@pytest.mark.parametrize('service', ['taxi', 'eats'])
async def test_first_usage_per_classes_fail_on_taxi(
        taxi_coupons,
        taxi_config,
        mockserver,
        local_services_card,
        user_statistics_services,
        service,
        filter_config,
        handler,
):
    taxi_config.set_values(dict(COUPONS_IGNORED_CHECKS=filter_config))
    await taxi_coupons.invalidate_caches()

    user_statistics_services.set_detailed_rides(1, tariff_class='business')
    request = make_request(
        handler, 'FOO123456', payment_info={'type': 'cash'}, locale='en',
    )
    request['service'] = service

    response = await taxi_coupons.post(handler, json=request)
    assert response.status_code == 200
    coupon = get_coupon(handler, response)
    if service == 'eats' and filter_config.get(service):
        assert coupon == {
            'currency_code': 'RUB',
            'descr': (
                '100 $SIGN$$CURRENCY$ discount for the'
                ' next ride in tariffs Comfort, Econom'
            ),
            'details': ['Expires: 05/01/2017'],
            'format_currency': True,
            'series': 'foo1',
            'series_purpose': 'marketing',
            'valid': True,
            'valid_classes': ['econom', 'business'],
            'value': 100.0,
            'expire_at': '2017-05-01T00:00:00+00:00',
        }
    else:
        assert coupon['error_code'] == 'ERROR_FIRST_RIDE_BY_CLASSES'


USERSTATS_RESPONSE = {'phone_id': [{'id': '123', 'counters': []}]}
APPLICATION_MAP_BRAND = {
    '__default__': 'unknown',
    'android': 'yataxi',
    'iphone': 'yataxi',
    'yango_android': 'yango',
    'uber_iphone': 'yauber',
}


@CHECK_HANDLERS_PARAMETRIZE
@pytest.mark.translations(
    override_uber={
        'couponcheck.details_invalid.unsupported_application_uber_iphone': {
            'en': 'Uber unsupported',
        },
    },
)
@pytest.mark.now('2019-01-01T00:00:00+0300')
async def test_coupon_strings_override(
        taxi_coupons, local_services_card, handler,
):
    request = make_request(
        handler, 'APP123455', payment_info={'type': 'cash'}, locale='en',
    )
    request['application']['name'] = 'uber_iphone'
    response = await taxi_coupons.post(handler, request)
    assert response.status_code == 200
    assert get_coupon(handler, response)['details'] == ['Uber unsupported']


@CHECK_HANDLERS_PARAMETRIZE
@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.config(
    COUPON_FRAUD_REQUIRE_CREDITCARD_BY_ZONES={'__default__': True},
)
@pytest.mark.parametrize(
    'phone_id, headers, service, coupon',
    [
        pytest.param('5bbb5faf15870bd76635d5e2', {}, None, 'FOO123455'),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            'eats',
            'foo058351',
            marks=pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
            id='eats',
        ),
    ],
)
async def test_metrics_exist(
        taxi_coupons,
        taxi_coupons_monitor,
        local_services,
        phone_id,
        headers,
        service,
        coupon,
        handler,
):
    request = make_request(
        handler,
        coupon,
        payment_info={'type': 'cash'},
        phone_id=phone_id,
        service=service,
    )
    response = await taxi_coupons.post(handler, json=request, headers=headers)
    assert response.status_code == 200

    metrics_name = 'coupon-check-statistics'
    metrics = await taxi_coupons_monitor.get_metrics(metrics_name)

    assert metrics_name in metrics.keys()


@CHECK_HANDLERS_PARAMETRIZE
@pytest.mark.translations(
    client_messages={
        'couponcheck.details_invalid.unsupported_application_yango_android': {
            'en': 'test application is unsupported',
        },
    },
)
@pytest.mark.parametrize(
    'phone_id, headers, service',
    [
        pytest.param('5bbb5faf15870bd76635d5e2', {}, None),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            'eats',
            marks=[
                pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
                pytest.mark.filldb(promocode_series='eats_flow'),
            ],
            id='eats',
        ),
    ],
)
async def test_unsupported_application(
        taxi_coupons, local_services, phone_id, headers, service, handler,
):
    request = make_request(
        handler,
        'WITHAPPS1',
        payment_info={'type': 'cash'},
        locale='en',
        app_name='yango_android',
        phone_id=phone_id,
        service=service,
    )
    response = await taxi_coupons.post(handler, request, headers=headers)
    assert response.status_code == 200
    content = get_coupon(handler, response)
    assert content['details'] == ['test application is unsupported']


@pytest.mark.config(
    COUPONS_USER_AGENT_RESTRICTIONS={
        'hon30': '^.+\\(HUAWEI; (BMH|EBG)-AN10\\)$',
    },
)
@pytest.mark.parametrize(
    'phone_id, headers, service',
    [
        pytest.param('5bbb5faf15870bd76635d5e2', {}, None),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            'eats',
            marks=(
                pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
                pytest.mark.filldb(promocode_series='eats_flow'),
            ),
            id='eats',
        ),
    ],
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
        pytest.param(None, True, id='skip check without UA'),
    ],
)
@pytest.mark.now('2019-03-06T11:30:00+0300')
@pytest.mark.skip(reason='flapping test, will be fixed in TAXIBACKEND-41551')
async def test_reserve_user_agent(
        taxi_coupons,
        mongodb,
        local_services_card,
        code,
        need_check_ua,
        user_agent,
        ua_match,
        phone_id,
        headers,
        service,
):
    request = util.mock_request_couponcheck(
        code, {'type': 'cash'}, phone_id=phone_id, service=service,
    )
    headers['User-Agent'] = user_agent
    response = await taxi_coupons.post(
        'v1/couponcheck', json=request, headers=headers,
    )

    assert response.status_code == 200
    content = response.json()

    valid = not need_check_ua or ua_match
    assert content['valid'] is valid
    if not valid:
        assert content['valid_any'] is False
        assert content['error_code'] == 'ERROR_MANUAL_ACTIVATION_IS_REQUIRED'


@CHECK_HANDLERS_PARAMETRIZE
@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.config(
    COUPON_FRAUD_REQUIRE_CREDITCARD_BY_ZONES={'__default__': False},
)
@pytest.mark.parametrize(
    'phone_id, headers, service',
    [
        pytest.param('5bbb5faf15870bd76635d5e2', {}, None),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            'eats',
            marks=(
                pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
                pytest.mark.filldb(promocode_series='eats_flow'),
            ),
            id='eats',
        ),
    ],
)
@pytest.mark.parametrize(
    'code,expected_value,expected_series, expected_purpose',
    [
        ('APP123455', 100, 'app', 'marketing'),
        ('APP123466', 42, 'app1', 'support'),
        ('APP123467', 100, 'app', 'referral_reward'),
    ],
)
async def test_value(
        mongodb,
        taxi_coupons,
        local_services_card,
        code,
        expected_value,
        expected_series,
        expected_purpose,
        phone_id,
        headers,
        service,
        handler,
):
    request = make_request(
        handler,
        code,
        payment_info={'type': 'cash'},
        locale='en',
        phone_id=phone_id,
        service=service,
    )
    response = await taxi_coupons.post(handler, request, headers=headers)
    assert response.status_code == 200
    content = get_coupon(handler, response)
    assert content == {
        'currency_code': 'RUB',
        'descr': (
            f'{expected_value} $SIGN$$CURRENCY$ discount for the ' f'next ride'
        ),
        'details': ['Expires: 05/01/2017'],
        'format_currency': True,
        'series': expected_series,
        'series_purpose': expected_purpose,
        'valid': True,
        'value': expected_value,
        'expire_at': '2017-05-01T00:00:00+00:00',
    }


@CHECK_HANDLERS_PARAMETRIZE
@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.parametrize(
    'phone_id, headers, service',
    [
        pytest.param(
            '5bbb5faf15870bd76635d5e2',
            {},
            None,
            marks=pytest.mark.filldb(promocode_usages2='limit_exceeded'),
        ),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            'eats',
            marks=(
                pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
                pytest.mark.filldb(mdb_promocode_usages2='limit_exceeded'),
                pytest.mark.filldb(promocode_series='eats_flow'),
            ),
            id='eats',
        ),
    ],
)
@pytest.mark.parametrize(
    'code, limit_exceeded',
    [
        pytest.param('codepromo2', False, id='usage_per_promocode_true'),
        pytest.param('seriespromo2', True, id='usage_per_promocode_false'),
        pytest.param(
            'seriespromojustone2',
            True,
            id='usage_per_promocode_false_check_another_promo',
        ),
    ],
)
async def test_usage_per_promocode(
        mongodb,
        taxi_coupons,
        local_services_card,
        code,
        limit_exceeded,
        phone_id,
        headers,
        service,
        handler,
):
    request = make_request(
        handler,
        code,
        payment_info={'type': 'card', 'method_id': 'card_id'},
        phone_id=phone_id,
        service=service,
    )
    response = await taxi_coupons.post(handler, request, headers=headers)
    assert response.status_code == 200

    response = get_coupon(handler, response)
    assert (
        response['error_code'] == 'ERROR_USER_LIMIT_EXCEEDED'
        if limit_exceeded
        else 'error_code' not in response
    )


@CHECK_HANDLERS_PARAMETRIZE
@pytest.mark.filldb(promocodes='percent')
@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.parametrize(
    'phone_id, headers, service',
    [
        pytest.param(
            '5bbb5faf15870bd76635d5e2',
            {},
            None,
            marks=(
                pytest.mark.filldb(promocode_usages2='percent'),
                pytest.mark.filldb(promocode_series='percent'),
            ),
        ),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            'eats',
            marks=(
                pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
                pytest.mark.filldb(mdb_promocode_usages2='percent'),
                pytest.mark.filldb(promocode_series='percent_eats_flow'),
            ),
            id='eats',
        ),
    ],
)
@pytest.mark.parametrize(
    'coupon, percent_limit_per_trip',
    [
        pytest.param(
            'percentpertripcode', True, id='percent_limit_per_trip_true',
        ),
        pytest.param(
            'percentnotpertrip', False, id='percent_limit_per_trip_false',
        ),
        pytest.param(
            'percentemptypertrip', False, id='percent_limit_per_trip_none',
        ),
    ],
)
async def test_percent_limit_per_trip(
        mongodb,
        taxi_coupons,
        local_services_card,
        coupon,
        percent_limit_per_trip,
        phone_id,
        headers,
        service,
        handler,
):
    request = make_request(
        handler,
        coupon,
        payment_info={'type': 'card', 'method_id': 'card_id'},
        phone_id=phone_id,
        service=service,
    )

    response = await taxi_coupons.post(handler, request, headers=headers)
    assert response.status_code == 200

    response = get_coupon(handler, response)
    # if coupon is percent_limit_per_trip it means the value is const = 400
    # else the value is decreasing so it should be 300(have cost_usage = 100)
    assert (
        response['limit'] == 400
        if percent_limit_per_trip
        else response['limit'] == 300
    )


@CHECK_HANDLERS_PARAMETRIZE
@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.filldb(promocodes='percent')
@pytest.mark.parametrize(
    'phone_id, headers, service',
    [
        pytest.param(
            '5bbb5faf15870bd76635d5e2',
            {},
            None,
            marks=(
                pytest.mark.filldb(promocode_series='percent'),
                pytest.mark.filldb(promocode_usages2='percent'),
            ),
        ),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            'eats',
            marks=(
                pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
                pytest.mark.filldb(promocode_series='percent_eats_flow'),
                pytest.mark.filldb(mdb_promocode_usages2='percent'),
            ),
            id='eats',
        ),
    ],
)
@pytest.mark.parametrize(
    'coupon, percent_limit_per_trip',
    [
        pytest.param(
            'percentpertripcode', True, id='percent_limit_per_trip_true',
        ),
        pytest.param(
            'percentnotpertrip', False, id='percent_limit_per_trip_false',
        ),
        pytest.param(
            'percentemptypertrip', False, id='percent_limit_per_trip_none',
        ),
    ],
)
async def test_reserve_blocks_code(
        mongodb,
        taxi_coupons,
        local_services_card,
        coupon,
        percent_limit_per_trip,
        phone_id,
        headers,
        service,
        handler,
):
    request = util.mock_request_reserve(
        code=coupon, phone_id=phone_id, service=service,
    )
    response = await taxi_coupons.post(
        'v1/couponreserve', json=request, headers=headers,
    )

    assert response.status_code == 200
    assert response.json()['valid']

    request = make_request(
        handler,
        coupon,
        payment_info={'type': 'card', 'method_id': 'card_id'},
        phone_id=phone_id,
        service=service,
    )
    response = await taxi_coupons.post(handler, request, headers=headers)
    assert response.status_code == 200

    response = get_coupon(handler, response)

    assert (
        response['valid'] if percent_limit_per_trip else not response['valid']
    )
