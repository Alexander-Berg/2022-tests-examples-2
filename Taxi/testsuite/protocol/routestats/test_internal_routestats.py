import dataclasses
import enum
import json
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest

from protocol.routestats import utils


_set_default_tariff_info_and_prices = utils.set_default_tariff_info_and_prices


def compare_service_levels_data(ext_service_levels, int_service_levels):
    assert len(int_service_levels)

    ext_service_levels_map = {
        level['class']: level for level in ext_service_levels
    }

    for int_service_level in int_service_levels:
        int_class = int_service_level['class']
        assert int_class in ext_service_levels_map


def test_internal_routestats_no_tvm(
        taxi_protocol, pricing_data_preparer, load_json,
):
    request = load_json('request.json')
    response = taxi_protocol.post('internal/routestats', request)
    assert response.status_code == 401


def test_routestats_returns_no_internal_data(
        local_services, mockserver, taxi_protocol, load_json,
):
    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def _mock_v2_prepare(request):
        return load_json('pdp_response.json')

    request = load_json('request.json')
    response = taxi_protocol.post('3.0/routestats', request)

    assert response.status_code == 200
    assert _mock_v2_prepare.has_calls
    assert 'internal_data' not in response.json()


@pytest.mark.user_experiments('explicit_antisurge')
@pytest.mark.experiments3(filename='experiments.json')
@pytest.mark.config(
    PERSONAL_WALLET_ENABLED=True,
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'routestats', 'dst': 'protocol'}],
    TVM_SERVICES={'routestats': 2020659, 'protocol': 13},
)
@pytest.mark.experiments3(filename='experiments.json')
def test_internal_routestats_basic(
        local_services,
        mockserver,
        taxi_protocol,
        load_json,
        tvm2_client,
        load,
):
    @mockserver.json_handler('/personal_wallet/v1/balances')
    def _mock_balances(request):
        return {
            'balances': [
                {
                    'wallet_id': 'wallet_id/some_number_value',
                    'currency': 'RUB',
                    'is_new': True,
                    'balance': '111',
                    'payment_orders': [],
                },
            ],
            'available_deposit_payment_methods': [],
        }

    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        res = utils.get_surge_calculator_response(request, 1)
        for class_info in res['classes']:
            if class_info['name'] == 'econom':
                class_info['explicit_antisurge'] = {'value': 0.3}
                class_info['value_smooth_b'] = 1.0
                break
        return res

    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def _mock_v2_prepare(request):
        return load_json('pdp_response.json')

    # to generate use `tvmknife unittest service --src 2020659 --dst 13`
    ticket = load('tvm2_ticket_2020659_13')
    request = load_json('request.json')
    response = taxi_protocol.post(
        'internal/routestats',
        request,
        headers={'X-Ya-Service-Ticket': ticket},
    )

    assert response.status_code == 200
    assert _mock_v2_prepare.has_calls
    data = response.json()
    int_data = data.get('internal_data')
    assert int_data is not None

    assert int_data['route_info'] == {'distance': '12346', 'time': '988'}

    assert 'service_levels_data' in int_data
    compare_service_levels_data(
        data['service_levels'], int_data['service_levels_data'],
    )

    assert 'tariff_categories' in int_data
    for tariff_category in int_data['tariff_categories']:
        required_fields = (
            'currency',
            'id',
            'name',
            'requirement_prices',
            'tanker_key',
        )
        for key in required_fields:
            assert key in tariff_category
        for req_price in tariff_category['requirement_prices']:
            required_fields = ('price', 'type')
            for key in required_fields:
                assert key in req_price


def fixed_pdp_response(response):
    econom_user = response['categories']['econom']['user']
    business_user = response['categories']['business']['user']
    econom_user['data']['coupon'] = {
        'valid': True,
        'format_currency': True,
        'descr': 'description',
        'details': ['some_detail'],
        'value': 300,
        'percent': 50,
        'limit': 300,
        'valid_classes': ['econom'],
        'currency_code': 'rub',
    }
    econom_user['meta']['coupon_applying_limit'] = 300.0
    econom_user['price']['total'] = 600
    econom_user['price']['strikeout'] = (
        econom_user['price']['total'] + econom_user['data']['coupon']['limit']
    )

    business_user['data']['discount'] = {
        'description': 'some discount description',
        'reason': 'for_all',
        'method': 'subvention-fix',
        'limited_rides': False,
    }
    business_user['meta']['discount_value'] = 0.2
    business_user['meta']['marketing_cashback:fintech:rate'] = 0.1
    business_user['meta']['cashback_sponsor:discount_cashback'] = 0.1
    business_user['meta']['driver_funded_discount_value'] = 2.55555
    business_user['price']['strikeout'] = 450
    business_user['price']['total'] = 360
    return response


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'routestats', 'dst': 'protocol'}],
    TVM_SERVICES={'routestats': 2020659, 'protocol': 13},
    ALL_CATEGORIES=['business', 'econom'],
)
def test_internal_routestats_extended(
        local_services,
        mockserver,
        experiments3,
        taxi_protocol,
        load_json,
        tvm2_client,
        load,
):
    experiments3.add_experiments_json(
        load_json('experiments3_extend_response.json'),
    )

    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def _mock_v2_prepare(request):
        return fixed_pdp_response(load_json('pdp_response.json'))

    # to generate use `tvmknife unittest service --src 2020659 --dst 13`
    ticket = load('tvm2_ticket_2020659_13')
    request = load_json('request.json')
    request['requirements'] = {'coupon': 'discount300'}
    response = taxi_protocol.post(
        'internal/routestats',
        request,
        headers={'X-Ya-Service-Ticket': ticket},
    )
    assert response.status_code == 200
    assert _mock_v2_prepare.has_calls
    int_data = response.json().get('internal_data')
    assert int_data is not None
    sl = int_data.get('service_levels_data')
    assert sl is not None

    assert sl == [
        {
            'class': 'business',
            'discount': {
                'value': '0.8',
                'description': 'some discount description',
            },
            'final_price': '360',
            'original_price': '450',
            'driver_funded_discount_value': '3',
            'surge': {
                'value': '3',
                'pins_approx': '0.1',
                'trend_time_delta_sec': '0.2',
                'surge_trend': '0.3',
                'synthetic_surge': '3',
            },
            'prices': {'user_total_price': '360'},
            'marketing_cashbacks': ['discount_cashback', 'fintech'],
        },
        {
            'class': 'econom',
            'coupon': {
                'applied': {'type': 'limit', 'limit': {'value': '300'}},
            },
            'final_price': '600',
            'original_price': '900',
            'surge': {'value': '1', 'synthetic_surge': '1'},
            'prices': {'user_total_price': '600'},
        },
    ]


@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'routestats', 'dst': 'protocol'}],
    TVM_SERVICES={'routestats': 2020659, 'protocol': 13},
    ALL_CATEGORIES=['econom'],
    ALTPIN_PRICE_GAIN_RATIO_DEGRADATION=-0.03,
    ALTPIN_MONEY_ZONES={
        '__default__': {
            'price_gain_absolute': 2,
            'price_gain_absolute_minorder': 0,
            'price_gain_ratio': 0,
            'route_gain_ratio': 0,
            'time_gain_ratio': 0,
        },
    },
)
@pytest.mark.now('2017-05-25T23:55:00+0300')
@pytest.mark.experiments3(filename='exp3_alt_point_switcher_b.json')
def test_altpin_b(
        local_services,
        taxi_protocol,
        tvm2_client,
        db,
        load_json,
        mockserver,
        now,
        pricing_data_preparer,
        load,
):
    _set_default_tariff_info_and_prices(pricing_data_preparer)

    @mockserver.json_handler('/addrs.yandex/search')
    def mock_yamaps(request):
        query = dict(
            arg_str.split('=')
            for arg_str in request.query_string.decode().split('&')
        )

        if query['ll'] == '37.584251%2C55.737545':
            return load_json('yamaps_original_b.json')
        return load_json('yamaps_altpin.json')

    @mockserver.json_handler('/pin_storage/v1/create_pin')
    def mock_pin_storage_create_pin(request):
        request_json = json.loads(request.get_data()).get('pin')
        assert 'tariff_zone' in request_json
        assert 'altpin_offer_id' in request_json

    @mockserver.json_handler('/alt/alt/v1/pin')
    def mock_pickup_altpoints(request):
        body = json.loads(request.get_data())
        assert body['selected_class'] == 'econom'
        assert len(body['extra']['prices']) == 1
        assert body['surge_value']
        assert body['altoffer_types'] == ['b']
        return load_json('altpoints.json')

    pricing_data_preparer.set_fixed_price(enable=True)
    pricing_data_preparer.set_trip_information(time=600, distance=4200)
    pricing_data_preparer.set_cost(
        user_cost=90, driver_cost=90, category='econom',
    )
    pricing_data_preparer.push()
    pricing_data_preparer.push()
    pricing_data_preparer.push()
    pricing_data_preparer.push()
    pricing_data_preparer.set_trip_information(time=1380, distance=6300)
    pricing_data_preparer.set_cost(
        user_cost=99, driver_cost=99, category='econom',
    )
    pricing_data_preparer.push()

    request = load_json('request.json')
    expected_response = load_json('expected_response.json')
    ticket = load('tvm2_ticket_2020659_13')
    response = taxi_protocol.post(
        'internal/routestats',
        request,
        headers={'X-Ya-Service-Ticket': ticket},
    )

    assert response.status_code == 200
    response_without_offer = response.json()
    main_offer_id = response_without_offer.pop('offer')
    response_without_offer['internal_data']['alternatives'][0].pop('offer_id')
    alt_offer_id = response_without_offer['alternatives']['options'][0].pop(
        'offer',
    )
    del response_without_offer['alternatives']['options'][0]['service_levels'][
        0
    ]['offer']
    del response_without_offer['service_levels'][0]['offer']
    assert response_without_offer == expected_response

    main_offer = utils.get_offer(main_offer_id, db)
    alt_offer = utils.get_offer(alt_offer_id, db)

    assert main_offer
    assert alt_offer

    assert 'alternative_type' not in main_offer
    assert alt_offer['alternative_type'] == 'altpin_b'


@dataclasses.dataclass(frozen=True)
class MainOfferParams:
    total_price: float
    discount_value: Optional[float] = None
    strikeout_price: Optional[float] = None
    meta_user_total_price: Optional[float] = None


class AlternativeType(enum.IntEnum):
    UNDEFINED = enum.auto()
    PAID_SUPPLY = enum.auto()
    ALT_PIN = enum.auto()
    ANTISURGE = enum.auto()


@dataclasses.dataclass(frozen=True)
class AlternativeParams(MainOfferParams):
    type: AlternativeType = AlternativeType.UNDEFINED


@dataclasses.dataclass(frozen=True)
class InternalDataResult:
    original_price: str
    final_price: str
    user_total_price: str
    discount_value: Optional[float] = None
    surge_value: Optional[float] = None
    is_paid_supply: Optional[bool] = None
    synthetic_surge: Optional[str] = None


MAIN_OFFER_BASE = MainOfferParams(
    total_price=451, discount_value=0.4, strikeout_price=852,
)

MAIN_OFFER_CASHBACK = MainOfferParams(
    total_price=400,
    discount_value=0.4,
    strikeout_price=852,
    meta_user_total_price=500,  # only when cashback comes
)


def _setup_pdp(pricing_data_preparer, offer_params: MainOfferParams):
    # we are simulating case, when user have cashback (from Plus) and
    # also have discount

    # cashback subtracted
    pricing_data_preparer.set_cost(
        user_cost=offer_params.total_price,
        driver_cost=offer_params.total_price,
    )
    pricing_data_preparer.set_discount(
        {
            'description': 'some discount description',
            'reason': 'for_all',
            'method': 'subvention-fix',
            'limited_rides': False,
        },
    )
    pricing_data_preparer.set_strikeout(offer_params.strikeout_price)

    pricing_data_preparer.set_meta(
        'discount_value', offer_params.discount_value,
    )
    if offer_params.meta_user_total_price is not None:
        pricing_data_preparer.set_meta(
            'user_total_price', offer_params.meta_user_total_price,
        )


def _assert_internal_sl(
        service_levels_data: List[dict], expected: List[InternalDataResult],
):
    expected_service_levels = []
    for sl in expected:
        level: dict = {
            'class': 'comfortplus',
            'discount': {
                'value': str(sl.discount_value or 1),
                'description': 'some discount description',
            },
            'final_price': sl.final_price,
            'original_price': sl.original_price,
            'surge': {
                'value': str(sl.surge_value or 1),
                'synthetic_surge': str(sl.synthetic_surge or 1),
            },
            'prices': {'user_total_price': sl.user_total_price},
        }
        if sl.is_paid_supply:
            level['is_paid_supply'] = bool(sl.is_paid_supply or False)

        expected_service_levels.append(level)

    assert (
        sorted(service_levels_data, key=lambda x: x['class'])
        == expected_service_levels
    )


def _assert_user_total_response(
        response, pricing_data_preparer, expected: List[InternalDataResult],
):
    assert response.status_code == 200
    assert pricing_data_preparer.calls > 0
    int_data = response.json().get('internal_data')
    assert int_data is not None
    sl = int_data.get('service_levels_data')
    assert sl is not None

    _assert_internal_sl(sl, expected)
    return int_data


@pytest.mark.parametrize(
    'main_offer, expected',
    [
        (
            MAIN_OFFER_BASE,
            InternalDataResult(
                final_price='451',
                discount_value=0.6,
                original_price='852',
                user_total_price='451',
            ),
        ),
        (
            MAIN_OFFER_CASHBACK,
            InternalDataResult(
                final_price='400',
                discount_value=0.6,
                original_price='852',
                user_total_price='500',
            ),
        ),
    ],
    ids=['main: no cashback', 'main: cashback'],
)
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'routestats', 'dst': 'protocol'}],
    TVM_SERVICES={'routestats': 2020659, 'protocol': 13},
    ALL_CATEGORIES=['comfortplus'],
)
@pytest.mark.experiments3(filename='experiments.json')
@pytest.mark.experiments3(filename='experiments3_extend_response.json')
def test_user_total_price_main(
        local_services,
        mockserver,
        experiments3,
        taxi_protocol,
        load_json,
        tvm2_client,
        load,
        pricing_data_preparer,
        main_offer: MainOfferParams,
        expected: InternalDataResult,
):
    _setup_pdp(pricing_data_preparer, main_offer)

    # to generate use `tvmknife unittest service --src 2020659 --dst 13`
    ticket = load('tvm2_ticket_2020659_13')
    request = load_json('request.json')
    response = taxi_protocol.post(
        'internal/routestats',
        request,
        headers={'X-Ya-Service-Ticket': ticket},
    )

    _assert_user_total_response(response, pricing_data_preparer, [expected])


# inspired by test_routestats.py::test_altpin_price_delta_not_zero
@pytest.mark.parametrize(
    'main_offer, alternative, expected, expected_alt',
    [
        (
            MAIN_OFFER_BASE,
            AlternativeParams(
                type=AlternativeType.ALT_PIN,
                total_price=100,
                discount_value=0.4,
                strikeout_price=250,
            ),
            InternalDataResult(
                final_price='451',
                discount_value=0.6,
                original_price='852',
                user_total_price='451',
            ),
            InternalDataResult(
                final_price='100',
                discount_value=0.6,
                original_price='250',
                user_total_price='100',
            ),
        ),
        (
            MAIN_OFFER_BASE,
            AlternativeParams(
                type=AlternativeType.ALT_PIN,
                total_price=100,
                discount_value=0.4,
                strikeout_price=250,
                meta_user_total_price=150,
            ),
            InternalDataResult(
                final_price='451',
                discount_value=0.6,
                original_price='852',
                user_total_price='451',
            ),
            InternalDataResult(
                final_price='100',
                discount_value=0.6,
                original_price='250',
                user_total_price='150',
            ),
        ),
        (
            MAIN_OFFER_CASHBACK,
            AlternativeParams(
                type=AlternativeType.ALT_PIN,
                total_price=100,
                discount_value=0.4,
                strikeout_price=250,
            ),
            InternalDataResult(
                final_price='400',
                discount_value=0.6,
                original_price='852',
                user_total_price='500',
                synthetic_surge='1',
            ),
            InternalDataResult(
                final_price='100',
                discount_value=0.6,
                original_price='250',
                user_total_price='100',
            ),
        ),
        (
            MAIN_OFFER_CASHBACK,
            AlternativeParams(
                type=AlternativeType.ALT_PIN,
                total_price=100,
                discount_value=0.4,
                strikeout_price=250,
                meta_user_total_price=150,
            ),
            InternalDataResult(
                final_price='400',
                discount_value=0.6,
                original_price='852',
                user_total_price='500',
            ),
            InternalDataResult(
                final_price='100',
                discount_value=0.6,
                original_price='250',
                user_total_price='150',
                synthetic_surge='1',
            ),
        ),
    ],
    ids=[
        'main: no cashback, alt_pin: no cashback',
        'main: no cashback, alt_pin: cashback',
        'main: cashback, alt_pin: no cashback',
        'main: cashback, alt_pin: cashback',
    ],
)
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'routestats', 'dst': 'protocol'}],
    TVM_SERVICES={'routestats': 2020659, 'protocol': 13},
    ALL_CATEGORIES=['comfortplus'],
)
@pytest.mark.experiments3(filename='experiments.json')
@pytest.mark.experiments3(filename='experiments3_extend_response.json')
# === alt pin marks ===
@pytest.mark.config(
    ALTPIN_PRICE_GAIN_RATIO_DEGRADATION=-0.03,
    ALTPIN_MONEY_THRESHOLD_DEST_TIME=0,
    ALTPIN_ALLOWED_CLASSES=['comfortplus'],
)
@pytest.mark.experiments3(filename='exp3_alt_point_switcher.json')
@pytest.mark.now('2017-05-25T11:30:00+0300')
def test_user_total_price_alt_pin(
        local_services,
        mockserver,
        experiments3,
        taxi_protocol,
        load_json,
        tvm2_client,
        load,
        pricing_data_preparer,
        main_offer: MainOfferParams,
        alternative: AlternativeParams,
        expected: InternalDataResult,
        expected_alt: InternalDataResult,
):
    if alternative.type != AlternativeType.ALT_PIN:
        raise ValueError('incorrect alternative type')

    @mockserver.json_handler('/alt/alt/v1/pin')
    def mock_alt_pin(request):
        body = json.loads(request.get_data())
        assert len(body['extra']['prices']) == 1
        assert body['surge_value']
        return load_json('altpin/altpoints.json')

    # alt pin 1
    _setup_pdp(pricing_data_preparer, alternative)
    pricing_data_preparer.push()

    # main offer (need to be last)
    pricing_data_preparer.delete_meta('user_total_price')
    _setup_pdp(pricing_data_preparer, main_offer)
    pricing_data_preparer.push()

    # to generate use `tvmknife unittest service --src 2020659 --dst 13`
    ticket = load('tvm2_ticket_2020659_13')

    request = load_json('request.json')
    request['suggest_alternatives'] = True
    request['selected_class'] = 'comfortplus'
    request['selected_class_only'] = True

    response = taxi_protocol.post(
        'internal/routestats',
        request,
        headers={'X-Ya-Service-Ticket': ticket},
    )

    # main offer
    int_data = _assert_user_total_response(
        response, pricing_data_preparer, [expected],
    )

    alternatives = int_data.get('alternatives')
    assert alternatives and len(alternatives) == 1
    alt_pin = alternatives[0]
    assert alt_pin.get('type') == 'altpin'
    _assert_internal_sl(alt_pin['service_levels_data'], [expected_alt])


@pytest.mark.parametrize(
    'main_offer, alternative, expected, expected_alt',
    [
        (
            MAIN_OFFER_BASE,
            AlternativeParams(
                type=AlternativeType.ANTISURGE,
                total_price=100,
                discount_value=0.4,
                strikeout_price=250,
            ),
            InternalDataResult(
                final_price='451',
                discount_value=0.6,
                original_price='852',
                user_total_price='451',
            ),
            InternalDataResult(
                final_price='100',
                discount_value=0.6,
                original_price='250',
                user_total_price='100',
                surge_value=0.3,
            ),
        ),
        (
            MAIN_OFFER_BASE,
            AlternativeParams(
                type=AlternativeType.ANTISURGE,
                total_price=100,
                discount_value=0.4,
                strikeout_price=250,
                meta_user_total_price=150,
            ),
            InternalDataResult(
                final_price='451',
                discount_value=0.6,
                original_price='852',
                user_total_price='451',
            ),
            InternalDataResult(
                final_price='100',
                discount_value=0.6,
                original_price='250',
                user_total_price='150',
                surge_value=0.3,
            ),
        ),
        (
            MAIN_OFFER_CASHBACK,
            AlternativeParams(
                type=AlternativeType.ANTISURGE,
                total_price=100,
                discount_value=0.4,
                strikeout_price=250,
            ),
            InternalDataResult(
                final_price='400',
                discount_value=0.6,
                original_price='852',
                user_total_price='500',
            ),
            InternalDataResult(
                final_price='100',
                discount_value=0.6,
                original_price='250',
                user_total_price='100',
                surge_value=0.3,
            ),
        ),
        (
            MAIN_OFFER_CASHBACK,
            AlternativeParams(
                type=AlternativeType.ANTISURGE,
                total_price=100,
                discount_value=0.4,
                strikeout_price=250,
                meta_user_total_price=150,
            ),
            InternalDataResult(
                final_price='400',
                discount_value=0.6,
                original_price='852',
                user_total_price='500',
            ),
            InternalDataResult(
                final_price='100',
                discount_value=0.6,
                original_price='250',
                user_total_price='150',
                surge_value=0.3,
            ),
        ),
    ],
    ids=[
        'main: no cashback, antisurge: no cashback',
        'main: no cashback, antisurge: cashback',
        'main: cashback, antisurge: no cashback',
        'main: cashback, antisurge: cashback',
    ],
)
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'routestats', 'dst': 'protocol'}],
    TVM_SERVICES={'routestats': 2020659, 'protocol': 13},
    ALL_CATEGORIES=['comfortplus'],
)
@pytest.mark.experiments3(filename='experiments.json')
@pytest.mark.experiments3(filename='experiments3_extend_response.json')
# === antisurge marks ===
@pytest.mark.user_experiments('explicit_antisurge')
@pytest.mark.config(
    EXPLICIT_ANTISURGE_SETTINGS={
        '__default__': {
            'MIN_ABS_GAIN': 20,
            'MIN_REL_GAIN': 0.2,
            'MIN_SURGE_B': 0.9,
        },
    },
    EXPLICIT_ANTISURGE_ETA_OFFSET={'__default__': 5},
    EXPLICIT_ANTISURGE_PIN_CARD_ICON='',
)
def test_user_total_price_antisurge(
        local_services,
        mockserver,
        experiments3,
        taxi_protocol,
        load_json,
        tvm2_client,
        load,
        pricing_data_preparer,
        main_offer: MainOfferParams,
        alternative: AlternativeParams,
        expected: InternalDataResult,
        expected_alt: InternalDataResult,
):
    if alternative.type != AlternativeType.ANTISURGE:
        raise ValueError('incorrect alternative type')

    _setup_pdp(pricing_data_preparer, main_offer)
    pricing_data_preparer.set_user_surge(
        sp=1.0, explicit_antisurge=0.3, value_b=1.0,
    )

    antisurge: Dict[str, Any] = {
        # cashback subtracted
        'total': alternative.total_price,
    }
    if alternative.strikeout_price is not None:
        antisurge['strikeout'] = alternative.strikeout_price

    meta = {}
    if alternative.meta_user_total_price is not None:
        # cashback not subtracted
        meta['user_total_price'] = alternative.meta_user_total_price
    if alternative.discount_value is not None:
        meta['discount_value'] = alternative.discount_value
    if meta:
        antisurge['meta'] = meta

    pricing_data_preparer.set_antisurge(antisurge)

    # to generate use `tvmknife unittest service --src 2020659 --dst 13`
    ticket = load('tvm2_ticket_2020659_13')

    request = load_json('request.json')
    request['suggest_alternatives'] = True
    request['skip_estimated_waiting'] = False

    response = taxi_protocol.post(
        'internal/routestats',
        request,
        headers={'X-Ya-Service-Ticket': ticket},
    )

    # main offer
    int_data = _assert_user_total_response(
        response, pricing_data_preparer, [expected],
    )

    alternatives = int_data.get('alternatives')
    assert alternatives and len(alternatives) == 1
    alt_pin = alternatives[0]
    assert alt_pin.get('type') == 'explicit_antisurge'
    _assert_internal_sl(alt_pin['service_levels_data'], [expected_alt])


# paid supply test inspired by test_routestats.py::test_paid_supply
ANDROID_WITH_PAID_SUPPLY: str = (
    'yandex-taxi/3.82.0.7675 Android/7.0 (android test client)'
)

BASE_PAID_SUPPLY_CONFIG = {
    'NO_CARS_ORDER_AVAILABLE_BY_ZONES': ['moscow'],
    'NO_CARS_ORDER_MIN_VERSIONS': {'android': {'version': [3, 45, 0]}},
    'PAID_SUPPLY_MIN_VERSIONS': {'android': {'version': [3, 82, 0]}},
    'PAID_SUPPLY_MIN_TAXIMETER_VERSION': '8.99',
    'PAID_SUPPLY_LONG_TRIP_CRITERIA': {
        'moscow': {
            '__default__': {'apply': 'either', 'distance': 1, 'duration': 1},
        },
    },
    'ENABLE_PAID_CANCEL': True,
}


@pytest.fixture(name='force_paid_supply')
def _force_paid_supply(mockserver, load_json, experiments3):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, 1)

    @mockserver.json_handler('/mlaas/no_cars_order/v1')
    def mock_no_cars_order_mlaas(request):
        return load_json('paid_supply/no_cars_order_mlaas.json')

    @mockserver.json_handler('/driver-eta/eta')
    def mock_driver_eta(request):
        # forcing initial request to have no cars
        req = json.loads(request.get_data())
        if 'extended_radius' in req and req['extended_radius']:
            assert 'min_taximeter_version' in req
            assert req['min_taximeter_version'] == '8.99'
            return utils.mock_driver_eta(
                load_json, 'paid_supply/driver_eta_extended_radius.json',
            )(request)
        else:
            assert 'min_taximeter_version' not in req
            return utils.mock_driver_eta(
                load_json, 'paid_supply/driver_eta.json',
            )(request)


@pytest.mark.parametrize(
    'main_offer, alternative, expected',
    [
        (
            MAIN_OFFER_BASE,
            AlternativeParams(
                type=AlternativeType.PAID_SUPPLY,
                total_price=1140,
                discount_value=0.4,
                strikeout_price=1617,
            ),
            InternalDataResult(
                final_price='1140',
                discount_value=0.6,
                original_price='1617',
                user_total_price='1140',
                is_paid_supply=True,
            ),
        ),
        (
            MAIN_OFFER_BASE,
            AlternativeParams(
                type=AlternativeType.PAID_SUPPLY,
                total_price=1140,
                discount_value=0.4,
                strikeout_price=1617,
                meta_user_total_price=1200,  # only when cashback comes
            ),
            InternalDataResult(
                final_price='1140',
                discount_value=0.6,
                original_price='1617',
                user_total_price='1200',
                is_paid_supply=True,
            ),
        ),
        (
            MAIN_OFFER_CASHBACK,
            AlternativeParams(
                type=AlternativeType.PAID_SUPPLY,
                total_price=1140,
                discount_value=0.4,
                strikeout_price=1617,
            ),
            InternalDataResult(
                final_price='1140',
                discount_value=0.6,
                original_price='1617',
                user_total_price='1140',
                is_paid_supply=True,
            ),
        ),
        (
            MAIN_OFFER_CASHBACK,
            AlternativeParams(
                type=AlternativeType.PAID_SUPPLY,
                total_price=1140,
                discount_value=0.4,
                strikeout_price=1617,
                meta_user_total_price=1200,  # only when cashback comes
            ),
            InternalDataResult(
                final_price='1140',
                discount_value=0.6,
                original_price='1617',
                user_total_price='1200',
                is_paid_supply=True,
            ),
        ),
    ],
    ids=[
        'main: no cashback, paid_supply: no cashback',
        'main: no cashback, paid_supply: cashback',
        'main: cashback, paid_supply: no cashback',
        'main: cashback, paid_supply: cashback',
    ],
)
@pytest.mark.config(
    TVM_ENABLED=True,
    TVM_RULES=[{'src': 'routestats', 'dst': 'protocol'}],
    TVM_SERVICES={'routestats': 2020659, 'protocol': 13},
    ALL_CATEGORIES=['comfortplus'],
)
@pytest.mark.now('2017-05-25T11:30:00+0300')
@pytest.mark.experiments3(filename='experiments.json')
@pytest.mark.experiments3(filename='experiments3_extend_response.json')
# === paid supply marks ===
@pytest.mark.config(
    **BASE_PAID_SUPPLY_CONFIG,
    PAID_SUPPLY_ALLOW_CASH_FALLBACK={
        '__default__': {
            '__default__': {
                'allow_cash': True,
                'enable_max_allowed_price': False,
                'max_allowed_price': 1000,
            },
        },
    },
)
@pytest.mark.user_experiments(
    'fixed_price', 'no_cars_order_available', 'surge_distance',
)
@pytest.mark.experiments3(filename='exp3_paid_cancel.json')
@pytest.mark.experiments3(filename='exp3_paid_supply_paid_cancel.json')
def test_user_total_price_paid_supply(
        local_services,
        mockserver,
        experiments3,
        taxi_protocol,
        load_json,
        tvm2_client,
        load,
        pricing_data_preparer,
        force_paid_supply,
        main_offer: MainOfferParams,
        alternative: AlternativeParams,
        expected: InternalDataResult,
):
    if alternative.type != AlternativeType.PAID_SUPPLY:
        raise ValueError('incorrect alternative type')

    # 1. setting PDP
    _setup_pdp(pricing_data_preparer, main_offer)

    # long trip
    pricing_data_preparer.set_trip_information(
        time=1421.5866954922676, distance=7514.629286628636,
    )

    paid_supply: Dict[str, Any] = {
        # cashback subtracted
        'total': alternative.total_price,
    }
    if alternative.strikeout_price is not None:
        paid_supply['strikeout'] = alternative.strikeout_price

    meta = {}
    if alternative.meta_user_total_price is not None:
        # cashback not subtracted
        meta['user_total_price'] = alternative.meta_user_total_price
    if alternative.discount_value is not None:
        meta['discount_value'] = alternative.discount_value
    if meta:
        paid_supply['meta'] = meta

    pricing_data_preparer.set_paid_supply(paid_supply)

    # preparing paid supply

    # to generate use `tvmknife unittest service --src 2020659 --dst 13`
    ticket = load('tvm2_ticket_2020659_13')
    request = load_json('request.json')
    response = taxi_protocol.post(
        'internal/routestats',
        request,
        headers={
            'X-Ya-Service-Ticket': ticket,
            'User-Agent': ANDROID_WITH_PAID_SUPPLY,
        },
    )
    _assert_user_total_response(response, pricing_data_preparer, [expected])
