import copy
import enum

import pytest

from tests_coupons import util


@pytest.mark.now('2017-03-13T11:30:00+0300')
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
    'code,card_only',
    [
        ('FOO123455', False),
        ('lntnsk50380260', True),
        ('paymethodscardonly1', True),
    ],
)
@pytest.mark.config(
    COUPON_FRAUD_REQUIRE_CREDITCARD_BY_ZONES={'__default__': False},
)
async def test_couponcheck_creditcard_only(
        taxi_coupons,
        local_services_card,
        code,
        card_only,
        phone_id,
        headers,
        service,
):
    request = util.mock_request_couponcheck(
        code, {'type': 'applepay'}, phone_id=phone_id, service=service,
    )

    response = await taxi_coupons.post(
        'v1/couponcheck', json=request, headers=headers,
    )
    assert response.status_code == 200
    response = response.json()
    assert response['valid'] is not card_only
    if card_only:
        assert response['valid_any'] is True
        assert response['error_code'] == 'ERROR_CREDITCARD_ONLY'
        assert (
            'Внимание! Промокод действует только при'
            ' оплате поездки банковской картой'
        ) in response['details']


@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.config(
    COUPON_FRAUD_REQUIRE_CREDITCARD_BY_ZONES={'__default__': True},
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
async def test_couponcheck_creditcard_nocard(
        taxi_coupons, local_services, phone_id, headers, service,
):
    request = util.mock_request_couponcheck(
        'FOO123455', {'type': 'cash'}, phone_id=phone_id, service=service,
    )

    # local_services.cards = [local_services.sample_card]
    response = await taxi_coupons.post(
        'v1/couponcheck', json=request, headers=headers,
    )

    assert response.status_code == 200
    content = response.json()
    assert content == {
        'currency_code': '',
        'descr': '',
        'details': [
            (
                'Add a bank card and use it to pay for rides to take '
                'advantage of promo codes and discounts'
            ),
        ],
        'error_code': 'ERROR_CREDITCARD_REQUIRED',
        'format_currency': False,
        'series_purpose': 'support',
        'valid': False,
        'valid_any': False,
        'value': 0.0,
        'expire_at': '1970-01-01T00:00:00+00:00',
    }


@pytest.mark.config(
    COUPON_FRAUD_REQUIRE_CREDITCARD_BY_ZONES={'__default__': True},
    COUPON_FRAUD_SERIES_WITHOUT_CREDITCARD_CHECK=['serialess000002'],
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
    'code, response_valid, response_error_code, response_details',
    [
        ('withphoneid', True, None, ['Rides left: 2', 'Expires: 03/01/2099']),
        (
            'serialess000001',
            False,
            'ERROR_CREDITCARD_REQUIRED',
            [
                'Add a bank card and use it to pay for '
                'rides to take advantage of '
                'promo codes and discounts',
            ],
        ),
    ],
)
async def test_series_without_creditcard_check_config(
        taxi_coupons,
        local_services,
        code,
        response_valid,
        response_error_code,
        response_details,
        phone_id,
        headers,
        service,
):
    payment = {'type': 'cash'}
    request = util.mock_request_couponcheck(
        code, payment, locale='en', phone_id=phone_id, service=service,
    )
    request['phone_id'] = '5714f45e9895600000000001'

    response = await taxi_coupons.post(
        'v1/couponcheck', json=request, headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data['valid'] is response_valid
    assert data.get('error_code') == response_error_code
    assert data.get('details') == response_details


APPLICATION_MAP_BRAND = {
    '__default__': 'unknown',
    'android': 'yataxi',
    'iphone': 'yataxi',
    'yango_android': 'yango',
    'uber_iphone': 'yauber',
}


BILLING_SERVICE_NAME_MAP_BY_BRAND = {
    '__default__': 'unknown',
    'yataxi': 'card',
    'yango': 'card',
    'yauber': 'uber',
}


@pytest.mark.config(
    BILLING_SERVICE_NAME_MAP_BY_BRAND=BILLING_SERVICE_NAME_MAP_BY_BRAND,
    APPLICATION_MAP_BRAND=APPLICATION_MAP_BRAND,
    COUPONS_CARDSTORAGE_REQUESTS_PARAMS={
        '__default__': {
            'timeout_ms': 10000,
            'retries': 3,
            'pass_renew_after': True,
        },
        'couponcheck': {
            'timeout_ms': 15000,
            'retries': 2,
            'pass_renew_after': False,
        },
    },
)
@pytest.mark.parametrize(
    'app_name',
    ['iphone', 'yango_android', 'uber_iphone', 'mobileweb_android'],
)
@pytest.mark.translations(
    override_uber={
        'couponcheck.details_invalid.unsupported_application_uber_iphone': {
            'en': 'Uber unsupported',
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
            marks=pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
            id='eats',
        ),
    ],
)
async def test_cardstorage_request(
        taxi_coupons,
        local_services,
        mockserver,
        app_name,
        phone_id,
        headers,
        service,
):
    local_services.check_service_type(
        BILLING_SERVICE_NAME_MAP_BY_BRAND, APPLICATION_MAP_BRAND, app_name,
    )

    response = await taxi_coupons.post(
        'v1/couponcheck',
        util.mock_request_couponcheck(
            'FOO123456',
            {'type': 'cash'},
            locale='en',
            app_name=app_name,
            phone_id=phone_id,
            service=service,
        ),
        headers=headers,
    )
    assert response.status_code == 200

    assert local_services.mock_cardstorage.has_calls

    util.check_cardstorage_requests(
        local_services.cardstorage_requests,
        expected_num_requests=2,
        expected_num_requests_wo_renew_after=2,
        expected_timeout_ms=15000,
    )


class CardstorageResponses(enum.Enum):
    Success = 'Success'
    Timeout = 'Timeout'
    NetworkError = 'NetworkError'
    Moneyless = 'Moneyless'


@pytest.mark.config(
    COUPONS_CLIENTS_CONFIG={'__default__': {'timeout_ms': 200, 'retries': 2}},
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
    'cardstorage_response', [e for e in CardstorageResponses],
)
@pytest.mark.parametrize(
    'cardstorage_fallback_response', [e for e in CardstorageResponses],
)
@pytest.mark.now('2017-03-13T11:30:00+0300')
async def test_cardstorage_fallback(
        cardstorage_response: CardstorageResponses,
        cardstorage_fallback_response: CardstorageResponses,
        taxi_coupons,
        local_services_card,
        mockserver,
        phone_id,
        headers,
        service,
):
    request = util.mock_request_couponcheck(
        'FOO123456', {'type': 'cash'}, phone_id=phone_id, service=service,
    )

    @mockserver.json_handler('/cardstorage/v1/payment_methods')
    def _mock_cardstorage(request):
        if 'renew_after' in request.json:
            response_type = cardstorage_response
        else:
            response_type = cardstorage_fallback_response

        if response_type == CardstorageResponses.Success:
            return local_services_card.cards
        if response_type == CardstorageResponses.Timeout:
            raise mockserver.TimeoutError()
        if response_type == CardstorageResponses.NetworkError:
            raise mockserver.NetworkError()
        assert response_type is CardstorageResponses.Moneyless
        resp = copy.deepcopy(local_services_card.cards)
        resp['available_cards'][0]['possible_moneyless'] = True
        return resp

    response = await taxi_coupons.post(
        'v1/couponcheck', request, headers=headers,
    )

    assert _mock_cardstorage.times_called == 2

    if cardstorage_response in (
            CardstorageResponses.Timeout,
            CardstorageResponses.NetworkError,
    ):
        using_cardstorage_response = cardstorage_fallback_response
    else:
        using_cardstorage_response = cardstorage_response
    if using_cardstorage_response == CardstorageResponses.Success:
        assert response.status_code == 200
        assert response.json()['valid'] is True
    elif using_cardstorage_response == CardstorageResponses.Moneyless:
        assert response.status_code == 200
        assert (
            response.json()['error_code']
            == 'ERROR_MANUAL_ACTIVATION_IS_REQUIRED'
        )
    else:  # both responses are error
        assert response.status_code == 429


@pytest.mark.now('2017-03-13T11:30:00+0300')
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
@pytest.mark.config(
    COUPON_FRAUD_REQUIRE_CREDITCARD_BY_ZONES={'__default__': False},
)
async def test_couponcheck_payment_methods(
        taxi_coupons,
        local_services,
        code,
        payment_method,
        method_id,
        valid_payment_method,
        phone_id,
        headers,
        service,
):
    if payment_method == 'card':
        local_services.add_card_and_ya_card()

    request = util.mock_request_couponcheck(
        code,
        {'type': payment_method, 'method_id': method_id},
        phone_id=phone_id,
        service=service,
    )

    response = await taxi_coupons.post(
        'v1/couponcheck', json=request, headers=headers,
    )
    assert response.status_code == 200
    response = response.json()
    assert response['valid'] == valid_payment_method

    if not valid_payment_method:
        # Check error code
        assert response['valid_any'] is True
        assert response['error_code'] == 'ERROR_INVALID_PAYMENT_METHOD'

        #  Check payment methods in details
        methods = util.PAYMENT_METHODS_MAP[code]
        assert response['details'] == [
            (
                'Внимание! Промокод действует только'
                ' для следующих методов оплаты: {}'
            ).format(methods),
        ]
    else:
        #  Check payment methods in details
        details = ['Действует до: 01.05.2017']
        methods = util.PAYMENT_METHODS_MAP.get(code)
        if methods:
            details.append(f'Методы оплаты: {methods}')
        assert response['details'] == details


@pytest.mark.now('2017-03-13T11:30:00+0300')
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
    'coupon, payment_type, method_id, is_valid_payment_method, '
    'coupon_valid_payment_types',
    [
        pytest.param(
            'paymentmethods1',
            'card',
            'card_id',
            True,
            ['applepay', 'card', 'cash'],
            id='valid_with_payment_types',
        ),
        pytest.param(
            'paymentmethods1',
            'card',
            'ya_card_id',
            True,
            ['applepay', 'card', 'cash'],
            id='valid_with_payment_types',
        ),
        pytest.param(
            'paymentmethods1',
            'googlepay',
            None,
            False,
            None,
            id='invalid_with_payment_types',
        ),
        pytest.param(
            'bizpaymentmethod1',
            'business_account',
            'business-123',
            True,
            ['business_account'],
            id='valid_with_payment_types_no_card',
        ),
        pytest.param(
            'bizpaymentmethod1',
            'cash',
            None,
            False,
            None,
            id='invalid_with_payment_types_no_card',
        ),
        pytest.param(
            'emptypaymentmethods1',
            'coop_account',
            'some-123',
            True,
            None,
            id='valid_no_payment_types',
        ),
        pytest.param(
            'creditcardonly1',
            'card',
            'card_id',
            True,
            ['card'],
            id='valid_creditcardonly',
        ),
        pytest.param(
            'creditcardonly1',
            'card',
            'ya_card_id',
            True,
            ['card'],
            id='valid_creditcardonly',
        ),
        pytest.param(
            'creditcardonly2',
            'card',
            'card_id',
            True,
            ['card'],
            id='valid_creditcardonly_empty_payment_methods',
        ),
        pytest.param(
            'creditcardonly2',
            'card',
            'ya_card_id',
            True,
            ['card'],
            id='valid_creditcardonly_empty_payment_methods',
        ),
        pytest.param(
            'creditcardonly1',
            'cash',
            None,
            False,
            None,
            id='invalid_creditcardonly',
        ),
    ],
)
@pytest.mark.config(
    COUPON_FRAUD_REQUIRE_CREDITCARD_BY_ZONES={'__default__': False},
)
async def test_couponcheck_valid_payment_types(
        taxi_coupons,
        local_services,
        coupon,
        payment_type,
        method_id,
        is_valid_payment_method,
        coupon_valid_payment_types,
        phone_id,
        headers,
        service,
):
    if payment_type == 'card':
        local_services.add_card_and_ya_card()

    request = util.mock_request_couponcheck(
        coupon,
        {'type': payment_type, 'method_id': method_id},
        phone_id=phone_id,
        service=service,
    )
    response = await taxi_coupons.post(
        'v1/couponcheck', json=request, headers=headers,
    )

    assert response.status_code == 200
    response = response.json()

    assert response['valid'] == is_valid_payment_method

    if is_valid_payment_method and coupon_valid_payment_types:
        assert (
            sorted(response['valid_payment_types'])
            == coupon_valid_payment_types
        )
    else:
        assert 'valid_payment_types' not in response


@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.parametrize(
    'phone_id, headers, service',
    [
        pytest.param('5bbb5faf15870bd76635d5e2', {}, None),
        pytest.param(
            None,
            {'X-Eats-User': 'personal_phone_id=100000000000000000000001'},
            'eats',
            marks=pytest.mark.config(COUPONS_SEPARATE_FLOWS=True),
            id='eats',
        ),
    ],
)
@pytest.mark.parametrize(
    'payment_method, require_method_id',
    [
        ('applepay', False),
        ('cash', False),
        ('card', True),
        ('googlepay', False),
        ('coop_account', True),
    ],
)
@pytest.mark.parametrize('method_id', [None, 'business-123'])
@pytest.mark.config(
    COUPON_FRAUD_REQUIRE_CREDITCARD_BY_ZONES={'__default__': False},
)
async def test_couponcheck_required_payment_method_id(
        taxi_coupons,
        local_services,
        payment_method,
        method_id,
        require_method_id,
        phone_id,
        headers,
        service,
):
    if payment_method == 'card':
        local_services.add_card()

    request = util.mock_request_couponcheck(
        'anycode',
        {'type': payment_method, 'method_id': method_id},
        phone_id=phone_id,
        service=service,
    )

    response = await taxi_coupons.post(
        'v1/couponcheck', json=request, headers=headers,
    )
    if require_method_id and not method_id:
        expected_code = 400
    else:
        expected_code = 200
    assert response.status_code == expected_code
