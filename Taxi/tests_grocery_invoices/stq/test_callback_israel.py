# pylint: disable=import-only-modules
from decimal import Decimal

import pytest

from tests_grocery_invoices import consts
from tests_grocery_invoices import helpers
from tests_grocery_invoices import models
from tests_grocery_invoices import pytest_marks
from tests_grocery_invoices.items_context import ItemsContext
from tests_grocery_invoices.items_context import SubItem
from tests_grocery_invoices.plugins import mock_easy_count

COUNTRY = models.Country.Israel

# pylint: disable=invalid-name
pytestmark = [pytest_marks.TRANSLATIONS_MARK]

RECEIPT_PRODUCT_ITEMS = helpers.make_product_receipt(COUNTRY)
RECEIPT_DELIVERY_ITEMS = helpers.make_delivery_receipt(COUNTRY)
RECEIPT_ITEMS = [*RECEIPT_PRODUCT_ITEMS, *RECEIPT_DELIVERY_ITEMS]
CART_ITEMS_RUS = helpers.make_cart_items(COUNTRY)

RECEIPT_TOTAL = '127.04'

CUSTOMER_NAME = f'{consts.PASSPORT_CUSTOMER_NAME} {consts.USER_PHONE}'


def add_items_title(items):
    for item in items:
        item.title = item.item_id + '_title'

    return items


CART_ITEMS_ISR = add_items_title(
    helpers.make_cart_items(models.Country.Israel),
)


@pytest.fixture
def _run_stq(run_grocery_invoices_callback):
    async def _do(items=None, **kwargs):
        items = items or RECEIPT_ITEMS

        await run_grocery_invoices_callback(
            items=models.items_to_json(items), **kwargs, country=COUNTRY.name,
        )

    return _do


async def test_basic_request(
        grocery_orders,
        grocery_cart,
        easy_count_v2,
        default_isr_receipt,
        _run_stq,
):
    receipt_data_type = consts.ORDER_RECEIPT_DATA_TYPE

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)

    idempotency_token = consts.EXTERNAL_PAYMENT_ID + receipt_data_type

    easy_count_v2.create.check(
        headers={'User-Agent': mock_easy_count.EASY_COUNT_USER_AGENT},
        customer_name=CUSTOMER_NAME,
        developer_email=mock_easy_count.DEVELOPER_EMAIL,
        transaction_id=idempotency_token,
        ua_uuid=consts.GROCERY_USER_UUID,
        parent=default_isr_receipt.payload['receipt_uuid'],
        show_items_including_vat=True,
        dont_send_email=True,
        api_key=mock_easy_count.EASY_COUNT_TOKEN,
    )

    await _run_stq()

    assert easy_count_v2.create.times_called == 1


@pytest.mark.parametrize(
    'payment_type, easy_count_data',
    [
        (
            models.PaymentType.card.value,
            {
                'cc_deal_type': 1,  # just 1 for cards
                'cc_number': consts.DEFAULT_LAST_4_DIGITS,
                'cc_type': 2,  # visa
                'payment_type': 3,  # just 3 for cards
            },
        ),
        (
            models.PaymentType.applepay.value,
            {'other_payment_type_name': 'Apple Pay', 'payment_type': 9},
        ),
        (
            models.PaymentType.cibus.value,
            {'other_payment_type_name': 'Cibus', 'payment_type': 9},
        ),
    ],
)
async def test_payment_types(
        grocery_orders,
        grocery_cart,
        easy_count_v2,
        _run_stq,
        payment_type,
        easy_count_data,
):
    payment_method = {'type': payment_type, 'id': 'payment-id'}

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)

    payment = {**easy_count_data, 'payment_sum': RECEIPT_TOTAL}

    easy_count_v2.create.check(payment=[payment], price_total=RECEIPT_TOTAL)

    await _run_stq(payment_method=payment_method)

    assert easy_count_v2.create.times_called == 1


@pytest.mark.parametrize(
    'receipt_type, config_value, easy_count_invoice_type',
    [
        (
            models.ReceiptType.payment.value,
            None,
            mock_easy_count.EASY_COUNT_PAYMENT,
        ),
        (
            models.ReceiptType.refund.value,
            None,
            mock_easy_count.EASY_COUNT_REFUND,
        ),
        (models.ReceiptType.payment.value, 200, 200),
        (models.ReceiptType.payment.value, 210, 210),
    ],
)
async def test_invoice_types(
        grocery_invoices_configs,
        grocery_orders,
        grocery_cart,
        easy_count_v2,
        _run_stq,
        receipt_type,
        config_value,
        easy_count_invoice_type,
):
    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)

    grocery_invoices_configs.easy_count_doc_request_type(config_value)

    easy_count_v2.create.check(type=easy_count_invoice_type)

    await _run_stq(receipt_type=receipt_type)

    assert easy_count_v2.create.times_called == 1


async def test_items(
        grocery_orders,
        grocery_cart,
        easy_count_v2,
        run_grocery_invoices_callback,
):
    grocery_cart.set_cart_data(cart_id=consts.CART_ID)

    first_item_id = 'item-id-0'
    first_item_0 = SubItem(price='10', quantity='2', full_price='20')
    first_item_1 = SubItem(price='20', quantity='1', full_price='20')

    second_item_id = 'item-id-1'
    second_item_0 = SubItem(price='15.1', quantity='2', full_price='20.99')
    second_item_1 = SubItem(price='17.29', quantity='1', full_price='20.17')

    items_context = ItemsContext(country=COUNTRY)
    cart_item_1 = items_context.add_sub_items(
        item_id=first_item_id, vat='17', items=[first_item_0, first_item_1],
    )
    cart_item_2 = items_context.add_sub_items(
        item_id=second_item_id, vat='0', items=[second_item_0, second_item_1],
    )

    grocery_cart.set_items_v2(items_context.items_v2)

    easy_count_items = [
        _to_easy_count_item(
            cart_item_1.item_id, cart_item_1.vat, first_item_0,
        ),
        _to_easy_count_item(
            cart_item_1.item_id, cart_item_1.vat, first_item_1,
        ),
        _to_easy_count_item(
            cart_item_2.item_id, cart_item_2.vat, second_item_0,
        ),
        _to_easy_count_item(
            cart_item_2.item_id, cart_item_2.vat, second_item_1,
        ),
    ]

    easy_count_v2.create.check(item=easy_count_items)

    await run_grocery_invoices_callback(
        items=items_context.stq_items, country=COUNTRY.name,
    )

    assert easy_count_v2.create.times_called == 1


# In case of only one item, document vat should be zero, because in
# document only one item and this item has zero vat, also for this item,
# vat_type should be NON (checking in conftest.py).

# If we have two items (0.0 vat and 13.0 vat), item with zero vat should
# be ignored and document vat should be 13.0, but vat_type for item with
# zero vat should be still NON.

# Case with three items (0.0 vat 13.0 vat and 13.0 vat) should be the same as
# with two items.

# Case with three items (0.0 vat 13.0 vat and 14.0 vat) is error.
@pytest.mark.parametrize(
    'document_vat,item_vats',
    [
        (consts.ZERO_VAT, [consts.ZERO_VAT]),
        ('13', [consts.ZERO_VAT, '13']),
        ('13', [consts.ZERO_VAT, '13', '13']),
        (None, [consts.ZERO_VAT, '13', '14']),
    ],
)
async def test_document_vat(
        grocery_orders,
        grocery_cart,
        easy_count_v2,
        run_grocery_invoices_callback,
        document_vat,
        item_vats,
):
    grocery_cart.set_cart_data(cart_id=consts.CART_ID)

    items_context = ItemsContext(country=COUNTRY)
    for idx, item_vat in enumerate(item_vats):
        item_id = f'item-id-{idx}'
        sub_item = SubItem(price='10', quantity='2', full_price='20')

        items_context.add_sub_items(
            item_id=item_id, vat=item_vat, items=[sub_item],
        )

    grocery_cart.set_items_v2(items_context.items_v2)

    easy_count_v2.create.check(vat=document_vat)

    await run_grocery_invoices_callback(
        items=items_context.stq_items,
        country=COUNTRY.name,
        expect_fail=(document_vat is None),
    )

    assert easy_count_v2.create.times_called == int(document_vat is not None)


@pytest_marks.RECEIPT_TYPES
async def test_stq_for_tlog(
        grocery_orders,
        grocery_cart,
        easy_count_v2,
        _run_stq,
        check_billing_tlog_callback_stq_event,
        receipt_type,
):
    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)

    await _run_stq(receipt_type=receipt_type)

    check_billing_tlog_callback_stq_event(
        info=dict(
            order_id=consts.ORDER_ID,
            country=COUNTRY.name,
            receipt_type=receipt_type,
            receipt_data_type=consts.ORDER_RECEIPT_DATA_TYPE,
            external_payment_id=consts.EXTERNAL_PAYMENT_ID,
            operation_id=consts.OPERATION_ID,
            terminal_id=consts.TERMINAL_ID,
            items=models.items_to_json(RECEIPT_ITEMS),
            payment_method=consts.DEFAULT_PAYMENT_METHOD,
            payment_finished=consts.PAYMENT_FINISHED,
        ),
        receipt_id=mock_easy_count.EASY_COUNT_DOC_NUMBER,
    )


@pytest_marks.RECEIPT_TYPES
async def test_store_receipt_pg(
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        easy_count_v2,
        _run_stq,
        receipt_type,
):
    receipt_data_type = consts.ORDER_RECEIPT_DATA_TYPE

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)

    await _run_stq(receipt_type=receipt_type)

    receipt = grocery_invoices_db.load_receipt(
        order_id=consts.ORDER_ID,
        receipt_id=mock_easy_count.EASY_COUNT_DOC_NUMBER,
    )
    assert receipt is not None
    assert receipt.receipt_data_type == receipt_data_type
    assert receipt.receipt_type == receipt_type
    assert receipt.link == mock_easy_count.EASY_COUNT_LINK
    assert receipt.receipt_source == consts.EASY_COUNT_SOURCE
    assert receipt.payload == dict(
        country=COUNTRY.name,
        external_id=mock_easy_count.EASY_COUNT_DOC_NUMBER,
        receipt_uuid=mock_easy_count.EASY_COUNT_DOC_UUID,
    )


def _to_easy_count_item(item_id, vat, item: SubItem):
    res = {'details': item_id + '_title', 'amount': item.quantity}

    if Decimal(vat) == Decimal(0):
        res['vat_type'] = 'NON'
    else:
        res['vat_type'] = 'INC'

    if item.full_price is not None and item.full_price != item.price:
        discount = Decimal(item.full_price) - Decimal(item.price)
        discount *= Decimal(item.quantity)

        res['discount_price'] = str(discount)
        res['discount_type'] = 'NUMBER'
        res['price'] = item.full_price
    else:
        res['price'] = item.price

    return res
