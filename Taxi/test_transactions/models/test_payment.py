import decimal

from transactions.internal import basket
from transactions.models import payment


def test_payment_items_get_basket():
    payment_items_with_merchant_id = _build_payment_items(
        item_id='some_item_id', merchant_id='some_merchant_id',
    )

    items_basket = payment_items_with_merchant_id.get_basket()

    key = basket.Key('some_item_id', 'some_merchant_id')
    assert items_basket.get(key).merchant.id == 'some_merchant_id'


def test_item_serde():
    item = _build_payment_item(
        item_id='some_item_id',
        amount=decimal.Decimal(100),
        merchant_id='some_merchant_id',
    )

    actual_serialized = item.to_mongo()
    assert actual_serialized == {
        'item_id': 'some_item_id',
        'amount': '100',
        'merchant': {'id': 'some_merchant_id'},
    }

    actual_deserialized = payment.Item.from_mongo(actual_serialized)
    assert actual_deserialized == item


def _build_payment_items(item_id, merchant_id):
    payment_items_with_merchant_id = payment.PaymentItems(
        payment_type=None,
        items=[_build_payment_item(item_id=item_id, merchant_id=merchant_id)],
    )
    return payment_items_with_merchant_id


def _build_payment_item(
        item_id: str,
        amount: decimal.Decimal = decimal.Decimal(100),
        merchant_id: str = None,
) -> payment.Item:
    merchant = None
    if merchant_id is not None:
        merchant = basket.Merchant(id=merchant_id, order_id=None)
    return payment.Item(
        item_id=item_id,
        merchant=merchant,
        amount=amount,
        product_id=None,
        fiscal_receipt_info=None,
        region_id=None,
        commission_category=None,
        price=None,
        quantity=None,
    )
