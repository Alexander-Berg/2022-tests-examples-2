# pylint: disable=import-error
from grocery_mocks.models import country
import pytest

from . import consts
from . import headers
from . import helpers

CASHBACK_SERVICE = 'lavka'
CASHBACK_TYPE = 'transaction'
SERVICE_ID = '662'
ISSUER = 'marketing'
CAMPAIGN_NAME = 'game_in_lavka'
TICKET = 'NEWSERVICE-2765'


def _bool_to_str(flag):
    if flag:
        return 'true'
    return 'false'


@pytest.fixture(name='_transactions')
def _mock_transactions(transactions):
    def _inner(cleared):
        transactions.retrieve.mock_response(
            id=consts.ORDER_ID, status='cleared', cleared=cleared,
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
        inner_kwargs = {'order_id': consts.ORDER_ID, **kwargs}
        grocery_cart.set_cashback_info_response(**inner_kwargs)

        check_request = _extract_keys(['order_id'], inner_kwargs)

        grocery_cart.check_cashback_info_request(**check_request)

    return _inner


@pytest.mark.parametrize('franchise', [True, False])
@pytest.mark.parametrize('has_plus', [True, False])
async def test_reward_calculator(
        grocery_cashback_db,
        grocery_cashback_reward_calculator,
        grocery_orders,
        passport,
        _grocery_cart,
        _transactions,
        has_plus,
        franchise,
):
    country_iso2 = country.Country.Russia.country_iso2

    grocery_orders.order.update(
        country_iso2=country_iso2, yandex_uid=headers.YANDEX_UID,
    )

    compensation_id = helpers.make_reward_compensation_id(consts.ORDER_ID)

    reward_amount = 50
    grocery_cashback_db.insert_compensation(
        compensation_id=compensation_id,
        compensation_type='tracking_game',
        data=helpers.create_other_payload(str(reward_amount)),
    )

    passport.set_has_plus(has_plus=has_plus)

    _grocery_cart(franchise=franchise)

    cleared_amount1 = 300
    cleared_amount2 = 500
    cleared_amount = cleared_amount1 + cleared_amount2

    _transactions(
        cleared=[
            {
                'payment_type': 'card',
                'items': [
                    {'amount': str(cleared_amount1), 'item_id': 'item1'},
                    {'amount': str(cleared_amount2), 'item_id': 'item2'},
                ],
            },
        ],
    )

    response_json = await grocery_cashback_reward_calculator(consts.ORDER_ID)

    assert response_json == {
        'cashback': str(reward_amount),
        'currency': consts.CURRENCY,
        'payload': {
            'cashback_service': CASHBACK_SERVICE,
            'cashback_type': CASHBACK_TYPE,
            'base_amount': str(cleared_amount),
            'has_plus': 'true' if has_plus else 'false',
            'amount': str(reward_amount),
            'service_id': SERVICE_ID,
            'franchise': _bool_to_str(franchise),
            'order_id': consts.ORDER_ID,
            'issuer': ISSUER,
            'campaign_name': CAMPAIGN_NAME,
            'ticket': TICKET,
            'country': country_iso2,
            'currency': consts.CURRENCY,
            'commission_cashback': '0',
            'client_id': headers.YANDEX_UID,
            'city': '',
        },
    }


async def test_no_invoice(
        grocery_cashback_db,
        grocery_cashback_reward_calculator,
        transactions,
        grocery_orders,
        passport,
        _grocery_cart,
):
    transactions.retrieve.status_code = 404

    compensation_id = helpers.make_reward_compensation_id(consts.ORDER_ID)

    grocery_cashback_db.insert_compensation(
        compensation_id=compensation_id,
        compensation_type='tracking_game',
        data=helpers.create_other_payload(amount='50'),
    )

    _grocery_cart()

    response_json = await grocery_cashback_reward_calculator(consts.ORDER_ID)

    assert response_json['payload']['base_amount'] == '0'
