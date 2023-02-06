import pytest

from tests_coupons import util


REFFERAL_REQUEST = {
    'application': {
        'name': 'iphone',
        'version': [0, 0, 0],
        'platform_version': [0, 0, 0],
    },
    'zone_name': 'moscow',
    'phone_id': '5714f45e98956f06baaae3d7',
    'yandex_uid': '222222222',
    'payment_options': ['card', 'coupon'],
    'country': 'rus',
    'currency': 'RUB',
    'format_currency': True,
    'locale': 'en',
}


def simple_call(uri):
    async def call_uri(taxi_coupons, data):
        return await taxi_coupons.post(uri, json=data)

    return call_uri


REQUEST_DATA = [
    pytest.param(
        util.make_list_request,
        util.mock_request_list(['4001', '4002', '4003'], 'iphone'),
        id='list_request',
    ),
    pytest.param(
        simple_call('v1/couponcheck'),
        util.mock_request_couponcheck('firstpromocode', {'type': 'cash'}),
        id='check_request',
    ),
    pytest.param(
        util.make_activate_request,
        util.mock_request_activate(
            ['4001'], '4001', 'firstpromocode', '5bbb5faf15870bd76635d5e2',
        ),
        id='activate_request',
    ),
    pytest.param(
        simple_call('v1/couponreserve'),
        util.mock_request_reserve(code='firstpromocode'),
        id='reserve_request',
    ),
    pytest.param(
        simple_call('v1/coupons/referral'),
        REFFERAL_REQUEST,
        id='referral_request',
    ),
]


@pytest.mark.now('2017-03-13T11:30:00+0300')
@pytest.mark.translations(
    client_messages={
        'couponcheck.details_invalid.first_ride_by_tariff': {
            'ru': 'Вы уже совершали первую поездку по данному тарифу',
        },
        'couponcheck.details_invalid.first_ride_by_payment_methods': {
            'ru': 'Вы уже совершали первую поездку по данному методу оплаты',
        },
        'couponcheck.details_invalid.first_ride_by_tariff_'
        'and_payment_method': {'ru': 'Лимит поездок исчерпан'},
    },
)
@pytest.mark.parametrize(
    'class_name,payment_method,is_valid,error_code',
    [
        pytest.param(
            'vip',
            'card',
            True,
            None,
            marks=[pytest.mark.filldb(promocode_series='both')],
        ),
        pytest.param(
            'econom',
            'cash',
            False,
            'ERROR_FIRST_RIDE_BY_CLASSES_AND_PAYMENT_METHODS',
            marks=[pytest.mark.filldb(promocode_series='both')],
        ),
        pytest.param(
            'econom',
            'card',
            False,
            'ERROR_FIRST_RIDE_BY_CLASSES',
            marks=[pytest.mark.filldb(promocode_series='by_classes')],
        ),
        pytest.param(
            'vip',
            'cash',
            False,
            'ERROR_FIRST_RIDE_BY_PAYMENT_METHODS',
            marks=[pytest.mark.filldb(promocode_series='by_payment_methods')],
        ),
    ],
)
@pytest.mark.filldb(promocodes='usages_check')
@pytest.mark.config(
    COUPON_FRAUD_REQUIRE_CREDITCARD_BY_ZONES={'__default__': False},
)
async def test_first_usage(
        taxi_coupons,
        local_services,
        user_statistics_services,
        class_name,
        payment_method,
        is_valid,
        error_code,
):
    user_statistics_services.user_statistics = {
        'data': [
            {
                'identity': {'type': 'phone_id', 'value': 'some_phone_id'},
                'counters': [
                    {
                        'properties': [
                            {'name': 'tariff_class', 'value': class_name},
                            {'name': 'payment_type', 'value': payment_method},
                        ],
                        'value': 3,
                        'counted_from': 'big bang',
                        'counted_to': 'today',
                    },
                ],
            },
        ],
    }

    request = util.mock_request_couponcheck('foo123456', {'type': 'cash'})
    response = await taxi_coupons.post('v1/couponcheck', json=request)
    assert response.status_code == 200
    content = response.json()
    assert content['valid'] == is_valid
    if error_code is not None:
        assert content['error_code'] == error_code
