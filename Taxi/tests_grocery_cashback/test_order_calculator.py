# pylint: disable=E0401
import decimal
import math

from grocery_mocks.models import country as countries
import pytest

from . import consts
from . import headers

ORDER_ID = 'order_id'
GROCERY_ORDER_ID = 'order_id-grocery'

YT_LOOKUP_ENABLED_DISABLED = pytest.mark.parametrize(
    'yt_lookup',
    [
        pytest.param(
            True,
            marks=pytest.mark.config(GROCERY_CASHBACK_YT_LOOKUP_ENABLED=True),
        ),
        pytest.param(
            False,
            marks=pytest.mark.config(GROCERY_CASHBACK_YT_LOOKUP_ENABLED=False),
        ),
    ],
)

GROCERY_CASHBACK_YT_LOOKUP_DISABLED = pytest.mark.config(
    GROCERY_CASHBACK_YT_LOOKUP_ENABLED=False,
)


def _bool_to_str(flag):
    if flag:
        return 'true'
    return 'false'


@pytest.fixture(name='_transactions')
def _mock_transactions(transactions):
    def _inner(sum_to_pay, currency=countries.Country.Russia.currency):
        transactions.retrieve.mock_response(
            id=ORDER_ID,
            status='init',
            sum_to_pay=sum_to_pay,
            yandex_uid=headers.YANDEX_UID,
            currency=currency,
        )

    return _inner


def _extract_keys(keys, kwargs):
    result = {}

    for key in keys:
        if key in kwargs:
            result.update({key: kwargs[key]})

    return result


@pytest.fixture(name='_grocery_cart')
def _mock_grocery_cart(grocery_cart):
    def _inner(**kwargs):
        grocery_cart.set_cashback_info_response(**kwargs)

        check_request = _extract_keys(['order_id', 'yt_lookup'], kwargs)

        grocery_cart.check_cashback_info_request(**check_request)

    return _inner


@pytest.mark.parametrize('franchise', [True, False])
@pytest.mark.parametrize(
    'cart_items, expected_response_items, cashback, base_amount',
    [
        (
            [
                {
                    'item_id': 'grocery_id1',
                    'title': 'title1',
                    'shelf_type': 'store',
                    'cashback_per_unit': '6',
                    'price': '200',
                    'total_price': '200',
                    'vat': '20',
                },
                {
                    'item_id': 'grocery_id2',
                    'title': 'title2',
                    'shelf_type': 'store',
                    'cashback_per_unit': '10',
                    'price': '200',
                    'total_price': '250',
                    'vat': '20',
                },
            ],
            [
                {
                    'amount': '6',
                    'item_id': 'grocery_id1',
                    'item_total_price': '200',
                    'title': 'title1',
                    'vat_rate': '20',
                },
                {
                    'amount': '10',
                    'item_id': 'grocery_id2',
                    'item_total_price': '250',
                    'title': 'title2',
                    'vat_rate': '20',
                },
            ],
            '16',
            '300',
        ),
        (
            # multiple items in invoice (check sum_to_pay below)
            [
                {
                    'item_id': 'grocery_id3',
                    'title': 'title3',
                    'shelf_type': 'store',
                    'cashback_per_unit': '50',
                    'price': '500',
                    'total_price': '700',
                    'vat': '17',
                },
            ],
            [
                {
                    'amount': '150',  # item-id-3 occurs three times
                    'item_id': 'grocery_id3',
                    'item_total_price': '700',
                    'title': 'title3',
                    'vat_rate': '17',
                },
            ],
            '150',  # item-id-3 occurs three times
            '1200',
        ),
        (
            # ignore items with zero amount
            [
                {
                    'item_id': 'grocery_id4',
                    'title': 'title4',
                    'shelf_type': 'store',
                    'cashback_per_unit': '50',
                    'price': '500',
                    'total_price': '700',
                    'vat': '17',
                },
            ],
            [],
            '0',  # grocery_id4 has zero amount
            '0',
        ),
        (
            # no cashback in cart at all
            [],
            [],
            '0',
            '0',
        ),
    ],
)
@pytest.mark.parametrize('has_plus', [True, False])
@GROCERY_CASHBACK_YT_LOOKUP_DISABLED
async def test_grocery_cashback_calc(
        cashback_order_calculator,
        _transactions,
        _grocery_cart,
        grocery_orders,
        passport,
        franchise,
        cart_items,
        expected_response_items,
        cashback,
        base_amount,
        has_plus,
):
    grocery_orders.add_order(
        order_id=GROCERY_ORDER_ID,
        yandex_uid=headers.YANDEX_UID,
        grocery_flow_version=consts.BASIC_FLOW_VERSION,
    )

    _transactions(
        sum_to_pay=[
            {
                'items': [
                    {'amount': '100', 'item_id': 'grocery_id1_1'},
                    {'amount': '200', 'item_id': 'grocery_id2_1'},
                    {'amount': '300', 'item_id': 'grocery_id3_1'},
                    {'amount': '400', 'item_id': 'grocery_id3_2'},
                    {'amount': '500', 'item_id': 'grocery_id3_3'},
                    {'amount': '0', 'item_id': 'grocery_id4_1'},
                ],
                'payment_type': 'card',
            },
            # this should be ignored in calculation,
            # we dont pay cashback for cashback spent
            {
                'items': [
                    {'amount': '100', 'item_id': 'grocery_id1_1'},
                    {'amount': '200', 'item_id': 'grocery_id2_1'},
                    {'amount': '300', 'item_id': 'grocery_id3_1'},
                    {'amount': '400', 'item_id': 'grocery_id3_2'},
                    {'amount': '500', 'item_id': 'grocery_id3_3'},
                ],
                'payment_type': 'personal_wallet',
            },
        ],
    )

    passport.set_has_plus(has_plus=has_plus)

    _grocery_cart(
        order_id=GROCERY_ORDER_ID, franchise=franchise, items=cart_items,
    )

    response = await cashback_order_calculator(order_id=GROCERY_ORDER_ID)

    assert response.status == 200

    response_json = response.json()
    response_json['payload']['items'].sort(key=lambda k: k['item_id'])

    assert response_json == {
        'cashback': cashback,
        'currency': 'RUB',
        'payload': {
            'cashback_service': 'lavka',
            'cashback_type': 'transaction',
            'franchise': _bool_to_str(franchise),
            'items': expected_response_items,
            'order_id': GROCERY_ORDER_ID,
            'service_id': consts.CASHBACK_SERVICE_ID,
            'base_amount': base_amount,
            'amount': cashback,
            'commission_cashback': '0',
            'currency': 'RUB',
            'city': '',
            'has_plus': _bool_to_str(has_plus),
            'client_id': headers.YANDEX_UID,
            'ticket': consts.TICKET,
        },
    }

    assert passport.times_called() == 1


@pytest.mark.parametrize('cart_cashback_gain', [None, '100'])
@GROCERY_CASHBACK_YT_LOOKUP_DISABLED
async def test_grocery_cashback_calc_with_cart_discount(
        _transactions,
        _grocery_cart,
        passport,
        cashback_order_calculator,
        cart_cashback_gain,
):
    _transactions(
        sum_to_pay=[
            {
                'items': [
                    {'amount': '100', 'item_id': 'grocery_id1-1'},
                    {'amount': '5', 'item_id': 'grocery_id2-1'},
                ],
                'payment_type': 'card',
            },
        ],
    )

    cashback_for_item_1 = 30

    _grocery_cart(
        order_id=ORDER_ID,
        items=[
            {
                'item_id': 'grocery_id1',
                'title': 'title1',
                'shelf_type': 'store',
                'cashback_per_unit': str(cashback_for_item_1),
                'total_price': '120',
                'price': '0',
                'vat': '20',
            },
        ],
        cart_cashback_gain=cart_cashback_gain,
    )

    passport.set_has_plus(has_plus=True)

    response = await cashback_order_calculator(order_id=ORDER_ID)

    assert response.status == 200
    response_json = response.json()
    payload = response_json['payload']

    sum_cashback = decimal.Decimal(cashback_for_item_1)
    if cart_cashback_gain is not None:
        sum_cashback += decimal.Decimal(cart_cashback_gain)

    assert response_json['cashback'] == str(sum_cashback)
    assert payload['amount'] == str(sum_cashback)
    if cart_cashback_gain is not None:
        assert payload['amount_on_cart'] == cart_cashback_gain


@YT_LOOKUP_ENABLED_DISABLED
async def test_grocery_cashback_calc_only_counts_store(
        _transactions,
        _grocery_cart,
        passport,
        cashback_order_calculator,
        yt_lookup,
):
    _transactions(
        sum_to_pay=[
            {
                'items': [
                    {'amount': '100', 'item_id': 'grocery_id1-1'},
                    {'amount': '100', 'item_id': 'grocery_id2-1'},
                    {'amount': '100', 'item_id': 'grocery_id3-1'},
                ],
                'payment_type': 'card',
            },
        ],
    )

    _grocery_cart(
        order_id=ORDER_ID,
        yt_lookup=yt_lookup,
        items=[
            {
                'item_id': 'grocery_id1',
                'title': 'title1',
                'shelf_type': 'parcel',
                'cashback_per_unit': '10',
                'total_price': '0',
                'price': '0',
                'vat': '20',
            },
            {
                'item_id': 'grocery_id2',
                'title': 'title2',
                'shelf_type': 'markdown',
                'cashback_per_unit': '20',
                'total_price': '120',
                'price': '100',
                'vat': '20',
            },
            {
                'item_id': 'grocery_id3',
                'title': 'title3',
                'shelf_type': 'store',
                'cashback_per_unit': '30',
                'total_price': '120',
                'price': '100',
                'vat': '20',
            },
        ],
    )

    passport.set_has_plus(has_plus=True)

    response = await cashback_order_calculator(order_id=ORDER_ID)

    assert response.status == 200
    response_json = response.json()

    assert response_json == {
        'cashback': '30',
        'currency': 'RUB',
        'payload': {
            'cashback_service': 'lavka',
            'cashback_type': 'transaction',
            'franchise': _bool_to_str(True),
            'items': [
                {
                    'amount': '30',
                    'item_id': 'grocery_id3',
                    'item_total_price': '120',
                    'title': 'title3',
                    'vat_rate': '20',
                },
            ],
            'order_id': 'order_id',
            'service_id': consts.CASHBACK_SERVICE_ID,
            'base_amount': '100',
            'amount': '30',
            'commission_cashback': '0',
            'currency': 'RUB',
            'city': '',
            'has_plus': _bool_to_str(True),
            'client_id': headers.YANDEX_UID,
            'ticket': consts.TICKET,
        },
    }


@GROCERY_CASHBACK_YT_LOOKUP_DISABLED
async def test_zero_invoice(
        _transactions, _grocery_cart, passport, cashback_order_calculator,
):
    _transactions(
        sum_to_pay=[
            {
                'items': [
                    {'amount': str(0), 'item_id': 'grocery_id1-1'},
                    {'amount': str(0), 'item_id': 'grocery_id1-2'},
                    {'amount': str(0), 'item_id': 'grocery_id2-1'},
                ],
                'payment_type': 'card',
            },
        ],
    )

    cashback_on_cart_percent = 10
    cashback_for_item_1 = 30
    cart_cashback_gain = 100

    _grocery_cart(
        order_id=ORDER_ID,
        cashback_on_cart_percent=str(cashback_on_cart_percent),
        items=[
            {
                'item_id': 'grocery_id1',
                'title': 'title1',
                'shelf_type': 'store',
                'cashback_per_unit': str(cashback_for_item_1),
                'total_price': '120',
                'price': '0',
                'vat': '20',
            },
        ],
        cart_cashback_gain=str(cart_cashback_gain),
    )

    passport.set_has_plus(has_plus=True)

    response = await cashback_order_calculator(order_id=ORDER_ID)

    assert response.status == 200
    response_json = response.json()
    payload = response_json['payload']

    assert response_json['cashback'] == '0'
    assert payload['items'] == []
    assert payload['amount'] == '0'
    assert payload['base_amount'] == '0'


@GROCERY_CASHBACK_YT_LOOKUP_DISABLED
async def test_cashback_on_cart(
        _transactions, _grocery_cart, passport, cashback_order_calculator,
):
    amount_1 = 20
    amount_2 = 50

    _transactions(
        sum_to_pay=[
            {
                'items': [
                    {'amount': str(amount_1), 'item_id': 'grocery_id1-1'},
                    {'amount': str(amount_1), 'item_id': 'grocery_id1-2'},
                    {'amount': str(amount_2), 'item_id': 'grocery_id2-1'},
                ],
                'payment_type': 'card',
            },
        ],
    )

    sum_amount = amount_1 * 2 + amount_2
    cashback_on_cart_percent = 10
    cashback_for_item_1 = 30
    _grocery_cart(
        order_id=ORDER_ID,
        cashback_on_cart_percent=str(cashback_on_cart_percent),
        items=[
            {
                'item_id': 'grocery_id1',
                'title': 'title1',
                'shelf_type': 'store',
                'cashback_per_unit': str(cashback_for_item_1),
                'total_price': '120',
                'price': '0',
                'vat': '20',
            },
        ],
    )

    passport.set_has_plus(has_plus=True)

    response = await cashback_order_calculator(order_id=ORDER_ID)

    assert response.status == 200
    response_json = response.json()
    payload = response_json['payload']

    cashback_for_item_1_amount = 2 * cashback_for_item_1

    cashback_on_cart = math.ceil(sum_amount * cashback_on_cart_percent / 100)
    sum_cashback = str(cashback_on_cart + cashback_for_item_1_amount)

    assert response_json['cashback'] == sum_cashback
    assert payload['items'] == [
        {
            'amount': str(cashback_for_item_1_amount),
            'item_id': 'grocery_id1',
            'item_total_price': '120',
            'title': 'title1',
            'vat_rate': '20',
        },
    ]
    assert payload['amount'] == sum_cashback
    assert payload['base_amount'] == str(sum_amount)


@pytest.mark.parametrize('franchise', [True, False])
@pytest.mark.parametrize('has_plus', [True, False])
@GROCERY_CASHBACK_YT_LOOKUP_DISABLED
async def test_israel_payload(
        _transactions,
        _grocery_cart,
        passport,
        cashback_order_calculator,
        grocery_orders,
        has_plus,
        franchise,
):
    grocery_orders.order.update(
        order_id=GROCERY_ORDER_ID, country_iso2='IL', country='Israel',
    )

    amount = 100

    _transactions(
        sum_to_pay=[
            {
                'items': [{'amount': str(amount), 'item_id': 'grocery_id1-1'}],
                'payment_type': 'card',
            },
        ],
        currency='ILS',
    )

    _grocery_cart(
        order_id=GROCERY_ORDER_ID,
        cashback_on_cart_percent='10',
        items=[
            {
                'item_id': 'grocery_id1',
                'title': 'title1',
                'shelf_type': 'store',
                'cashback_per_unit': '30',
                'total_price': '120',
                'price': '0',
                'vat': '20',
            },
        ],
        franchise=franchise,
    )

    passport.set_has_plus(has_plus=has_plus)

    response = await cashback_order_calculator(order_id=GROCERY_ORDER_ID)

    assert response.status == 200
    response_json = response.json()

    cashback = '10'

    assert response_json == {
        'cashback': cashback,
        'currency': 'ILS',
        'payload': {
            'cashback_service': 'yango_deli',
            'cashback_type': 'transaction',
            'franchise': _bool_to_str(franchise),
            'order_id': GROCERY_ORDER_ID,
            'service_id': consts.CASHBACK_SERVICE_ID,
            'base_amount': str(amount),
            'amount': cashback,
            'country': 'IL',
            'currency': 'ILS',
            'has_plus': _bool_to_str(has_plus),
            'issuer': 'marketing',
            'campaign_name': 'general_cashback_issue',
            'ticket': 'NEWSERVICE-1636',
        },
    }
