import pytest

from . import consts
from . import headers
from . import helpers

CASHBACK_SERVICE = 'lavka'
CASHBACK_TYPE = 'nontransaction'
SERVICE_ID = '662'
ISSUER = 'support'
CAMPAIGN_NAME = 'support_compensation'
TICKET = 'NEWSERVICE-1849'


@pytest.mark.parametrize('has_plus', [True, False])
async def test_compensation_calculator(
        grocery_cashback_create_compensation,
        grocery_cashback_compensation_calculator,
        grocery_payments,
        grocery_orders,
        passport,
        has_plus,
):
    items = helpers.make_transaction_items(consts.PRODUCTS)
    grocery_payments.add_transaction(status='clear_success', items=items)

    response = await grocery_cashback_create_compensation(
        consts.COMPENSATION_ID, consts.PAYLOAD,
    )

    assert response.status_code == 200

    moked_order = grocery_orders.add_order()
    moked_order_dict = moked_order.as_dict()
    moked_order_dict['order_id'] = consts.ORDER_ID
    moked_order.update(yandex_uid=headers.YANDEX_UID)

    passport.set_has_plus(has_plus=has_plus)

    response = await grocery_cashback_compensation_calculator(
        consts.COMPENSATION_ID,
    )

    assert response.status_code == 200

    assert response.json() == {
        'cashback': consts.CASHBACK_AMOUNT,
        'currency': consts.CURRENCY,
        'payload': {
            'cashback_service': CASHBACK_SERVICE,
            'cashback_type': CASHBACK_TYPE,
            'has_plus': 'true' if has_plus else 'false',
            'service_id': SERVICE_ID,
            'issuer': ISSUER,
            'campaign_name': CAMPAIGN_NAME,
            'ticket': TICKET,
            'amount': consts.CASHBACK_AMOUNT,
            'currency': consts.CURRENCY,
            'order_id': f'compensation:{consts.COMPENSATION_ID}',
            'grocery_order_id': consts.ORDER_ID,
            'compensation_id': consts.COMPENSATION_ID,
            'commission_cashback': '0',
            'client_id': headers.YANDEX_UID,
            'city': '',
        },
    }


@pytest.mark.parametrize(
    'payload, times_called, products',
    [(consts.PAYLOAD, 2, consts.PRODUCTS), (helpers.OTHER_PAYLOAD, 0, None)],
)
async def test_payments_called(
        grocery_cashback_create_compensation,
        grocery_cashback_compensation_calculator,
        grocery_payments,
        grocery_orders,
        passport,
        payload,
        times_called,
        products,
):
    if products:
        items = helpers.make_transaction_items(consts.PRODUCTS)
        grocery_payments.add_transaction(status='clear_success', items=items)

    response = await grocery_cashback_create_compensation(
        consts.COMPENSATION_ID, payload,
    )

    assert response.status_code == 200

    moked_order = grocery_orders.add_order()
    moked_order_dict = moked_order.as_dict()
    moked_order_dict['order_id'] = consts.ORDER_ID
    moked_order.update(yandex_uid=headers.YANDEX_UID)

    passport.set_has_plus(has_plus=True)

    response = await grocery_cashback_compensation_calculator(
        consts.COMPENSATION_ID,
    )

    assert response.status_code == 200

    assert grocery_payments.times_retrieve_called() == times_called
