import decimal

import pytest

from tests_grocery_invoices import consts
from tests_grocery_invoices import helpers
from tests_grocery_invoices import models
from tests_grocery_invoices import pytest_marks
from tests_grocery_invoices.plugins import configs
from tests_grocery_invoices.plugins import mock_document_templator
from tests_grocery_invoices.stq.configs import france as country_configs

# pylint: disable=invalid-name
Decimal = decimal.Decimal

COUNTRY = models.Country.France
COMPANY = country_configs.COMPANY
URL_TEMPLATE = country_configs.URL_TEMPLATE
GROUP_IP = configs.get_group_id(COUNTRY)

RECEIPT_PRODUCT_ITEMS = helpers.make_product_receipt(COUNTRY)
RECEIPT_DELIVERY_ITEMS = helpers.make_delivery_receipt(COUNTRY)
RECEIPT_TIPS_ITEMS = helpers.make_tips_receipt(COUNTRY)
RECEIPT_ITEMS = [
    *RECEIPT_PRODUCT_ITEMS,
    *RECEIPT_DELIVERY_ITEMS,
    *RECEIPT_TIPS_ITEMS,
]
CART_ITEMS = helpers.make_cart_items(COUNTRY)


@pytest.fixture
def _run_stq(run_grocery_invoices_callback):
    async def _do(items=None, **kwargs):
        items = models.items_to_json(items or RECEIPT_PRODUCT_ITEMS)

        await run_grocery_invoices_callback(
            country=COUNTRY.name, items=items, **kwargs,
        )

    return _do


@pytest.mark.config(
    CURRENCY_KEEP_TRAILING_ZEROS={'__default__': {'__default__': False}},
)
@pytest_marks.FORMATTER_CONFIGS
@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.MARK_NOW
@country_configs.RECEIPT_PARAMS
@pytest_marks.CURRENCY_FORMATTING_RULES
@pytest_marks.EUROPE_PAYMENT_TYPES
@pytest_marks.RECEIPT_DATA_TYPES
@pytest_marks.RECEIPT_TYPES
async def test_document_templator_request(
        grocery_orders,
        grocery_cart,
        document_templator,
        stq,
        _run_stq,
        payment_type,
        receipt_data_type,
        receipt_type,
):
    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    payment_method = {'id': 'payment_method-id', 'type': payment_type}

    date = (
        f'{consts.NOW_DAY}.{consts.NOW_MONTH}.{consts.NOW_YEAR_LAST_2_DIGITS}'
    )

    total_without_vat = Decimal(0)
    summary_vat = Decimal(0)
    total = Decimal(0)
    items = []

    for receipt_item in RECEIPT_ITEMS:
        total_without_vat += Decimal(receipt_item.total_without_vat())
        summary_vat += Decimal(receipt_item.total_vat())
        total += Decimal(receipt_item.total())
        items.append(
            {
                'net': _format_price(receipt_item.total_without_vat()),
                'quantity': receipt_item.quantity,
                'title': receipt_item.title,
                'total': _format_price(receipt_item.total()),
                'tva': _format_price(receipt_item.total_vat()),
                'tva_percent': f'{receipt_item.vat}%',
                'price_with_vat': _format_price(receipt_item.price_with_vat()),
            },
        )
        _check_total_with_vat(receipt_item)

    assert total_without_vat + summary_vat == total

    payment_info_title_en = pytest_marks.get_payment_title(
        COUNTRY, payment_type, receipt_type, 'en',
    )
    payment_info_title_fr = pytest_marks.get_payment_title(
        COUNTRY, payment_type, receipt_type, 'fr',
    )

    payment_info_title = f'{payment_info_title_en} / {payment_info_title_fr}'

    document_templator.check_create_receipt(
        group_id=GROUP_IP,
        description=' ',
        generate_text_immediately=True,
        name=f'{consts.EXTERNAL_PAYMENT_ID}-{receipt_data_type}',
        params=[
            {
                'name': 'user',
                'value': {
                    'address': consts.ORDER_ADDRESS,
                    'recipient': consts.PASSPORT_CUSTOMER_NAME,
                },
            },
            {
                'name': 'company',
                'value': {
                    'address': COMPANY['address'],
                    'email': COMPANY['email'],
                    'name': COMPANY['name'],
                    'rcs_number': COMPANY['rcs_number'],
                    'siret_number': COMPANY['siret_number'],
                },
            },
            {'name': 'payment_info_title', 'value': payment_info_title},
            {'name': 'head_html', 'value': country_configs.HEAD_HTML},
            {
                'name': 'order',
                'value': {
                    'date': date,
                    'items': [*items],
                    'number': consts.SHORT_ORDER_ID,
                },
            },
            {
                'name': 'tva_details',
                'value': {
                    'net': _format_price(total_without_vat),
                    'total': _format_price(total),
                    'tva': _format_price(summary_vat),
                    'tva_number': COMPANY['tva_number'],
                },
            },
        ],
        template_id=country_configs.TEMPLATE_ID,
    )

    await _run_stq(
        receipt_type=receipt_type,
        receipt_data_type=receipt_data_type,
        payment_method=payment_method,
        items=RECEIPT_ITEMS,
    )

    assert stq.grocery_invoices_receipt_polling.times_called == 0
    assert stq.grocery_payments_billing_tlog_callback.times_called == 1


@pytest_marks.TRANSLATIONS_MARK
@country_configs.RECEIPT_PARAMS
@pytest_marks.RECEIPT_TYPES
async def test_check_billing_event(
        grocery_orders,
        grocery_cart,
        document_templator,
        check_billing_tlog_callback_stq_event,
        _run_stq,
        receipt_type,
):
    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    await _run_stq(receipt_type=receipt_type)

    check_billing_tlog_callback_stq_event(
        info=dict(
            order_id=consts.ORDER_ID,
            country=COUNTRY.name,
            receipt_type=receipt_type,
            external_payment_id=consts.EXTERNAL_PAYMENT_ID,
            operation_id=consts.OPERATION_ID,
            terminal_id=consts.TERMINAL_ID,
            items=models.items_to_json(RECEIPT_PRODUCT_ITEMS),
            payment_method=consts.DEFAULT_PAYMENT_METHOD,
            payment_finished=consts.PAYMENT_FINISHED,
            receipt_data_type='order',
        ),
    )


@pytest_marks.MARK_NOW
@pytest_marks.TRANSLATIONS_MARK
@country_configs.RECEIPT_PARAMS
@pytest_marks.RECEIPT_TYPES
async def test_retry_and_400_already_exists(
        grocery_orders,
        grocery_cart,
        document_templator,
        _run_stq,
        receipt_type,
):
    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    document_templator.mock_error(
        code='DYNAMIC_DOCUMENT_WITH_NAME_ALREADY_EXIST',
    )

    document_templator.check_document_by_name(
        name=f'{consts.EXTERNAL_PAYMENT_ID}-order',
    )

    await _run_stq(receipt_type=receipt_type)

    assert document_templator.times_document_by_name_called() == 1


@pytest_marks.MARK_NOW
@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.RECEIPT_TYPES
@country_configs.RECEIPT_PARAMS
async def test_append_receipt(
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        document_templator,
        _run_stq,
        receipt_type,
):
    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    await _run_stq(receipt_type=receipt_type)

    receipt = grocery_invoices_db.load_receipt(
        order_id=consts.ORDER_ID,
        receipt_id=mock_document_templator.DOCUMENT_ID,
    )

    assert receipt is not None
    assert receipt.receipt_data_type == consts.ORDER_RECEIPT_DATA_TYPE
    assert receipt.receipt_type == receipt_type
    assert receipt.link == URL_TEMPLATE.format(
        mock_document_templator.DOCUMENT_ID,
    )
    assert receipt.receipt_source == consts.FRANCE_DOCUMENT_TEMPLATOR_SOURCE
    assert receipt.payload['country'] == COUNTRY.name

    assert len(receipt.items) == len(RECEIPT_PRODUCT_ITEMS)
    for i, item in enumerate(receipt.items):
        assert item['item_id'] == CART_ITEMS[i].item_id
        assert item['item_type'] == RECEIPT_PRODUCT_ITEMS[i].item_type
        assert item['quantity'] == RECEIPT_PRODUCT_ITEMS[i].quantity
        assert item['price'] == RECEIPT_PRODUCT_ITEMS[i].price

    total = decimal.Decimal(0)
    for item in RECEIPT_PRODUCT_ITEMS:
        total += decimal.Decimal(item.total())
    assert receipt.total == total


@pytest_marks.MARK_NOW
@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.RECEIPT_TYPES
@country_configs.RECEIPT_PARAMS
async def test_receipt_notification(
        grocery_orders,
        grocery_cart,
        processing,
        document_templator,
        _run_stq,
        receipt_type,
):
    receipt_link = URL_TEMPLATE.format(mock_document_templator.DOCUMENT_ID)
    receipt_type_log = f'{receipt_type}_receipt'

    order = grocery_orders.order
    order.update(
        country_iso3=COUNTRY.country_iso3,
        locale='locale',
        app_info='app_info',
    )
    order['user_info'].update(
        taxi_user_id='taxi_user_id',
        eats_user_id='eats_user_id',
        personal_phone_id='personal_phone_id',
        personal_email_id='personal_email_id',
        yandex_uid='yandex_uid',
        user_ip='user_ip',
    )
    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS)

    await _run_stq(receipt_type=receipt_type)

    events = list(
        processing.events(scope='grocery', queue='processing_non_critical'),
    )

    assert len(events) == 1
    assert events[0].payload == {
        'order_id': consts.ORDER_ID,
        'reason': 'send_receipts',
        'order_log_info': {
            'receipts': [
                {
                    'receipt_type': receipt_type_log,
                    'receipt_url': receipt_link,
                    'title': receipt_type_log,
                    'creation_timestamp': consts.NOW,
                },
            ],
            'app_info': order['app_info'],
            'country_iso3': order['country_iso3'],
            'eats_user_id': order['user_info']['eats_user_id'],
            'locale': order['locale'],
            'personal_email_id': order['user_info']['personal_email_id'],
            'personal_phone_id': order['user_info']['personal_phone_id'],
            'taxi_user_id': order['user_info']['taxi_user_id'],
        },
        'yandex_uid': order['user_info']['yandex_uid'],
        'user_ip': order['user_info']['user_ip'],
    }


def _check_total_with_vat(item: models.Item):
    summary_vat = decimal.Decimal(item.total_vat())
    total_without_vat = decimal.Decimal(item.total_without_vat())

    total = decimal.Decimal(item.total())

    assert summary_vat + total_without_vat == total


def _format_price(price):
    price = str(price)
    price = price.replace('.', ',')
    return f'{price} €'
