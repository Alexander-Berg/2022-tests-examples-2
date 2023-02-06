import decimal
import math

import pytest

from . import consts
from . import models


ReceiptType = models.ReceiptType


ITEM_ID_1 = 'long-item-id-111111111111111111111111111111111111111111111111'
ITEM_ID_TIPS = 'tips'
DEPOT_TIN = '1233456789'

KIND_PAYMENT_VAT_17 = 'grocery_item_sale_vat_17'
KIND_PAYMENT_VAT_0 = 'grocery_item_sale_vat_0'
KIND_DISCOUNT_VAT_17 = 'discount_grocery_item_sale_vat_17'
KIND_DISCOUNT_VAT_0 = 'discount_grocery_item_sale_vat_0'
KIND_TIPS = 'grocery_tips_vat_17'

CART_ID = '28fe4a6e-c00d-45c1-a34e-6329c4a4e329'

QUANTITY = decimal.Decimal('3')
TIPS_QUANTITY = decimal.Decimal('1')

PRICE_WITHOUT_VAT = decimal.Decimal('100')
VAT_PERCENT = decimal.Decimal('17')
PRICE_WITH_VAT = decimal.Decimal('117')

SUMMARY_VAT = VAT_PERCENT * QUANTITY

AMOUNT_WITHOUT_VAT = PRICE_WITHOUT_VAT * QUANTITY
TRANSACTION_AMOUNT = str(AMOUNT_WITHOUT_VAT + SUMMARY_VAT)
TIPS_AMOUNT = str(PRICE_WITHOUT_VAT * TIPS_QUANTITY + VAT_PERCENT)

OPERATION_ID_TIPS = 'operation-id-tips'

PAYMENT_METHOD = {
    'payment_method': {'id': 'card-xc0f55c4b0a350c74502f4e92', 'type': 'card'},
}


def _is_discount(kind):
    return kind in (KIND_DISCOUNT_VAT_0, KIND_DISCOUNT_VAT_17)


def _make_not_discount_kind(kind):
    if kind == KIND_DISCOUNT_VAT_0:
        return KIND_PAYMENT_VAT_0
    if kind == KIND_DISCOUNT_VAT_17:
        return KIND_PAYMENT_VAT_17
    return None


def _make_item(
        item_id=ITEM_ID_1 + '_0',
        price=PRICE_WITH_VAT,
        quantity=QUANTITY,
        item_type='product',
):
    return models.receipt_item(
        item_id=item_id,
        price=str(price),
        quantity=str(quantity),
        item_type=item_type,
    )


def _make_delivery_item():
    return models.receipt_item(
        item_id='delivery',
        price=str(PRICE_WITH_VAT),
        quantity=str(1),
        item_type='delivery',
    )


def _make_sub_item_id(item_id, index=0):
    return item_id + '_' + str(index)


@pytest.fixture
def _run_stq_task(run_grocery_payments_billing_tlog_callback):
    async def _inner(**kwargs):
        obj = {
            'receipt_type': ReceiptType.Payment.value,
            'country': 'Israel',
            'external_payment_id': consts.INVOICE_ID,
            **kwargs,
        }

        await run_grocery_payments_billing_tlog_callback(**obj)

    return _inner


def _get_payment(
        price_without_vat,
        quantity,
        amount_without_vat,
        summary_vat,
        kind,
        transaction_type=ReceiptType.Payment.value,
        tlog_order_status='delivered',
        item_id=ITEM_ID_1,
):
    detailed_product = kind
    product_kind = kind
    if _is_discount(kind):
        detailed_product = 'discount'
        product_kind = _make_not_discount_kind(kind)

    return {
        'amount': amount_without_vat,
        'billing_client_id': 'user-uid',
        'currency': 'ILS',
        'invoice_date': consts.NOW,
        'payload': {
            'agglomeration': 'TELAVIV',
            'detailed_product': detailed_product,
            'ignore_in_balance': True,
            'invoice_id': consts.INVOICE_ID,
            'is_payable': False,
            'item_id': item_id,
            'order_details': {
                'TIN': DEPOT_TIN,
                'courier_id': consts.EATS_COURIER_ID,
                'courier_type': consts.TRANSPORT_TYPE,
                'local_place_confirmed_dttm': consts.FINISH_STARTED,
                'order_status': tlog_order_status,
                'place_city': 'order_city',
                'place_id': consts.DEPOT_ID,
            },
            'order_id': consts.ORDER_ID,
            'price': price_without_vat,
            'product': product_kind,
            'quantity': quantity,
            'service_id': 663,
            'tariff_class': 'lavka',
            'transaction_type': transaction_type,
            'vat': summary_vat,
        },
        'payment_kind': kind,
    }


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'order_status, tlog_order_status',
    [('closed', 'delivered'), ('canceled', 'rejected')],
)
@pytest.mark.parametrize(
    'item, sub_items',
    [
        (
            _make_item(),
            [
                models.GroceryCartSubItem(
                    item_id=_make_sub_item_id(ITEM_ID_1),
                    price=str(PRICE_WITH_VAT),
                    full_price=str(PRICE_WITH_VAT),
                    quantity=str(QUANTITY),
                ),
            ],
        ),
        (_make_delivery_item(), []),
    ],
)
@pytest.mark.config(GROCERY_ORDERS_ISRAEL_TLOG_ENABLED=True)
async def test_payment_item_no_discount(
        grocery_orders,
        grocery_cart,
        grocery_depots,
        billing_orders,
        _run_stq_task,
        order_status,
        tlog_order_status,
        item,
        sub_items,
):
    grocery_orders.order.update(status=order_status)
    grocery_cart.set_cart_data(cart_id=CART_ID)

    item_1 = models.GroceryCartItemV2(
        item_id=item['item_id'], vat=str(VAT_PERCENT), sub_items=sub_items,
    )

    grocery_cart.set_items_v2([item_1])

    country = models.Country.Israel
    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID,
        country_iso3=country.country_iso3,
        currency=country.currency,
        tin=DEPOT_TIN,
    )

    payment = _get_payment(
        price_without_vat=str(PRICE_WITHOUT_VAT),
        quantity=str(item['quantity']),
        amount_without_vat=str(
            PRICE_WITHOUT_VAT * decimal.Decimal(item['quantity']),
        ),
        summary_vat=str(VAT_PERCENT * decimal.Decimal(item['quantity'])),
        kind=KIND_PAYMENT_VAT_17,
        tlog_order_status=tlog_order_status,
        item_id=item['item_id'],
    )

    billing_orders.check_request_v1(
        order_id=consts.ORDER_ID,
        item_id=item['item_id'],
        operation_id=consts.OPERATION_ID,
        payments=[payment],
    )

    await _run_stq_task(items=[item])

    assert billing_orders.process_async_times_called() == 1


@pytest.mark.now(consts.NOW)
@pytest.mark.config(GROCERY_ORDERS_ISRAEL_TLOG_ENABLED=True)
async def test_payment_with_tips(
        grocery_orders,
        grocery_cart,
        grocery_depots,
        billing_orders,
        _run_stq_task,
):
    grocery_cart.set_cart_data(cart_id=CART_ID)

    item = _make_item(item_id='tips', quantity=TIPS_QUANTITY, item_type='tips')

    country = models.Country.Israel
    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID,
        country_iso3=country.country_iso3,
        currency=country.currency,
        tin=DEPOT_TIN,
    )

    tips_payment = _get_payment(
        price_without_vat=str(PRICE_WITHOUT_VAT),
        quantity=str(TIPS_QUANTITY),
        amount_without_vat=str(PRICE_WITHOUT_VAT * TIPS_QUANTITY),
        summary_vat=str(VAT_PERCENT * TIPS_QUANTITY),
        kind=KIND_TIPS,
        tlog_order_status='delivered',
        item_id=item['item_id'],
    )
    billing_orders.check_request_v1(
        order_id=consts.ORDER_ID,
        item_id=item['item_id'],
        operation_id=OPERATION_ID_TIPS,
        payments=[tips_payment],
    )

    await _run_stq_task(operation_id=OPERATION_ID_TIPS, items=[item])

    assert billing_orders.process_async_times_called() == 1


@pytest.mark.now(consts.NOW)
@pytest.mark.parametrize(
    'order_status', ['reserved', 'assembling', 'delivering'],
)
@pytest.mark.config(GROCERY_ORDERS_ISRAEL_TLOG_ENABLED=True)
async def test_ignore_not_finished_status(
        grocery_orders,
        grocery_cart,
        grocery_depots,
        order_status,
        billing_orders,
        _run_stq_task,
):
    grocery_orders.order.update(status=order_status)
    grocery_cart.set_cart_data(cart_id=CART_ID)

    country = models.Country.Israel
    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID,
        country_iso3=country.country_iso3,
        currency=country.currency,
        tin=DEPOT_TIN,
    )

    await _run_stq_task()

    assert billing_orders.process_async_times_called() == 0


@pytest.mark.now(consts.NOW)
@pytest.mark.config(GROCERY_ORDERS_ISRAEL_TLOG_ENABLED=True)
async def test_payment_item_with_discount(
        grocery_orders,
        grocery_cart,
        grocery_depots,
        billing_orders,
        _run_stq_task,
):
    grocery_cart.set_cart_data(cart_id=CART_ID)

    full_price_with_vat = decimal.Decimal(117 * 2)
    full_price_without_vat = decimal.Decimal(200)
    price_with_vat = decimal.Decimal(117)
    price_without_vat = decimal.Decimal(100)

    amount_without_vat = full_price_without_vat * QUANTITY
    amount_with_vat = full_price_with_vat * QUANTITY
    summary_vat = amount_with_vat - amount_without_vat

    item_1 = models.GroceryCartItemV2(
        item_id=ITEM_ID_1,
        vat=str(VAT_PERCENT),
        sub_items=[
            models.GroceryCartSubItem(
                item_id=_make_sub_item_id(ITEM_ID_1),
                price=str(price_with_vat),
                full_price=str(full_price_with_vat),
                quantity=str(QUANTITY),
            ),
        ],
    )

    grocery_cart.set_items_v2([item_1])

    country = models.Country.Israel
    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID,
        country_iso3=country.country_iso3,
        currency=country.currency,
        tin=DEPOT_TIN,
    )

    payment_for_item = _get_payment(
        price_without_vat=str(full_price_without_vat),
        quantity=str(QUANTITY),
        amount_without_vat=str(amount_without_vat),
        summary_vat=str(summary_vat),
        kind=KIND_PAYMENT_VAT_17,
    )

    discount_for_item_with_vat = full_price_with_vat - price_with_vat
    discount_for_item_without_vat = full_price_without_vat - price_without_vat
    amount_discount_without_vat = discount_for_item_without_vat * QUANTITY
    summary_vat_for_discount = (
        discount_for_item_with_vat - discount_for_item_without_vat
    ) * QUANTITY

    payment_for_discount = _get_payment(
        price_without_vat=str(discount_for_item_without_vat),
        quantity=str(QUANTITY),
        amount_without_vat=str(-amount_discount_without_vat),
        summary_vat=str(summary_vat_for_discount),
        kind=KIND_DISCOUNT_VAT_17,
        transaction_type=ReceiptType.Refund.value,  # because discount
    )

    billing_orders.check_request_v1(
        order_id=consts.ORDER_ID,
        item_id=ITEM_ID_1,
        operation_id=consts.OPERATION_ID,
        payments=[payment_for_item, payment_for_discount],
    )

    await _run_stq_task(items=[_make_item(price=price_with_vat)])

    assert billing_orders.process_async_times_called() == 1


@pytest.mark.now(consts.NOW)
@pytest.mark.config(GROCERY_ORDERS_ISRAEL_TLOG_ENABLED=True)
async def test_refund_item(
        grocery_orders,
        grocery_cart,
        grocery_depots,
        billing_orders,
        _run_stq_task,
):
    grocery_cart.set_cart_data(cart_id=CART_ID)

    item_1 = models.GroceryCartItemV2(
        item_id=ITEM_ID_1,
        vat=str(VAT_PERCENT),
        sub_items=[
            models.GroceryCartSubItem(
                item_id=_make_sub_item_id(ITEM_ID_1),
                price=str(PRICE_WITH_VAT),
                full_price=str(PRICE_WITH_VAT),
                quantity=str(QUANTITY),
            ),
        ],
    )

    grocery_cart.set_items_v2([item_1])

    country = models.Country.Israel
    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID,
        country_iso3=country.country_iso3,
        currency=country.currency,
        tin=DEPOT_TIN,
    )

    payment = _get_payment(
        price_without_vat=str(PRICE_WITHOUT_VAT),
        quantity=str(QUANTITY),
        amount_without_vat=str(-AMOUNT_WITHOUT_VAT),
        summary_vat=str(SUMMARY_VAT),
        kind=KIND_PAYMENT_VAT_17,
        transaction_type=ReceiptType.Refund.value,
    )

    billing_orders.check_request_v1(
        order_id=consts.ORDER_ID,
        item_id=ITEM_ID_1,
        operation_id=consts.OPERATION_ID,
        payments=[payment],
    )

    await _run_stq_task(
        receipt_type=ReceiptType.Refund.value, items=[_make_item()],
    )

    assert billing_orders.process_async_times_called() == 1


@pytest.mark.now(consts.NOW)
@pytest.mark.config(GROCERY_ORDERS_ISRAEL_TLOG_ENABLED=True)
async def test_refund_item_with_discount(
        grocery_orders,
        grocery_cart,
        grocery_depots,
        billing_orders,
        _run_stq_task,
):
    grocery_cart.set_cart_data(cart_id=CART_ID)

    full_price_with_vat = decimal.Decimal(117 * 2)
    full_price_without_vat = decimal.Decimal(200)
    price_with_vat = decimal.Decimal(117)
    price_without_vat = decimal.Decimal(100)

    amount_without_vat = full_price_without_vat * QUANTITY
    amount_with_vat = full_price_with_vat * QUANTITY
    summary_vat = amount_with_vat - amount_without_vat

    item_1 = models.GroceryCartItemV2(
        item_id=ITEM_ID_1,
        vat=str(VAT_PERCENT),
        sub_items=[
            models.GroceryCartSubItem(
                item_id=_make_sub_item_id(ITEM_ID_1),
                price=str(price_with_vat),
                full_price=str(full_price_with_vat),
                quantity=str(QUANTITY),
            ),
        ],
    )

    grocery_cart.set_items_v2([item_1])

    country = models.Country.Israel
    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID,
        country_iso3=country.country_iso3,
        currency=country.currency,
        tin=DEPOT_TIN,
    )

    payment_for_item = _get_payment(
        price_without_vat=str(full_price_without_vat),
        quantity=str(QUANTITY),
        amount_without_vat=str(-amount_without_vat),
        summary_vat=str(summary_vat),
        kind=KIND_PAYMENT_VAT_17,
        transaction_type=ReceiptType.Refund.value,
    )

    discount_for_item_with_vat = full_price_with_vat - price_with_vat
    discount_for_item_without_vat = full_price_without_vat - price_without_vat
    amount_discount_without_vat = discount_for_item_without_vat * QUANTITY
    summary_vat_for_discount = (
        discount_for_item_with_vat - discount_for_item_without_vat
    ) * QUANTITY

    payment_for_discount = _get_payment(
        price_without_vat=str(discount_for_item_without_vat),
        quantity=str(QUANTITY),
        amount_without_vat=str(amount_discount_without_vat),
        summary_vat=str(summary_vat_for_discount),
        kind=KIND_DISCOUNT_VAT_17,
        # because discount + refund
        transaction_type=ReceiptType.Payment.value,
    )

    billing_orders.check_request_v1(
        order_id=consts.ORDER_ID,
        item_id=ITEM_ID_1,
        operation_id=consts.OPERATION_ID,
        payments=[payment_for_item, payment_for_discount],
    )

    await _run_stq_task(
        receipt_type=ReceiptType.Refund.value,
        items=[_make_item(price=price_with_vat)],
    )

    assert billing_orders.process_async_times_called() == 1


@pytest.mark.now(consts.NOW)
@pytest.mark.config(GROCERY_ORDERS_ISRAEL_TLOG_ENABLED=True)
async def test_zero_vat(
        grocery_orders,
        grocery_cart,
        grocery_depots,
        billing_orders,
        _run_stq_task,
):
    grocery_cart.set_cart_data(cart_id=CART_ID)

    full_price_with_vat = decimal.Decimal(100 * 2)
    full_price_without_vat = decimal.Decimal(200)
    price_with_vat = decimal.Decimal(100)
    price_without_vat = decimal.Decimal(100)

    amount_without_vat = full_price_without_vat * QUANTITY
    amount_with_vat = full_price_with_vat * QUANTITY
    summary_vat = amount_with_vat - amount_without_vat

    assert summary_vat == decimal.Decimal(0)
    assert amount_with_vat == amount_without_vat

    item_1 = models.GroceryCartItemV2(
        item_id=ITEM_ID_1,
        vat='0',
        sub_items=[
            models.GroceryCartSubItem(
                item_id=_make_sub_item_id(ITEM_ID_1),
                price=str(price_with_vat),
                full_price=str(full_price_with_vat),
                quantity=str(QUANTITY),
            ),
        ],
    )

    grocery_cart.set_items_v2([item_1])

    country = models.Country.Israel
    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID,
        country_iso3=country.country_iso3,
        currency=country.currency,
        tin=DEPOT_TIN,
    )

    payment_for_item = _get_payment(
        price_without_vat=str(full_price_without_vat),
        quantity=str(QUANTITY),
        amount_without_vat=str(amount_without_vat),
        summary_vat=str(summary_vat),
        kind=KIND_PAYMENT_VAT_0,
    )

    discount_for_item_with_vat = full_price_with_vat - price_with_vat
    discount_for_item_without_vat = full_price_without_vat - price_without_vat
    amount_discount_without_vat = discount_for_item_without_vat * QUANTITY
    summary_vat_for_discount = (
        discount_for_item_with_vat - discount_for_item_without_vat
    ) * QUANTITY

    payment_for_discount = _get_payment(
        price_without_vat=str(discount_for_item_without_vat),
        quantity=str(QUANTITY),
        amount_without_vat=str(-amount_discount_without_vat),
        summary_vat=str(summary_vat_for_discount),
        kind=KIND_DISCOUNT_VAT_0,
        transaction_type=ReceiptType.Refund.value,  # because discount
    )

    billing_orders.check_request_v1(
        order_id=consts.ORDER_ID,
        item_id=ITEM_ID_1,
        operation_id=consts.OPERATION_ID,
        payments=[payment_for_item, payment_for_discount],
    )

    await _run_stq_task(
        receipt_type=ReceiptType.Payment.value,
        items=[_make_item(price=price_with_vat)],
    )

    assert billing_orders.process_async_times_called() == 1


@pytest.mark.now(consts.NOW)
@pytest.mark.config(GROCERY_ORDERS_ISRAEL_TLOG_ENABLED=True)
async def test_roundings(
        grocery_orders,
        pgsql,
        grocery_cart,
        grocery_depots,
        billing_orders,
        _run_stq_task,
):
    grocery_cart.set_cart_data(cart_id=CART_ID)

    quantity = decimal.Decimal('4')
    price_with_vat = decimal.Decimal('3.14')
    # 3.14 / 1.17 = 2,6837... = 2.68
    price_without_vat = decimal.Decimal('2.68')

    amount = price_with_vat * quantity
    assert amount == decimal.Decimal('12.56')
    # 12.56 / 1.17 = 10,73504... = 10.74
    amount_without_vat = decimal.Decimal('10.74')

    summary_vat = amount - amount_without_vat
    assert str(summary_vat) == '1.82'

    item_1 = models.GroceryCartItemV2(
        item_id=ITEM_ID_1,
        vat='17',
        sub_items=[
            models.GroceryCartSubItem(
                item_id=_make_sub_item_id(ITEM_ID_1),
                price=str(price_with_vat),
                full_price=str(price_with_vat),
                quantity=str(quantity),
            ),
        ],
    )

    grocery_cart.set_items_v2([item_1])

    country = models.Country.Israel
    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID,
        country_iso3=country.country_iso3,
        currency=country.currency,
        tin=DEPOT_TIN,
    )

    payment_for_item = _get_payment(
        price_without_vat=str(price_without_vat),
        quantity=str(quantity),
        amount_without_vat=str(amount_without_vat),
        summary_vat=str(summary_vat),
        kind=KIND_PAYMENT_VAT_17,
    )

    billing_orders.check_request_v1(
        order_id=consts.ORDER_ID,
        item_id=ITEM_ID_1,
        operation_id=consts.OPERATION_ID,
        payments=[payment_for_item],
    )

    await _run_stq_task(
        receipt_type=ReceiptType.Payment.value,
        items=[_make_item(price=price_with_vat, quantity=quantity)],
    )

    assert billing_orders.process_async_times_called() == 1


@pytest.mark.now(consts.NOW)
@pytest.mark.config(GROCERY_ORDERS_ISRAEL_TLOG_ENABLED=True)
async def test_roundings_with_discount(
        grocery_orders,
        grocery_cart,
        grocery_depots,
        billing_orders,
        _run_stq_task,
):
    grocery_cart.set_cart_data(cart_id=CART_ID)

    quantity = decimal.Decimal('4')

    full_price_with_vat = decimal.Decimal('6.28')
    # 6.28 / 1.17 = 5,3675... = 5.37
    full_price_without_vat = decimal.Decimal('5.37')

    price_with_vat = decimal.Decimal('3.14')
    # 3.14 / 1.17 = 2,6837... = 2.68
    price_without_vat = decimal.Decimal('2.68')

    amount_with_vat = full_price_with_vat * quantity
    assert amount_with_vat == decimal.Decimal('25.12')
    # 25.12 / 1.17 = 21,470... = 21.47
    amount_without_vat = decimal.Decimal('21.47')

    summary_vat_for_full = amount_with_vat - amount_without_vat
    assert str(summary_vat_for_full) == '3.65'

    # 3.14 * 4 = 12.56
    # 3.14 * 4 / 1.17 = 10,73504... = 10.74
    # vat: 12.56 - 10.74 = 1.82
    summary_vat_in_receipt = price_with_vat * quantity - decimal.Decimal(
        '10.74',
    )
    assert str(summary_vat_in_receipt) == '1.82'

    item_1 = models.GroceryCartItemV2(
        item_id=ITEM_ID_1,
        vat='17',
        sub_items=[
            models.GroceryCartSubItem(
                item_id=_make_sub_item_id(ITEM_ID_1),
                price=str(price_with_vat),
                full_price=str(full_price_with_vat),
                quantity=str(quantity),
            ),
        ],
    )

    grocery_cart.set_items_v2([item_1])

    country = models.Country.Israel
    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID,
        country_iso3=country.country_iso3,
        currency=country.currency,
        tin=DEPOT_TIN,
    )

    payment_for_item = _get_payment(
        price_without_vat=str(full_price_without_vat),
        quantity=str(quantity),
        amount_without_vat=str(amount_without_vat),
        summary_vat=str(summary_vat_for_full),
        kind=KIND_PAYMENT_VAT_17,
    )

    discount_price_with_vat = full_price_with_vat - price_with_vat
    # Discount is 50%, so price_with_vat == discount_price_with_vat
    assert discount_price_with_vat == price_with_vat
    discount_price_without_vat = price_without_vat

    discount_amount_with_vat = discount_price_with_vat * quantity
    assert str(discount_amount_with_vat) == '12.56'
    # 12.56 / 1.17 = 10,73504... = 10.74
    discount_amount_without_vat = decimal.Decimal('10.74')
    discount_summary_vat = summary_vat_for_full - summary_vat_in_receipt

    payment_for_discount = _get_payment(
        price_without_vat=str(discount_price_without_vat),
        quantity=str(quantity),
        amount_without_vat=str(-discount_amount_without_vat),
        summary_vat=str(discount_summary_vat),
        kind=KIND_DISCOUNT_VAT_17,
        transaction_type=ReceiptType.Refund.value,  # because discount
    )

    total_in_receipt = price_with_vat * quantity
    # Проверяем, что разница ндс у скидки и товара - это то, что мы записали
    # в чек.
    assert (
        summary_vat_for_full - discount_summary_vat == summary_vat_in_receipt
    )
    # Проверяем тоже самое, только для цен товаров.
    assert amount_with_vat - discount_amount_with_vat == total_in_receipt

    billing_orders.check_request_v1(
        order_id=consts.ORDER_ID,
        item_id=ITEM_ID_1,
        operation_id=consts.OPERATION_ID,
        payments=[payment_for_item, payment_for_discount],
    )

    await _run_stq_task(
        receipt_type=ReceiptType.Payment.value,
        items=[_make_item(price=price_with_vat, quantity=quantity)],
    )

    assert billing_orders.process_async_times_called() == 1


ORDERS_PER_REQUEST = 3
ORDERS_COUNT = 17


@pytest.mark.now(consts.NOW)
@pytest.mark.config(GROCERY_ORDERS_ISRAEL_TLOG_ENABLED=True)
@pytest.mark.config(
    GROCERY_ORDERS_ISRAEL_BILLING_ORDERS_PARAMS={
        '__default__': {
            'agglomeration': 'TELAVIV',
            'is_payable': False,
            'ignore_in_balance': True,
            'service_id': 663,
            'tariff_class': 'lavka',
        },
    },
)
@pytest.mark.config(
    GROCERY_PAYMENTS_BILLING_BILLING_ORDERS_BATCH_SIZE=ORDERS_PER_REQUEST,
)
async def test_batched_request(
        grocery_orders,
        grocery_cart,
        grocery_depots,
        billing_orders,
        _run_stq_task,
):
    grocery_cart.set_cart_data(cart_id=CART_ID)

    items = []
    request_items = []
    price = '10'
    amount = decimal.Decimal(0)
    for i in range(0, ORDERS_COUNT):
        item_id = f'item-id-{i}'
        items.append(
            models.GroceryCartItemV2(
                item_id=item_id,
                vat='17',
                sub_items=[
                    models.GroceryCartSubItem(
                        item_id=_make_sub_item_id(item_id),
                        price='10',
                        full_price='10',
                        quantity='1',
                    ),
                ],
            ),
        )

        request_items.append(
            models.receipt_item(
                item_id=item_id + '_0', price=price, quantity='1',
            ),
        )

        amount += decimal.Decimal(price)

    grocery_cart.set_items_v2(items)

    country = models.Country.Israel
    grocery_depots.add_depot(
        legacy_depot_id=consts.DEPOT_ID,
        country_iso3=country.country_iso3,
        currency=country.currency,
        tin=DEPOT_TIN,
    )

    await _run_stq_task(items=request_items)

    assert billing_orders.process_async_times_called() != 1
    assert billing_orders.process_async_times_called() == math.ceil(
        len(items) / ORDERS_PER_REQUEST,
    )
