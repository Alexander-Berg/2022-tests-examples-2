import decimal

import pytest

from . import consts
from . import models
from .plugins import configs


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize('receipt_type', models.ReceiptType)
@pytest.mark.parametrize('payment_type', ['badge', 'corp', 'card'])
async def test_products(
        grocery_orders,
        grocery_cart,
        run_grocery_payments_billing_tlog_callback,
        check_eats_payments_billing_proxy_callback,
        receipt_type,
        payment_type,
        grocery_depots,
):
    country = models.Country.Russia
    order_id = consts.ORDER_ID
    items = [
        models.receipt_item(item_id='item_id_1', price='150', quantity='2'),
    ]

    grocery_depots.add_depot(legacy_depot_id=consts.DEPOT_ID)

    await run_grocery_payments_billing_tlog_callback(
        order_id=order_id,
        payment_type=payment_type,
        receipt_type=receipt_type.value,
        country=country.name,
        items=items,
    )

    check_eats_payments_billing_proxy_callback(
        order_id=order_id,
        payment_type=payment_type,
        transaction_type=receipt_type.value,
        currency=country.currency,
        event_at=consts.NOW,
        items=_convert_items(
            items=items,
            balance_client_id=configs.get_balance_client_id(country),
            item_type='product',
        ),
    )


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize('receipt_type', models.ReceiptType)
@pytest.mark.parametrize(
    'receipt_data_type',
    [models.ReceiptDataType.Delivery, models.ReceiptDataType.Tips],
)
async def test_delivery_and_tips(
        grocery_orders,
        grocery_cart,
        run_grocery_payments_billing_tlog_callback,
        check_eats_payments_billing_proxy_callback,
        receipt_type,
        receipt_data_type,
        grocery_depots,
):
    country = models.Country.Russia
    order_id = consts.ORDER_ID
    payment_type = 'card'
    items = [
        models.receipt_item(
            item_id='item_id_1',
            price='150',
            quantity='2',
            item_type=receipt_data_type.value,
        ),
    ]

    grocery_depots.add_depot(legacy_depot_id=consts.DEPOT_ID)

    await run_grocery_payments_billing_tlog_callback(
        order_id=order_id,
        payment_type=payment_type,
        receipt_type=receipt_type.value,
        country=country.name,
        items=items,
        receipt_data_type=receipt_data_type.value,
    )

    check_eats_payments_billing_proxy_callback(
        order_id=order_id,
        payment_type=payment_type,
        transaction_type=receipt_type.value,
        currency=country.currency,
        event_at=consts.NOW,
        items=_convert_items(
            items=items,
            balance_client_id=consts.BALANCE_CLIENT_ID,
            item_type=receipt_data_type.value,
        ),
    )


@pytest.mark.now(consts.NOW)
@pytest.mark.config(EDA_CORE_DONATION={'client_id': consts.BALANCE_CLIENT_ID})
@pytest.mark.parametrize('receipt_type', models.ReceiptType)
async def test_helping_hand(
        grocery_orders,
        grocery_cart,
        run_grocery_payments_billing_tlog_callback,
        check_eats_payments_billing_proxy_callback,
        receipt_type,
        grocery_depots,
):
    country = models.Country.Russia
    order_id = consts.ORDER_ID
    payment_type = 'card'
    receipt_data_type = models.ReceiptDataType.HelpingHand
    items = [
        models.receipt_item(
            item_id='item_id_1',
            price='150',
            quantity='2',
            item_type=receipt_data_type.value,
        ),
    ]

    grocery_depots.add_depot(legacy_depot_id=consts.DEPOT_ID)

    await run_grocery_payments_billing_tlog_callback(
        order_id=order_id,
        payment_type=payment_type,
        receipt_type=receipt_type.value,
        country=country.name,
        items=items,
        receipt_data_type=receipt_data_type.value,
    )

    check_eats_payments_billing_proxy_callback(
        order_id=order_id,
        payment_type=payment_type,
        transaction_type=receipt_type.value,
        currency=country.currency,
        event_at=consts.NOW,
        items=_convert_items(
            items=items,
            balance_client_id=consts.BALANCE_CLIENT_ID,
            item_type='donation',
        ),
    )


def _convert_items(*, items, balance_client_id, item_type):
    out_items = []
    for item in items:
        price = decimal.Decimal(item['price'])
        quantity = decimal.Decimal(item['quantity'])

        out_items.append(
            {
                'balance_client_id': balance_client_id,
                'item_id': item['item_id'],
                'item_type': item_type,
                'place_id': consts.DEPOT_ID,
                'amount': str(price * quantity),
            },
        )
    return out_items
