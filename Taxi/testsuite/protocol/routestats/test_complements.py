from copy import deepcopy
import dataclasses
import json
from typing import Optional

import pytest

from order_offers_switch_parametrize import ORDER_OFFERS_SAVE_SWITCH
from protocol.routestats import utils

USER_IN_COMPLEMENT_EXP = 'b300bda7d41b4bae8d58dfa93221ef16'
USER_IN_PW_AVAILABILITY_EXP = '7c5c00000000000000000000582af45b'
USER_UID_IN_COMPLEMENT_EXP = '4003514353'
USER_NOT_IN_COMPLEMENT_EXP = '7c5cea02692a49a5b5e277e4582af45b'

FRANCE_IP = '89.185.38.136'
RUSSIA_IP = '2.60.1.1'
DUMMY_IP = '0.0.0.0'

TANKER_KEY_PREFIX = 'routestats.brandings.complement_personal_wallet_payment'

RIDE_COST = 330
DEFAULT_BALANCE = 300

PLUS_BALANCES_RESPONSE = {
    'balances': [
        {
            'wallet_id': 'wallet_id/some_number_value',
            'currency': 'RUB',
            'balance': str(DEFAULT_BALANCE),
        },
        {
            'wallet_id': 'wallet_id/some_number_value',
            'currency': 'USD',
            'balance': '100500',
        },
    ],
}


COMPLEMENTS = [
    {
        'type': 'personal_wallet',
        'payment_method_id': 'wallet_id/some_number_value',
    },
]


def _make_branding(value, covers_ride_cost=False):
    extra = {
        'payment': {
            'type': 'personal_wallet',
            'payment_method_id': 'wallet_id/some_number_value',
        },
        'cost_coverage': 'full' if covers_ride_cost else 'partial',
    }
    branding = {'type': 'complement_payment', 'extra': extra}
    if covers_ride_cost:
        branding.update({'title': 'Поехать бесплатно'})
    else:
        branding.update(
            {
                'title': 'Поехать дешевле',
                'subtitle': f'Баланс: {value} баллов',
            },
        )
    return branding


BRANDING_LESS_THAN_COST = _make_branding(DEFAULT_BALANCE)
BRANDING_COVERS_RIDE_COST = _make_branding(RIDE_COST, covers_ride_cost=True)
MIN_DISPLAY_AMOUNT = 50

pytestmark = [
    pytest.mark.now('2017-05-26T03:40:00+0300'),
    pytest.mark.config(
        PERSONAL_WALLET_ENABLED=True,
        CURRENCY_ROUNDING_RULES={'__default__': {'__default__': 10}},
        CURRENCY_FORMATTING_RULES={'__default__': {'__default__': 2}},
        COMPLEMENT_TYPES_COMPATIBILITY_MAPPING={
            'personal_wallet': ['card', 'applepay', 'googlepay'],
        },
    ),
    pytest.mark.user_experiments('fixed_price'),
    pytest.mark.experiments3(filename='experiments3.json'),
]


@dataclasses.dataclass()
class PricingDataPreparerContext:
    coupon_value: Optional[int]
    user_tags: Optional[dict]


@pytest.fixture
def pricing_data_preparer_context():
    return PricingDataPreparerContext(None, None)


@pytest.fixture(autouse=True)
def mock_new_pricing(mockserver, load_json, pricing_data_preparer_context):
    def get_wallet_balance(request):
        # for some reason codegen client uses
        # application/x-www-form-urlencoded for content type,
        # so we parse json manually
        request_json = json.loads(request.get_data().decode())
        return (
            request_json['user_info']['payment_info']
            .get('complements', {})
            .get('personal_wallet', {})
            .get('balance', 0)
        )

    def get_price(user_pricing_data):
        return user_pricing_data['price']['total']

    def apply_complements(request, user_pricing_data):
        price = get_price(user_pricing_data)
        min_price = user_pricing_data['data']['tariff']['boarding_price']

        balance = get_wallet_balance(request)

        user_pricing_data['meta']['display_price'] = max(price - balance, 0)
        user_pricing_data['meta']['display_min_price'] = max(
            min_price - balance, 0,
        )
        user_pricing_data['data']['complements']['personal_wallet'][
            'balance'
        ] = balance

    def apply_coupon(user_pricing_data):
        coupon_value = pricing_data_preparer_context.coupon_value
        if not coupon_value:
            return
        price_before_coupon = get_price(user_pricing_data)

        # assume percent=100% and limit=value
        price_after_coupon = max(price_before_coupon - coupon_value, 0)

        coeff = price_after_coupon / price_before_coupon
        user_pricing_data['price']['total'] *= coeff

        user_pricing_data['data']['coupon'] = make_coupon(coupon_value)
        user_pricing_data['meta']['price_before_coupon'] = price_before_coupon

    def apply_tags(user_pricing_data):
        user_tags = pricing_data_preparer_context.user_tags
        if not user_tags:
            return
        user_pricing_data['data']['user_tags'] = user_tags

    @mockserver.json_handler('/pricing_data_preparer/v2/prepare')
    def mock_pricing_data_preparer(request):
        response = load_json('pricing-data-preparer-response.json')
        comfortplus_category_info = response['categories']['comfortplus']
        # just copy
        response['categories']['business'] = deepcopy(
            comfortplus_category_info,
        )
        response['categories']['vip'] = deepcopy(comfortplus_category_info)
        response['categories']['minivan'] = deepcopy(comfortplus_category_info)
        for category in response['categories']:
            user_pricing_data = response['categories'][category]['user']
            apply_coupon(user_pricing_data)
            apply_complements(request, user_pricing_data)
            apply_tags(user_pricing_data)

        return response


@pytest.fixture
def mocks(mockserver, load_json):
    @mockserver.json_handler('/surge_calculator/v1/calc-surge')
    def mock_surge_get_surge(request):
        return utils.get_surge_calculator_response(request, 1)


def _gather_complements_branding(level):
    brandings = level.get('brandings', [])
    return [br for br in brandings if br['type'] == 'complement_payment']


def _get_all_complements_brandings(content, classes=None):
    result = []
    for sl in content['service_levels']:
        if classes is None or sl['class'] in classes:
            cashback = _gather_complements_branding(sl)
            if cashback:
                result.append(cashback[0])
    return result


def plus_balances(mockserver, response_code, balance):
    if response_code != 200:
        return mockserver.make_response(status=response_code)
    response = deepcopy(PLUS_BALANCES_RESPONSE)
    response['balances'][0]['balance'] = str(balance)
    return response


def make_coupon(value: int):
    return {
        'valid': True,
        'format_currency': True,
        'descr': 'description',
        'details': ['some_detail'],
        'value': value,
        'percent': 100,
        'limit': value,
        'valid_classes': ['econom', 'comfortplus'],
        'currency_code': 'rub',
    }


def check_complement_personal_wallet_payment_branding(
        content, expected_branding: dict,
):
    econom_brandings = _get_all_complements_brandings(
        content, classes=['econom'],
    )
    if expected_branding is not None:
        assert econom_brandings
        branding = econom_brandings[0]
        assert branding == expected_branding
    else:
        assert not econom_brandings

    # personal wallet payment restricted for comfortplus
    comfortplus_brandings = _get_all_complements_brandings(
        content, classes=['comfortplus'],
    )
    assert not comfortplus_brandings


@pytest.mark.parametrize(
    'user_id, balance, response_code, expected_branding',
    [
        (USER_IN_COMPLEMENT_EXP, '300', 200, BRANDING_LESS_THAN_COST),
        # corner case when `ride cost == wallet balance`
        (USER_IN_COMPLEMENT_EXP, '330', 200, _make_branding(330)),
        (USER_IN_COMPLEMENT_EXP, '350', 200, BRANDING_COVERS_RIDE_COST),
        (USER_IN_COMPLEMENT_EXP, '0', 200, None),
        (USER_IN_COMPLEMENT_EXP, '300', 403, None),
        (USER_IN_COMPLEMENT_EXP, '300', 500, None),
        (USER_NOT_IN_COMPLEMENT_EXP, '300', 200, None),
    ],
)
@pytest.mark.config(PLUS_WALLET_PROTOCOL_BALANCES_ENABLED=True)
def test_complement_personal_wallet_payment_branding_basic(
        local_services_fixed_price,
        taxi_protocol,
        mockserver,
        db,
        load_json,
        user_id,
        balance,
        response_code,
        expected_branding,
):
    @mockserver.json_handler('/plus_wallet/v1/balances')
    def mock_balances(request):
        assert request.args['yandex_uid']
        assert request.args['currencies']
        return plus_balances(mockserver, response_code, balance)

    request = load_json('simple_request.json')
    request['id'] = user_id

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200

    content = response.json()
    check_complement_personal_wallet_payment_branding(
        content, expected_branding,
    )


@pytest.mark.parametrize(
    'has_ya_plus, has_cashback_plus, remote_ip, is_expected_branding',
    [
        (False, False, RUSSIA_IP, False),
        (False, True, RUSSIA_IP, False),
        (True, False, RUSSIA_IP, False),
        (True, True, FRANCE_IP, False),
        (True, True, DUMMY_IP, False),
        (True, True, RUSSIA_IP, True),
    ],
    ids=[
        'no plus no cashback',
        'no plus',
        'no cashback',
        'wrong France ip',
        'wrong dummy ip',
        'all ok',
    ],
)
@pytest.mark.config(PLUS_WALLET_PROTOCOL_BALANCES_ENABLED=True)
def test_complement_personal_wallet_payment_branding_by_subscription_status(
        local_services_fixed_price,
        taxi_protocol,
        mockserver,
        db,
        load_json,
        has_ya_plus,
        has_cashback_plus,
        remote_ip,
        is_expected_branding,
):
    @mockserver.json_handler('/plus_wallet/v1/balances')
    def mock_balances(request):
        assert request.args['yandex_uid']
        assert request.args['currencies']
        return plus_balances(mockserver, 200, 300)

    db.users.update(
        {'_id': USER_IN_PW_AVAILABILITY_EXP},
        {
            '$set': {
                'has_ya_plus': has_ya_plus,
                'has_cashback_plus': has_cashback_plus,
            },
        },
    )

    request = load_json('simple_request.json')
    request['id'] = USER_IN_PW_AVAILABILITY_EXP

    response = taxi_protocol.post(
        '3.0/routestats', request, headers={'X-Remote-IP': remote_ip},
    )
    assert response.status_code == 200

    content = response.json()
    if is_expected_branding:
        check_complement_personal_wallet_payment_branding(
            content, BRANDING_LESS_THAN_COST,
        )
    else:
        check_complement_personal_wallet_payment_branding(content, None)


@pytest.mark.config(
    LIMITS_BY_CURRENCY={
        'RUB': {'complements_branding_display_min_amount': MIN_DISPLAY_AMOUNT},
    },
)
@pytest.mark.parametrize(
    'main_payment_type, balance, has_complement, expected_branding',
    [
        ('card', DEFAULT_BALANCE, False, BRANDING_LESS_THAN_COST),
        # no branding if "complements" sent in request
        ('card', DEFAULT_BALANCE, True, None),
        ('card', '30', False, None),
        # corner case
        ('card', MIN_DISPLAY_AMOUNT, False, _make_branding(50)),
        ('cash', DEFAULT_BALANCE, False, None),
        ('cash', DEFAULT_BALANCE, True, None),
        ('corp', DEFAULT_BALANCE, False, None),
        ('corp', DEFAULT_BALANCE, True, None),
        ('personal_wallet', DEFAULT_BALANCE, False, None),
        ('personal_wallet', DEFAULT_BALANCE, True, None),
    ],
)
@pytest.mark.config(PLUS_WALLET_PROTOCOL_BALANCES_ENABLED=True)
def test_complement_personal_wallet_payment_branding_types(
        local_services_fixed_price,
        taxi_protocol,
        mockserver,
        db,
        load_json,
        main_payment_type,
        balance,
        has_complement,
        expected_branding,
):
    @mockserver.json_handler('/plus_wallet/v1/balances')
    def mock_balances(request):
        return plus_balances(mockserver, 200, balance)

    request = load_json('simple_request.json')
    request['id'] = USER_IN_COMPLEMENT_EXP
    request['payment']['type'] = main_payment_type
    if has_complement:
        request['payment']['complements'] = COMPLEMENTS

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200

    content = response.json()
    check_complement_personal_wallet_payment_branding(
        content, expected_branding,
    )


@pytest.mark.user_experiments('discount_strike')
@pytest.mark.parametrize(
    'user_id, balance, response_code, expect_changed_description',
    [
        (USER_IN_COMPLEMENT_EXP, '300', 200, True),
        (USER_IN_COMPLEMENT_EXP, '0', 200, False),
        (USER_IN_COMPLEMENT_EXP, '300', 403, False),
        (USER_IN_COMPLEMENT_EXP, '300', 500, False),
        (USER_NOT_IN_COMPLEMENT_EXP, '300', 200, False),
    ],
)
@pytest.mark.config(PLUS_WALLET_PROTOCOL_BALANCES_ENABLED=True)
def test_complement_personal_wallet_payment_strikeout_basic(
        local_services_fixed_price,
        taxi_protocol,
        mockserver,
        load_json,
        user_id,
        balance,
        response_code,
        expect_changed_description,
):
    @mockserver.json_handler('/plus_wallet/v1/balances')
    def mock_balances(request):
        return plus_balances(mockserver, response_code, balance)

    request = load_json('simple_request.json')
    request['id'] = user_id
    request['payment']['complements'] = COMPLEMENTS

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200

    content = response.json()
    levels = content.pop('service_levels')
    for level in levels:
        # we expect no branding if "complements" passed in request
        complements_branding = _gather_complements_branding(level)
        assert not complements_branding

        if level['class'] == 'econom':
            if expect_changed_description:
                assert (
                    level['description'] == 'Ride cost 30\xa0$SIGN$$CURRENCY$'
                )
                assert level['price'] == '30\xa0$SIGN$$CURRENCY$'
                assert level['pin_description'].startswith(
                    'From here 30\xa0$SIGN$$CURRENCY$',
                )

                assert level['original_price'] == '330\xa0$SIGN$$CURRENCY$'
                # based on tariff_description, not tariff_description_final
                # so not affected by complements
                assert (
                    level['details'][0]['price'] == '330\xa0$SIGN$$CURRENCY$'
                )
            else:
                assert (
                    level['description'] == 'Ride cost 330\xa0$SIGN$$CURRENCY$'
                )
                assert level['price'] == '330\xa0$SIGN$$CURRENCY$'
                assert 'original_price' not in level
        if level['class'] == 'comfortplus':
            # personal wallet payment restricted for comfortplus
            assert 'original_price' not in level


@pytest.mark.user_experiments('discount_strike')
@pytest.mark.parametrize(
    'user_id, balance, response_code, expect_changed_description',
    [
        (USER_IN_COMPLEMENT_EXP, '300', 200, True),
        (USER_IN_COMPLEMENT_EXP, '0', 200, False),
    ],
)
@pytest.mark.config(PLUS_WALLET_PROTOCOL_BALANCES_ENABLED=True)
def test_complement_personal_wallet_payment_strikeout_no_destination(
        mocks,
        taxi_protocol,
        mockserver,
        load_json,
        user_id,
        balance,
        response_code,
        expect_changed_description,
):
    @mockserver.json_handler('/plus_wallet/v1/balances')
    def mock_balances(request):
        return plus_balances(mockserver, response_code, balance)

    request = load_json('simple_request.json')
    request['id'] = user_id
    request['payment']['complements'] = COMPLEMENTS
    del request['route'][1]

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200

    content = response.json()
    levels = content.pop('service_levels')
    for level in levels:
        # we expect no branding if "complements" passed in request
        complements_branding = _gather_complements_branding(level)
        assert not complements_branding

        if level['class'] == 'econom':
            if expect_changed_description:
                assert level['description'] == 'from 0\xa0$SIGN$$CURRENCY$'
                assert level['price'] == '0\xa0$SIGN$$CURRENCY$'
                # original_price and pin_description
                # are only for routes with destination

                # based on tariff_description, not tariff_description_final
                # so not affected by complements
                assert (
                    level['details'][0]['price'] == '100\xa0$SIGN$$CURRENCY$'
                )
            else:
                assert level['description'] == 'from 100\xa0$SIGN$$CURRENCY$'
                assert level['price'] == '100\xa0$SIGN$$CURRENCY$'
        if level['class'] == 'comfortplus':
            # personal wallet payment restricted for comfortplus
            assert level['description'] == 'from 200\xa0$SIGN$$CURRENCY$'
            assert level['price'] == '200\xa0$SIGN$$CURRENCY$'


@pytest.mark.user_experiments('discount_strike')
@pytest.mark.parametrize(
    'user_id, balance, response_code, expect_complements_in_offer',
    [
        (USER_IN_COMPLEMENT_EXP, '300', 200, True),
        (
            USER_IN_COMPLEMENT_EXP,
            '0',
            200,
            True,
        ),  # we dont check this, maybe should
        (USER_IN_COMPLEMENT_EXP, '300', 403, True),  # same
        (USER_IN_COMPLEMENT_EXP, '300', 500, True),  # same
        (USER_NOT_IN_COMPLEMENT_EXP, '300', 200, False),
    ],
)
@pytest.mark.config(PLUS_WALLET_PROTOCOL_BALANCES_ENABLED=True)
@ORDER_OFFERS_SAVE_SWITCH
def test_complements_in_offer(
        local_services_fixed_price,
        taxi_protocol,
        mockserver,
        db,
        load_json,
        mock_order_offers,
        order_offers_save_enabled,
        user_id,
        balance,
        response_code,
        expect_complements_in_offer,
):
    @mockserver.json_handler('/plus_wallet/v1/balances')
    def mock_balances(request):
        return plus_balances(mockserver, response_code, balance)

    request = load_json('simple_request.json')
    request['id'] = user_id
    request['payment']['complements'] = COMPLEMENTS

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200

    content = response.json()
    offer_id = content.pop('offer')
    offer = utils.get_saved_offer(
        db, mock_order_offers, order_offers_save_enabled,
    )
    if order_offers_save_enabled:
        assert mock_order_offers.mock_save_offer.times_called == 1

    assert offer['_id'] == offer_id
    if expect_complements_in_offer:
        assert offer['complements'] == COMPLEMENTS
    else:
        assert 'complements' not in offer


@pytest.mark.parametrize(
    'coupon_value, expected_branding',
    [
        # ride cost is 330
        pytest.param(
            320,
            _make_branding(10, covers_ride_cost=True),
            id='non-zero final cost',
        ),
        pytest.param(330, None, id='exact-coupon-cover'),
        pytest.param(331, None, id='full-coupon-cover'),
    ],
)
@pytest.mark.config(PLUS_WALLET_PROTOCOL_BALANCES_ENABLED=True)
def test_complement_personal_wallet_payment_with_coupon(
        local_services_fixed_price,
        taxi_protocol,
        mockserver,
        pricing_data_preparer_context,
        db,
        load_json,
        coupon_value,
        expected_branding,
):
    @mockserver.json_handler('/plus_wallet/v1/balances')
    def mock_balances(request):
        return plus_balances(mockserver, response_code=200, balance=1000)

    pricing_data_preparer_context.coupon_value = coupon_value

    request = load_json('simple_request.json')
    request['id'] = USER_IN_COMPLEMENT_EXP
    request['requirements'] = {'coupon': 'coupon'}

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200

    content = response.json()

    check_complement_personal_wallet_payment_branding(
        content, expected_branding=expected_branding,
    )


@pytest.mark.parametrize(
    'user_tags, expected_branding',
    [
        pytest.param(
            ['experienced_plus_payer'],
            None,
            marks=(
                pytest.mark.match_tags(
                    entity_type='yandex_uid',
                    entity_value=USER_UID_IN_COMPLEMENT_EXP,
                    entity_tags=['experienced_plus_payer'],
                )
            ),
        ),
        pytest.param(
            ['wrong_tag'],
            BRANDING_LESS_THAN_COST,
            marks=(
                pytest.mark.match_tags(
                    entity_type='user_id',
                    entity_value=USER_UID_IN_COMPLEMENT_EXP,
                    entity_tags=['wrong_tag'],
                )
            ),
        ),
        pytest.param(None, BRANDING_LESS_THAN_COST),
    ],
)
@pytest.mark.config(
    PLUS_WALLET_PROTOCOL_BALANCES_ENABLED=True,
    ROUTESTATS_FETCH_USER_TAGS=True,
)
def test_complement_personal_wallet_payment_branding_disabled_by_tag(
        local_services_fixed_price,
        taxi_protocol,
        mockserver,
        pricing_data_preparer_context,
        load_json,
        user_tags,
        expected_branding,
):
    @mockserver.json_handler('/plus_wallet/v1/balances')
    def mock_balances(request):
        assert request.args['yandex_uid']
        assert request.args['currencies']
        return plus_balances(mockserver, 200, '300')

    pricing_data_preparer_context.user_tags = user_tags

    request = load_json('simple_request.json')
    request['id'] = USER_IN_COMPLEMENT_EXP

    response = taxi_protocol.post('3.0/routestats', request)
    assert response.status_code == 200

    content = response.json()
    check_complement_personal_wallet_payment_branding(
        content, expected_branding,
    )
