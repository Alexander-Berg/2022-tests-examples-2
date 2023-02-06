# pylint: disable=C0302
# pylint: disable=import-only-modules
import copy
import datetime
import decimal

# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from grocery_mocks.utils import helpers as mock_helpers
from metrics_aggregations import helpers as metrics_helpers
import pytest

from tests_grocery_invoices import consts
from tests_grocery_invoices import eats_receipts_helpers
from tests_grocery_invoices import helpers
from tests_grocery_invoices import models
from tests_grocery_invoices import pytest_marks
from tests_grocery_invoices.items_context import ItemsContext
from tests_grocery_invoices.items_context import SubItem
from tests_grocery_invoices.plugins import configs
from tests_grocery_invoices.plugins import mock_eats_core_receipts
from tests_grocery_invoices.plugins import mock_eats_receipts

COUNTRY = models.Country.Russia

RECEIPT_PRODUCT_ITEMS = helpers.make_product_receipt(COUNTRY)
RECEIPT_DELIVERY_ITEMS = helpers.make_delivery_receipt(COUNTRY)
RECEIPT_TIPS_ITEMS = helpers.make_tips_receipt(COUNTRY)
RECEIPT_SERVICE_FEE_ITEMS = helpers.make_service_fee_receipt(COUNTRY)
RECEIPT_ITEMS = [*RECEIPT_PRODUCT_ITEMS, *RECEIPT_DELIVERY_ITEMS]
CART_ITEMS_RUS = helpers.make_cart_items(COUNTRY)

RECEIPT_TOTAL = '127.04'

PAYMENT_METHOD = {'id': 'card-x123', 'type': 'card'}
TIPS_ITEM_ID = 'tips'
ISRAEL_USER_NAME = f'{consts.PASSPORT_CUSTOMER_NAME} {consts.USER_PHONE}'

BADGE_PAYMENT_METHOD = {'id': 'badge-x123', 'type': 'badge'}
CORP_PAYMENT_METHOD = {'id': 'corp-x123', 'type': 'corp'}

TWO_DAYS_AGO = (
    consts.NOW_DT - datetime.timedelta(days=2)
).isoformat() + '+00:00'


SELF_EMPLOYED_COURIER = {
    'id': 'courier-id-1',
    'transport_type': 'pedestrian',
    'vat': '0',
    'personal_tin_id': consts.COURIER_TIN_ID,
}

DELIVERY_SERVICE_COURIER = {
    'id': 'courier-id-2',
    'transport_type': 'pedestrian',
    'vat': consts.DELIVERY_TAX,
    'personal_tin_id': consts.COURIER_TIN_ID,
    'organization_name': 'test-organization',
}

NAMES = {
    'delivery': consts.DELIVERY_RECEIPT_RU,
    'tips': consts.TIPS_RECEIPT_RU,
}


def add_items_title(items):
    for item in items:
        item.title = item.item_id + '_title'

    return items


CART_ITEMS_ISR = add_items_title(
    helpers.make_cart_items(models.Country.Israel),
)


def make_easy_count_item(
        item_id, price, quantity, full_price=None, title=None,
):
    if title is None:
        title = item_id + '_title'

    item = models.Item(
        item_id=item_id, price=str(price), quantity=str(quantity), title=title,
    )

    if full_price is not None:
        item.full_price = full_price

    return item


EASY_COUNT_ITEMS = [
    make_easy_count_item('item-id-1', price=10, quantity=1),
    make_easy_count_item('item-id-2', price=15, quantity=2),
    make_easy_count_item('item-id-3', price=20.51, quantity=4),
    make_easy_count_item(
        'delivery', price=5, quantity=1, title=consts.DELIVERY_RECEIPT_HE,
    ),
]


@pytest.fixture
def _run_stq(run_grocery_invoices_callback):
    async def _do(items=None, **kwargs):
        items = items or RECEIPT_ITEMS

        await run_grocery_invoices_callback(
            items=models.items_to_json(items), **kwargs,
        )

    return _do


@pytest.fixture(name='check_eats_receipt_create')
def _check_eats_receipt_create(
        eats_receipts, eats_core_receipts, grocery_orders,
):
    def _inner(service, receipt_data_type, products=None, is_refund=False):
        order = grocery_orders.order
        personal_phone_id = order['user_info']['personal_phone_id']

        if eats_receipts_helpers.is_eats_core_receipts(service):
            if products is None:
                products = mock_eats_core_receipts.convert_items(
                    cart_items=CART_ITEMS_RUS,
                    supplier_tin=order['depot']['tin'],
                )

            eats_core_receipts.check_receipt_send(
                documentId=f'{consts.EXTERNAL_PAYMENT_ID}'
                f'-{receipt_data_type}',
                isRefund=is_refund,
                order={
                    'countryCode': 'RU',
                    'orderNr': consts.ORDER_ID,
                    'orderType': 'native',
                    'paymentMethod': 'card',
                },
                products=products,
                userInfo={'userEmail': consts.USER_PHONE},
            )
        else:
            if products is None:
                products = mock_eats_receipts.convert_items(
                    cart_items=CART_ITEMS_RUS,
                    supplier_tin=grocery_orders.order['depot']['tin'],
                )

            eats_receipts.check_receipt_request(
                document_id=f'{consts.EXTERNAL_PAYMENT_ID}'
                f'-{receipt_data_type}',
                is_refund=is_refund,
                order={
                    'country_code': 'RU',
                    'order_nr': consts.ORDER_ID,
                    'payment_method': 'card',
                },
                products=products,
                user_info={'personal_phone_id': personal_phone_id},
            )

    return _inner


# pylint: disable=C0103
@pytest.fixture(name='check_eats_receipts_times_called')
def _check_eats_receipts_times_called(eats_receipts, eats_core_receipts):
    def _inner(service, times_called):
        if eats_receipts_helpers.is_eats_core_receipts(service):
            check_called = eats_core_receipts.times_receipts_send_called()
            assert check_called == times_called
        else:
            check_called = eats_receipts.times_receipts_request_called()
            assert check_called == times_called

    return _inner


@pytest_marks.EATS_RECEIPTS_SERVICES
@pytest_marks.MARK_NOW
async def test_callback_russia_eats_core_receipts(
        grocery_invoices_configs,
        grocery_orders,
        grocery_cart,
        check_receipt_polling_stq_event,
        check_eats_receipt_create,
        check_eats_receipts_times_called,
        _run_stq,
        eats_receipts_service,
):
    receipt_data_type = 'order'

    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_RUS)

    check_eats_receipt_create(
        service=eats_receipts_service, receipt_data_type=receipt_data_type,
    )

    await _run_stq(items=RECEIPT_PRODUCT_ITEMS)

    check_eats_receipts_times_called(
        service=eats_receipts_service, times_called=1,
    )

    check_receipt_polling_stq_event(
        params={
            'source': eats_receipts_helpers.eats_receipts_stq_source(
                eats_receipts_service,
            ),
        },
        polling_id=f'{consts.EXTERNAL_PAYMENT_ID}-{receipt_data_type}',
        info=dict(
            order_id=consts.ORDER_ID,
            country=COUNTRY.name,
            receipt_type='payment',
            receipt_data_type=receipt_data_type,
            external_payment_id=consts.EXTERNAL_PAYMENT_ID,
            operation_id=consts.OPERATION_ID,
            terminal_id=consts.TERMINAL_ID,
            items=models.items_to_json(RECEIPT_PRODUCT_ITEMS),
            payment_method=consts.DEFAULT_PAYMENT_METHOD,
            payment_finished=consts.PAYMENT_FINISHED,
        ),
    )


@pytest_marks.EATS_RECEIPTS_SERVICES
@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.MARK_NOW
@pytest.mark.parametrize(
    'courier_info, expected_vat, polling_times_called',
    [
        (DELIVERY_SERVICE_COURIER, DELIVERY_SERVICE_COURIER['vat'], 1),
        (SELF_EMPLOYED_COURIER, consts.SELFEMPLOYED_TAX, 2),
    ],
)
@pytest.mark.parametrize(
    'receipt_data_type, receipt_items',
    [
        (consts.DELIVERY_RECEIPT_DATA_TYPE, RECEIPT_DELIVERY_ITEMS),
        (consts.TIPS_RECEIPT_DATA_TYPE, RECEIPT_TIPS_ITEMS),
    ],
)
async def test_callback_russia_eats_receipts_delivery_or_tips(
        taxi_grocery_invoices,
        grocery_invoices_configs,
        grocery_orders,
        grocery_cart,
        selfemployed,
        check_receipt_polling_stq_event,
        check_eats_receipt_create,
        check_eats_receipts_times_called,
        _run_stq,
        courier_info,
        expected_vat,
        polling_times_called,
        receipt_data_type,
        receipt_items: list,
        eats_receipts_service,
):
    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    supplier_inn = (
        'supplierINN'
        if eats_receipts_helpers.is_eats_core_receipts(eats_receipts_service)
        else 'supplier_inn'
    )

    products = [
        {
            'id': receipt_item.item_id,
            'parent': None,
            'price': receipt_item.price,
            supplier_inn: consts.COURIER_TIN,
            'tax': expected_vat,
            'title': NAMES[receipt_data_type],
        }
        for receipt_item in receipt_items
    ]

    await taxi_grocery_invoices.invalidate_caches()

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_RUS)

    check_eats_receipt_create(
        service=eats_receipts_service,
        receipt_data_type=receipt_data_type,
        products=products,
    )

    grocery_orders.order.update(courier_info=courier_info)

    await _run_stq(receipt_data_type=receipt_data_type, items=receipt_items)

    check_eats_receipts_times_called(
        service=eats_receipts_service, times_called=1,
    )

    source = eats_receipts_helpers.eats_receipts_stq_source(
        eats_receipts_service,
    )

    stq_event_id = f'{consts.EXTERNAL_PAYMENT_ID}/{receipt_data_type}/{source}'

    check_receipt_polling_stq_event(
        stq_event_id=stq_event_id,
        times_called=polling_times_called,
        params={'source': source},
        polling_id=f'{consts.EXTERNAL_PAYMENT_ID}-{receipt_data_type}',
        info=dict(
            order_id=consts.ORDER_ID,
            country=COUNTRY.name,
            receipt_type='payment',
            receipt_data_type=receipt_data_type,
            external_payment_id=consts.EXTERNAL_PAYMENT_ID,
            operation_id=consts.OPERATION_ID,
            terminal_id=consts.TERMINAL_ID,
            items=models.items_to_json(receipt_items),
            payment_method=consts.DEFAULT_PAYMENT_METHOD,
            payment_finished=consts.PAYMENT_FINISHED,
        ),
    )


@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.MARK_NOW
async def test_callback_russia_service_fee(
        grocery_invoices_configs,
        grocery_orders,
        grocery_cart,
        check_receipt_polling_stq_event,
        check_eats_receipt_create,
        check_eats_receipts_times_called,
        _run_stq,
):
    receipt_data_type = consts.ORDER_RECEIPT_DATA_TYPE

    grocery_invoices_configs.eats_receipts_service(consts.EATS_RECEIPTS)

    products = [
        {
            'id': receipt_item.item_id,
            'parent': None,
            'price': receipt_item.price,
            'supplier_inn': grocery_orders.order['depot']['tin'],
            'tax': consts.RUSSIA_VAT,
            'title': consts.SERVICE_FEE_RECEIPT_RU,
        }
        for receipt_item in RECEIPT_SERVICE_FEE_ITEMS
    ]

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_RUS)

    check_eats_receipt_create(
        service=consts.EATS_RECEIPTS,
        receipt_data_type=receipt_data_type,
        products=products,
    )

    grocery_orders.order.update(courier_info=DELIVERY_SERVICE_COURIER)

    await _run_stq(items=RECEIPT_SERVICE_FEE_ITEMS)

    check_eats_receipts_times_called(
        service=consts.EATS_RECEIPTS, times_called=1,
    )

    check_receipt_polling_stq_event(
        params={
            'source': eats_receipts_helpers.eats_receipts_stq_source(
                consts.EATS_RECEIPTS,
            ),
        },
        polling_id=f'{consts.EXTERNAL_PAYMENT_ID}-{receipt_data_type}',
        info=dict(
            order_id=consts.ORDER_ID,
            country=COUNTRY.name,
            receipt_type='payment',
            receipt_data_type=receipt_data_type,
            external_payment_id=consts.EXTERNAL_PAYMENT_ID,
            operation_id=consts.OPERATION_ID,
            terminal_id=consts.TERMINAL_ID,
            items=models.items_to_json(RECEIPT_SERVICE_FEE_ITEMS),
            payment_method=consts.DEFAULT_PAYMENT_METHOD,
            payment_finished=consts.PAYMENT_FINISHED,
        ),
    )


@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.MARK_NOW
@pytest_marks.DEVELOPER_EMAIL_MARK
@pytest_marks.GROCERY_USER_UUID_MARK
@pytest_marks.RECEIPT_TYPES
@pytest_marks.EATS_RECEIPTS_SERVICES
async def test_invoices_callback_isr_expat_flow(
        taxi_grocery_invoices,
        grocery_invoices_configs,
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        personal,
        cardstorage,
        easy_count,
        check_billing_tlog_callback_stq_event,
        check_receipt_polling_stq_event,
        check_eats_receipt_create,
        default_isr_receipt,
        _run_stq,
        receipt_type,
        eats_receipts_service,
):
    country = models.Country.Israel
    payment_type = 'card'
    receipt_data_type = consts.ORDER_RECEIPT_DATA_TYPE
    payment_method = {'type': payment_type, 'id': 'payment-id'}

    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)
    grocery_invoices_configs.grocery_invoices_russia_tin_expat_params()

    grocery_orders.order.update(grocery_flow_version=consts.EXPAT_FLOW_VERSION)
    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)

    vat = CART_ITEMS_ISR[0].vat
    payment = easy_count.get_easy_count_payment(
        total_price='0', payment_type=payment_type,
    )
    invoice_type = (
        consts.EASY_COUNT_PAYMENT
        if receipt_type == consts.TYPE_PAYMENT
        else consts.EASY_COUNT_REFUND
    )

    items = copy.deepcopy(EASY_COUNT_ITEMS)

    for item in items:
        if item.item_id != 'delivery':
            item.full_price = item.price
        item.price = '0'

    easy_count.check_request(
        customer_name=ISRAEL_USER_NAME,
        developer_email=consts.DEVELOPER_EMAIL,
        items=items,
        payment=payment,
        price_total=payment.payment_sum,
        idempotency_token=consts.EXTERNAL_PAYMENT_ID + receipt_data_type,
        invoice_type=invoice_type,
        is_payment=receipt_type == consts.TYPE_PAYMENT,
        user_uuid=consts.GROCERY_USER_UUID,
        document_vat=vat,
    )

    supplier_inn = (
        'supplierINN'
        if eats_receipts_helpers.is_eats_core_receipts(eats_receipts_service)
        else 'supplier_inn'
    )

    check_eats_receipt_create(
        service=eats_receipts_service,
        receipt_data_type=receipt_data_type,
        is_refund=(receipt_type == consts.TYPE_REFUND),
        products=[
            {
                'id': 'expat_coupon',
                'parent': None,
                'price': RECEIPT_TOTAL,
                supplier_inn: consts.GROCERY_TIN,
                'tax': consts.RUSSIA_VAT,
                'title': (
                    consts.EXPAT_PAYMENT_COUPON_RU
                    if receipt_type == consts.TYPE_PAYMENT
                    else consts.EXPAT_REFUND_COUPON_RU
                ),
            },
        ],
    )

    await _run_stq(
        receipt_type=receipt_type,
        country=country.name,
        payment_method=payment_method,
        items=RECEIPT_ITEMS,
    )

    check_billing_tlog_callback_stq_event(
        info=dict(
            order_id=consts.ORDER_ID,
            country=country.name,
            receipt_type=receipt_type,
            receipt_data_type=receipt_data_type,
            external_payment_id=consts.EXTERNAL_PAYMENT_ID,
            operation_id=consts.OPERATION_ID,
            terminal_id=consts.TERMINAL_ID,
            items=[
                {
                    'item_id': item.item_id,
                    'price': '0',
                    'quantity': item.quantity,
                    'item_type': item.item_type,
                }
                for item in RECEIPT_ITEMS
            ],
            payment_method=payment_method,
            payment_finished=consts.PAYMENT_FINISHED,
            currency=country.currency,
        ),
        receipt_id=consts.EASY_COUNT_DOC_NUMBER,
    )

    event_id = helpers.make_polling_task_id(
        consts.EXTERNAL_PAYMENT_ID,
        receipt_data_type,
        eats_receipts_helpers.eats_receipts_stq_source(eats_receipts_service),
    )

    check_receipt_polling_stq_event(
        stq_event_id=event_id,
        info=mock_helpers.sub_dict(
            order_id=consts.ORDER_ID,
            country=models.Country.Russia.name,
            receipt_type=receipt_type,
            receipt_data_type=receipt_data_type,
            items=[
                {
                    'item_id': 'expat_coupon',
                    'price': RECEIPT_TOTAL,
                    'quantity': '1',
                    'item_type': 'expat_coupon',
                },
            ],
            currency=models.Country.Russia.currency,
        ),
        params={
            'source': eats_receipts_helpers.eats_receipts_stq_source(
                eats_receipts_service,
            ),
        },
        polling_id=f'{consts.EXTERNAL_PAYMENT_ID}-{receipt_data_type}',
        task_created=consts.NOW,
    )

    assert easy_count.times_called() == 1

    receipt = grocery_invoices_db.load_receipt(
        order_id=consts.ORDER_ID, receipt_id=consts.EASY_COUNT_DOC_NUMBER,
    )
    assert receipt is not None
    assert receipt.receipt_data_type == receipt_data_type
    assert receipt.receipt_type == receipt_type
    assert receipt.link == consts.EASY_COUNT_LINK
    assert receipt.receipt_source == consts.EASY_COUNT_SOURCE
    assert receipt.payload['country'] == country.name

    assert len(receipt.items) == len(RECEIPT_ITEMS)
    for i, item in enumerate(receipt.items):
        assert item['item_type'] == RECEIPT_ITEMS[i].item_type
        assert item['quantity'] == RECEIPT_ITEMS[i].quantity
        assert item['price'] == '0'

    assert receipt.total == decimal.Decimal(0)


@pytest_marks.MARK_NOW
async def test_callback_russia_splitted_receipts(
        grocery_invoices_configs,
        grocery_cart,
        check_eats_receipts_times_called,
        check_receipt_polling_stq_event,
        _run_stq,
        eats_receipts,
        grocery_orders,
):
    eats_receipts_service = consts.EATS_RECEIPTS
    tin1 = 'tin1'
    tin2 = 'tin2'

    first_item_id = 'item-id-0'
    first_item_0 = SubItem(price='10', quantity='2', full_price='20')
    first_item_1 = SubItem(price='20', quantity='1', full_price='20')

    second_item_id = 'item-id-1'
    second_item_0 = SubItem(price='15.1', quantity='2', full_price='20.99')
    second_item_1 = SubItem(price='17.29', quantity='1', full_price='20.17')

    items_context = ItemsContext(country=COUNTRY)
    cart_item_1 = items_context.add_sub_items(
        item_id=first_item_id,
        items=[first_item_0, first_item_1],
        supplier_tin=tin1,
    )
    cart_item_2 = items_context.add_sub_items(
        item_id=second_item_id,
        items=[second_item_0, second_item_1],
        supplier_tin=tin2,
    )

    receipt_data_type = 'order'

    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)
    grocery_invoices_configs.split_receipts_by_supplier_tin(enabled=True)

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(items_context.items_v2)

    order = grocery_orders.order
    personal_phone_id = order['user_info']['personal_phone_id']

    requests = [
        {
            'document_id': (
                f'{consts.EXTERNAL_PAYMENT_ID}' f'-{receipt_data_type}'
            ),
            'is_refund': False,
            'order': {
                'country_code': 'RU',
                'order_nr': consts.ORDER_ID,
                'payment_method': 'card',
            },
            'products': product,
            'user_info': {'personal_phone_id': personal_phone_id},
        }
        for product in [
            mock_eats_receipts.convert_items([cart_item_1]),
            mock_eats_receipts.convert_items([cart_item_2]),
        ]
    ]

    eats_receipts.check_receipt_requests(requests)

    item_1, item_2, item_3, item_4 = [
        helpers.make_receipt_item(**item) for item in items_context.stq_items
    ]

    receipt_product_items = [item_1, item_2, item_3, item_4]

    await _run_stq(items=receipt_product_items)

    check_eats_receipts_times_called(
        service=eats_receipts_service, times_called=2,
    )

    events = [([item_3, item_4], tin2), ([item_1, item_2], tin1)]

    for items, supplier_tin in events:
        check_receipt_polling_stq_event(
            times_called=None,
            params={
                'source': eats_receipts_helpers.eats_receipts_stq_source(
                    eats_receipts_service,
                ),
            },
            polling_id=f'{consts.EXTERNAL_PAYMENT_ID}-{receipt_data_type}',
            info=dict(
                order_id=consts.ORDER_ID,
                country=COUNTRY.name,
                receipt_type='payment',
                receipt_data_type=receipt_data_type,
                external_payment_id=consts.EXTERNAL_PAYMENT_ID,
                operation_id=consts.OPERATION_ID,
                terminal_id=consts.TERMINAL_ID,
                items=models.items_to_json(items),
                payment_method=consts.DEFAULT_PAYMENT_METHOD,
                payment_finished=consts.PAYMENT_FINISHED,
                supplier_tin=supplier_tin,
            ),
        )


@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.MARK_NOW
@pytest_marks.DEVELOPER_EMAIL_MARK
@pytest_marks.GROCERY_USER_UUID_MARK
async def test_long_order_id_israel(
        taxi_grocery_invoices,
        grocery_orders,
        grocery_cart,
        personal,
        cardstorage,
        easy_count,
        _run_stq,
):
    payment_type = 'card'
    receipt_type = 'payment'

    payment_method = {'type': payment_type, 'id': 'payment-id'}

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)

    await _run_stq(
        external_payment_id='x' * 1000,
        receipt_type=receipt_type,
        country=models.Country.Israel.name,
        payment_method=payment_method,
    )

    assert easy_count.times_called() == 1


@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.MARK_NOW
@pytest_marks.DEVELOPER_EMAIL_MARK
@pytest_marks.GROCERY_USER_UUID_MARK
@pytest.mark.parametrize(
    'courier_info', [None, consts.DELIVERY_SERVICE_COURIER],
)
async def test_no_courier_info(
        taxi_grocery_invoices,
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        personal,
        cardstorage,
        easy_count,
        courier_info,
        _run_stq,
):
    payment_type = 'card'
    receipt_type = 'payment'

    payment_method = {'type': payment_type, 'id': 'payment-id'}

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)

    grocery_orders.order.update(courier_info=courier_info)

    await _run_stq(
        task_id=consts.TASK_ID,
        receipt_type=receipt_type,
        country=models.Country.Israel.name,
        payment_method=payment_method,
        expect_fail=(courier_info is None),
    )

    if courier_info is None:
        pg_task = grocery_invoices_db.load_task(consts.TASK_ID)
        assert pg_task.status == 'failed'
        assert pg_task.params['error_code'] == 'no_courier_info::tlog'


@configs.GROCERY_RECEIPTS_POLLING_POLICY
@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.MARK_NOW
@pytest_marks.DEVELOPER_EMAIL_MARK
@pytest_marks.GROCERY_USER_UUID_MARK
@pytest.mark.parametrize(
    'receipt_type, receipt_data_type, expect_fail',
    [
        ('payment', 'order', False),
        ('payment', 'tips', True),
        ('refund', 'order', True),
    ],
)
async def test_invoices_callback_isr_no_order_receipt(
        taxi_grocery_invoices,
        grocery_orders,
        grocery_cart,
        personal,
        cardstorage,
        easy_count,
        stq,
        _run_stq,
        receipt_type,
        receipt_data_type,
        expect_fail,
):
    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)

    await _run_stq(
        country=models.Country.Israel.name,
        receipt_type=receipt_type,
        receipt_data_type=receipt_data_type,
    )

    assert stq.grocery_invoices_callback.times_called == int(expect_fail)

    assert easy_count.times_called() == int(not expect_fail)


@configs.GROCERY_RECEIPTS_POLLING_POLICY
@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.MARK_NOW
@pytest_marks.DEVELOPER_EMAIL_MARK
@pytest_marks.GROCERY_USER_UUID_MARK
@pytest.mark.parametrize(
    'task_created, easy_count_times_called',
    [(consts.NOW, 0), (TWO_DAYS_AGO, 1)],
)
@pytest.mark.parametrize('add_tip_receipts', [False, True])
async def test_isr_no_order_receipt_time_left(
        taxi_grocery_invoices,
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        personal,
        cardstorage,
        easy_count,
        stq,
        _run_stq,
        add_tip_receipts,
        task_created,
        easy_count_times_called,
):
    country = models.Country.Israel
    receipt_type = 'payment'
    receipt_data_type = 'delivery'

    receipt_uuid = 'root_receipt_uuid'

    if add_tip_receipts:
        grocery_invoices_db.insert(
            models.Receipt(
                payload=dict(
                    country=country.name,
                    receipt_uuid=receipt_uuid,
                    external_id='external_id',
                ),
                receipt_data_type='tips',
            ),
        )

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)

    await _run_stq(
        country=country.name,
        receipt_type=receipt_type,
        receipt_data_type=receipt_data_type,
        task_created=task_created,
    )

    assert easy_count.times_called() == easy_count_times_called


@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.MARK_NOW
@pytest_marks.DEVELOPER_EMAIL_MARK
@pytest_marks.GROCERY_USER_UUID_MARK
@pytest_marks.RECEIPT_TYPES
async def test_easy_count_tips(
        taxi_grocery_invoices,
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        personal,
        cardstorage,
        easy_count,
        check_billing_tlog_callback_stq_event,
        default_isr_receipt,
        _run_stq,
        receipt_type,
):
    country = models.Country.Israel
    receipt_data_type = 'tips'

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)

    tips_price = '199'

    vat = consts.ISRAEL_VAT
    payment = easy_count.get_easy_count_payment(total_price=tips_price)
    invoice_type = (
        consts.EASY_COUNT_PAYMENT
        if receipt_type == consts.TYPE_PAYMENT
        else consts.EASY_COUNT_REFUND
    )

    stq_items = [
        helpers.make_receipt_item(
            TIPS_ITEM_ID, price=tips_price, quantity=1, item_type='tips',
        ),
    ]

    easy_count.check_request(
        customer_name=ISRAEL_USER_NAME,
        developer_email=consts.DEVELOPER_EMAIL,
        items=[
            make_easy_count_item(
                TIPS_ITEM_ID,
                price=tips_price,
                quantity=1,
                title=consts.TIPS_RECEIPT_HE,
            ),
        ],
        payment=payment,
        price_total=payment.payment_sum,
        idempotency_token=consts.EXTERNAL_PAYMENT_ID + receipt_data_type,
        invoice_type=invoice_type,
        is_payment=receipt_type == consts.TYPE_PAYMENT,
        user_uuid=consts.GROCERY_USER_UUID,
        document_vat=vat,
    )
    await _run_stq(
        receipt_type=receipt_type,
        country=country.name,
        items=stq_items,
        receipt_data_type=receipt_data_type,
    )

    check_billing_tlog_callback_stq_event(
        info=mock_helpers.sub_dict(
            receipt_type=receipt_type,
            country=country.name,
            external_payment_id=consts.EXTERNAL_PAYMENT_ID,
            items=models.items_to_json(stq_items),
        ),
        receipt_id=consts.EASY_COUNT_DOC_NUMBER,
    )
    assert easy_count.times_called() == 1

    receipt = grocery_invoices_db.load_receipt(
        order_id=consts.ORDER_ID, receipt_id=consts.EASY_COUNT_DOC_NUMBER,
    )
    assert receipt is not None
    assert receipt.receipt_data_type == receipt_data_type
    assert receipt.items == [
        {
            'item_id': TIPS_ITEM_ID,
            'item_type': 'tips',
            'price': tips_price,
            'quantity': '1',
        },
    ]
    assert receipt.total == decimal.Decimal(tips_price)


@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.MARK_NOW
@pytest_marks.RECEIPT_TYPES
@pytest.mark.parametrize(
    'receipt_data_type, receipt_items',
    [
        (consts.DELIVERY_RECEIPT_DATA_TYPE, RECEIPT_DELIVERY_ITEMS),
        (consts.TIPS_RECEIPT_DATA_TYPE, RECEIPT_TIPS_ITEMS),
    ],
)
@pytest.mark.parametrize(
    'payment_method', [BADGE_PAYMENT_METHOD, CORP_PAYMENT_METHOD],
)
@pytest_marks.EATS_RECEIPTS_SERVICES
async def test_callback_badge_and_corp(
        grocery_invoices_configs,
        grocery_orders,
        grocery_cart,
        check_receipt_polling_stq_event,
        check_billing_tlog_callback_stq_event,
        _run_stq,
        receipt_type,
        receipt_data_type,
        receipt_items,
        payment_method,
        eats_receipts_service,
):
    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_RUS)

    grocery_orders.order.update(courier_info=DELIVERY_SERVICE_COURIER)

    await _run_stq(
        receipt_type=receipt_type,
        country=COUNTRY.name,
        payment_method=payment_method,
        receipt_data_type=receipt_data_type,
        items=receipt_items,
    )

    check_receipt_polling_stq_event(
        times_called=0, receipt_id=consts.EASY_COUNT_DOC_NUMBER,
    )

    check_billing_tlog_callback_stq_event(
        info=mock_helpers.sub_dict(
            receipt_type=receipt_type,
            country=COUNTRY.name,
            payment_method=payment_method,
            receipt_data_type=receipt_data_type,
            items=models.items_to_json(receipt_items),
        ),
    )


@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.MARK_NOW
@pytest_marks.RECEIPT_TYPES
@pytest_marks.EATS_RECEIPTS_SERVICES
@pytest.mark.parametrize(
    'receipt_data_type, receipt_items',
    [
        (consts.DELIVERY_RECEIPT_DATA_TYPE, RECEIPT_DELIVERY_ITEMS),
        (consts.TIPS_RECEIPT_DATA_TYPE, RECEIPT_TIPS_ITEMS),
    ],
)
@pytest.mark.parametrize(
    'payment_method', [BADGE_PAYMENT_METHOD, CORP_PAYMENT_METHOD],
)
async def test_callback_badge_and_corp_fns(
        grocery_invoices_configs,
        grocery_orders,
        grocery_cart,
        selfemployed,
        check_receipt_polling_stq_event,
        check_billing_tlog_callback_stq_event,
        default_fns_receipt,
        _run_stq,
        receipt_type,
        receipt_data_type,
        receipt_items,
        payment_method,
        eats_receipts_service,
):
    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_RUS)

    grocery_orders.order.update(courier_info=SELF_EMPLOYED_COURIER)

    await _run_stq(
        receipt_type=receipt_type,
        country=COUNTRY.name,
        receipt_data_type=receipt_data_type,
        payment_method=payment_method,
        items=receipt_items,
    )

    if receipt_type == consts.TYPE_PAYMENT:
        assert selfemployed.times_register_income_called() == 1
        assert selfemployed.times_revert_income_called() == 0
    else:
        assert selfemployed.times_revert_income_called() == 1
        assert selfemployed.times_register_income_called() == 0

    event_id = helpers.make_polling_task_id(
        selfemployed.default_message_id, receipt_data_type, consts.FNS_SOURCE,
    )
    check_receipt_polling_stq_event(
        times_called=1,
        stq_event_id=event_id,
        info=mock_helpers.sub_dict(
            country=COUNTRY.name,
            order_id=consts.ORDER_ID,
            receipt_type=receipt_type,
            receipt_data_type=receipt_data_type,
        ),
        params={'source': consts.FNS_SOURCE},
        polling_id=selfemployed.default_message_id,
        task_created=consts.NOW,
    )

    check_billing_tlog_callback_stq_event(
        info=mock_helpers.sub_dict(
            receipt_type=receipt_type,
            country=COUNTRY.name,
            payment_method=payment_method,
            receipt_data_type=receipt_data_type,
            items=models.items_to_json(receipt_items),
        ),
    )


@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.EATS_RECEIPTS_SERVICES
@pytest_marks.MARK_NOW
@pytest_marks.RECEIPT_TYPES
@pytest.mark.parametrize(
    'receipt_data_type, receipt_items',
    [
        (consts.DELIVERY_RECEIPT_DATA_TYPE, RECEIPT_DELIVERY_ITEMS),
        (consts.TIPS_RECEIPT_DATA_TYPE, RECEIPT_TIPS_ITEMS),
    ],
)
async def test_callback_russia_fns(
        grocery_invoices_configs,
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        personal,
        selfemployed,
        check_receipt_polling_stq_event,
        default_fns_receipt,
        _run_stq,
        receipt_type,
        receipt_data_type,
        receipt_items,
        eats_receipts_service,
):
    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_RUS)

    grocery_orders.order.update(courier_info=SELF_EMPLOYED_COURIER)

    selfemployed.check_register_income(
        inn=consts.COURIER_TIN,
        services=[
            {
                'Name': NAMES[receipt_data_type],
                'Quantity': int(receipt_items[0].quantity),
                'Amount': receipt_items[0].price,
            },
        ],
    )

    await _run_stq(
        receipt_type=receipt_type,
        receipt_data_type=receipt_data_type,
        items=receipt_items,
    )

    if receipt_type == consts.TYPE_PAYMENT:
        assert selfemployed.times_register_income_called() == 1
        assert selfemployed.times_revert_income_called() == 0
    else:
        assert selfemployed.times_revert_income_called() == 1
        assert selfemployed.times_register_income_called() == 0

    event_id = helpers.make_polling_task_id(
        selfemployed.default_message_id, receipt_data_type, consts.FNS_SOURCE,
    )
    check_receipt_polling_stq_event(
        times_called=2,
        stq_event_id=event_id,
        info=mock_helpers.sub_dict(
            order_id=consts.ORDER_ID,
            country=COUNTRY.name,
            receipt_type=receipt_type,
            receipt_data_type=receipt_data_type,
        ),
        params={'source': consts.FNS_SOURCE},
        polling_id=selfemployed.default_message_id,
        task_created=consts.NOW,
    )

    event_id = helpers.make_polling_task_id(
        consts.EXTERNAL_PAYMENT_ID,
        receipt_data_type,
        eats_receipts_helpers.eats_receipts_stq_source(eats_receipts_service),
    )
    check_receipt_polling_stq_event(
        stq_event_id=event_id,
        info=mock_helpers.sub_dict(
            order_id=consts.ORDER_ID,
            country=COUNTRY.name,
            receipt_type=receipt_type,
            receipt_data_type=receipt_data_type,
        ),
        params={
            'source': eats_receipts_helpers.eats_receipts_stq_source(
                eats_receipts_service,
            ),
        },
        polling_id=f'{consts.EXTERNAL_PAYMENT_ID}-{receipt_data_type}',
        task_created=consts.NOW,
    )


@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.EATS_RECEIPTS_SERVICES
@pytest_marks.MARK_NOW
@pytest_marks.RECEIPT_TYPES
@pytest.mark.parametrize(
    'order_status',
    [
        'draft',
        'checked_out',
        'reserving',
        'reserved',
        'assembling',
        'assembled',
        'delivering',
        'pending_cancel',
    ],
)
@pytest.mark.parametrize(
    'receipt_data_type, receipt_items',
    [
        (consts.DELIVERY_RECEIPT_DATA_TYPE, RECEIPT_DELIVERY_ITEMS),
        (consts.TIPS_RECEIPT_DATA_TYPE, RECEIPT_TIPS_ITEMS),
    ],
)
async def test_delivery_or_tips_not_finished_order(
        grocery_invoices_configs,
        grocery_orders,
        grocery_cart,
        stq,
        _run_stq,
        receipt_type,
        order_status,
        receipt_data_type,
        receipt_items,
        eats_receipts_service,
):
    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    grocery_orders.order.update(status=order_status)

    await _run_stq(
        receipt_type=receipt_type,
        receipt_data_type=receipt_data_type,
        items=receipt_items,
    )

    assert stq.grocery_invoices_callback.times_called == 1


@configs.GROCERY_RECEIPTS_POLLING_POLICY
@pytest_marks.RECEIPT_TYPES
@pytest.mark.parametrize('delta, expect_fail', [(-1, False), (1, True)])
@pytest.mark.parametrize(
    'receipt_data_type, receipt_items',
    [
        (consts.DELIVERY_RECEIPT_DATA_TYPE, RECEIPT_DELIVERY_ITEMS),
        (consts.TIPS_RECEIPT_DATA_TYPE, RECEIPT_TIPS_ITEMS),
    ],
)
async def test_delivery_or_tips_not_finished_order_error_after(
        grocery_orders,
        stq_runner,
        stq,
        mocked_time,
        _run_stq,
        receipt_type,
        delta,
        expect_fail,
        receipt_data_type,
        receipt_items,
):
    now_delta = datetime.timedelta(
        seconds=configs.POLICY_ERROR_AFTER_SECONDS + delta,
    )
    mocked_time.set(consts.NOW_DT + now_delta)

    grocery_orders.order.update(status='assembling')

    await _run_stq(
        receipt_type=receipt_type,
        receipt_data_type=receipt_data_type,
        items=receipt_items,
        expect_fail=expect_fail,
    )

    assert (
        stq.grocery_invoices_callback.times_called == 0 if expect_fail else 1
    )


@pytest_marks.MARK_NOW
@pytest_marks.RECEIPT_TYPES
@pytest_marks.EATS_RECEIPTS_SERVICES
async def test_callback_helping_hand(
        grocery_invoices_configs,
        grocery_orders,
        grocery_cart,
        check_receipt_polling_stq_event,
        check_billing_tlog_callback_stq_event,
        _run_stq,
        receipt_type,
        eats_receipts_service,
):
    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    receipt_data_type = consts.HELPING_HAND_RECEIPT_DATA_TYPE

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_RUS)

    await _run_stq(
        receipt_type=receipt_type,
        country=COUNTRY.name,
        payment_method=PAYMENT_METHOD,
        receipt_data_type=receipt_data_type,
    )

    check_receipt_polling_stq_event(times_called=0)

    check_billing_tlog_callback_stq_event(
        info=mock_helpers.sub_dict(
            receipt_type=receipt_type,
            country=COUNTRY.name,
            payment_method=PAYMENT_METHOD,
            receipt_data_type=receipt_data_type,
        ),
    )


@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.MARK_NOW
@pytest_marks.RECEIPT_TYPES
@pytest.mark.parametrize(
    'receipt_data_type, receipt_items',
    [
        (consts.ORDER_RECEIPT_DATA_TYPE, RECEIPT_PRODUCT_ITEMS),
        (consts.DELIVERY_RECEIPT_DATA_TYPE, RECEIPT_DELIVERY_ITEMS),
        (consts.TIPS_RECEIPT_DATA_TYPE, RECEIPT_TIPS_ITEMS),
        (consts.ORDER_RECEIPT_DATA_TYPE, RECEIPT_SERVICE_FEE_ITEMS),
    ],
)
@pytest.mark.parametrize(
    'valid_vat',
    [
        dict(
            product=[consts.RUSSIA_VAT],
            delivery=[consts.DELIVERY_TAX],
            tips=[consts.DELIVERY_TAX],
            service_fee=[consts.RUSSIA_VAT],
            expect_fail=False,
        ),
        dict(
            product=[], delivery=[], tips=[], service_fee=[], expect_fail=True,
        ),
    ],
)
async def test_vat_validation(
        grocery_invoices_configs,
        taxi_grocery_invoices_monitor,
        grocery_orders,
        grocery_cart,
        _run_stq,
        receipt_type,
        receipt_data_type,
        receipt_items,
        valid_vat,
):
    expect_fail = valid_vat['expect_fail']

    grocery_invoices_configs.eats_receipts_service(consts.EATS_RECEIPTS)
    grocery_invoices_configs.set_valid_vat(**valid_vat)

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_RUS)

    grocery_orders.order.update(courier_info=DELIVERY_SERVICE_COURIER)

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_invoices_monitor,
            sensor='grocery_invoices_invalid_vat',
    ) as collector:
        await _run_stq(
            expect_fail=expect_fail,
            receipt_type=receipt_type,
            country=COUNTRY.name,
            receipt_data_type=receipt_data_type,
            items=receipt_items,
        )

    metric = collector.get_single_collected_metric()
    if expect_fail:
        assert metric.value == 1
    else:
        assert metric is None


@pytest_marks.MARK_NOW
@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.DEVELOPER_EMAIL_MARK
@pytest_marks.GROCERY_USER_UUID_MARK
@pytest.mark.parametrize('card_pan', ['123456******44', '1234******44'])
async def test_bad_pci_dss(
        taxi_grocery_invoices,
        grocery_orders,
        grocery_cart,
        personal,
        cardstorage,
        easy_count,
        default_isr_receipt,
        _run_stq,
        card_pan,
):
    cardstorage.set_pan(pan=card_pan)

    receipt_type = models.ReceiptType.payment.value
    payment_type = models.PaymentType.card.value
    payment_method = {'type': payment_type, 'id': 'payment-id'}

    # no http calls to service in test, so explicit call is required
    await taxi_grocery_invoices.invalidate_caches()

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)
    await _run_stq(
        receipt_type=receipt_type,
        country=models.Country.Israel.name,
        payment_method=payment_method,
        expect_fail=True,
    )

    assert easy_count.times_called() == 0
    assert cardstorage.times_card_called() == 1


@pytest_marks.MARK_NOW
@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.DEVELOPER_EMAIL_MARK
@pytest_marks.GROCERY_USER_UUID_MARK
@pytest.mark.parametrize(
    'card_pan, last_digits',
    [('123456*****12', '12'), ('123456******1234', '1234')],
)
async def test_pci_dss(
        taxi_grocery_invoices,
        grocery_orders,
        grocery_cart,
        personal,
        cardstorage,
        easy_count,
        default_isr_receipt,
        _run_stq,
        card_pan,
        last_digits,
):
    receipt_data_type = 'order'

    cardstorage.set_pan(pan=card_pan)

    receipt_type = models.ReceiptType.payment.value
    payment_type = models.PaymentType.card.value
    payment_method = {'type': payment_type, 'id': 'payment-id'}

    # no http calls to service in test, so explicit call is required
    await taxi_grocery_invoices.invalidate_caches()

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)

    vat = CART_ITEMS_ISR[0].vat
    payment = easy_count.get_easy_count_payment(
        total_price=RECEIPT_TOTAL,
        payment_type=payment_type,
        cc_number=last_digits,
    )
    invoice_type = (
        consts.EASY_COUNT_PAYMENT
        if receipt_type == consts.TYPE_PAYMENT
        else consts.EASY_COUNT_REFUND
    )
    easy_count.check_request(
        customer_name=ISRAEL_USER_NAME,
        developer_email=consts.DEVELOPER_EMAIL,
        items=EASY_COUNT_ITEMS,
        payment=payment,
        price_total=payment.payment_sum,
        idempotency_token=consts.EXTERNAL_PAYMENT_ID + receipt_data_type,
        invoice_type=invoice_type,
        is_payment=receipt_type == consts.TYPE_PAYMENT,
        user_uuid=consts.GROCERY_USER_UUID,
        document_vat=vat,
    )
    await _run_stq(
        receipt_type=receipt_type,
        country=models.Country.Israel.name,
        payment_method=payment_method,
        expect_fail=False,
    )
    assert easy_count.times_called() == 1
    assert cardstorage.times_card_called() == 1


@pytest_marks.MARK_NOW
@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.DEVELOPER_EMAIL_MARK
@pytest_marks.GROCERY_USER_UUID_MARK
@pytest.mark.parametrize(
    'system,easy_type',
    [
        ('VISA', 2),
        ('mastercard', 99),
        ('MasterCard', 99),
        ('DinersClubCarteBlanche', 3),
        ('AmericanExpress', 4),
        ('xxx-123', 0),  # unknown
    ],
)
async def test_system(
        taxi_grocery_invoices,
        grocery_orders,
        grocery_cart,
        personal,
        cardstorage,
        easy_count,
        default_isr_receipt,
        _run_stq,
        system,
        easy_type,
):
    cardstorage.set_system(system=system)

    receipt_type = models.ReceiptType.payment.value
    payment_type = models.PaymentType.card.value
    payment_method = {'type': payment_type, 'id': 'payment-id'}

    # no http calls to service in test, so explicit call is required
    await taxi_grocery_invoices.invalidate_caches()

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)

    vat = CART_ITEMS_ISR[0].vat
    payment = easy_count.get_easy_count_payment(
        total_price=RECEIPT_TOTAL,
        payment_type=payment_type,
        cc_type=easy_type,
    )
    invoice_type = (
        consts.EASY_COUNT_PAYMENT
        if receipt_type == consts.TYPE_PAYMENT
        else consts.EASY_COUNT_REFUND
    )
    easy_count.check_request(
        customer_name=ISRAEL_USER_NAME,
        developer_email=consts.DEVELOPER_EMAIL,
        items=EASY_COUNT_ITEMS,
        payment=payment,
        price_total=payment.payment_sum,
        invoice_type=invoice_type,
        is_payment=receipt_type == consts.TYPE_PAYMENT,
        user_uuid=consts.GROCERY_USER_UUID,
        document_vat=vat,
    )
    await _run_stq(
        receipt_type=receipt_type,
        country=models.Country.Israel.name,
        payment_method=payment_method,
        expect_fail=False,
    )

    assert easy_count.times_called() == 1
    assert cardstorage.times_card_called() == 1


@pytest.mark.parametrize(
    'title, title_cut',
    [('я' * 500, 'я' * 125 + '...'), ('q' * 500, 'q' * 125 + '...')],
)
async def test_eats_receipts_long_title(
        grocery_invoices_configs,
        grocery_orders,
        grocery_cart,
        check_eats_receipt_create,
        _run_stq,
        title,
        title_cut,
):
    receipt_data_type = 'order'

    eats_receipts_service = 'eats_receipts'

    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    cart_item = helpers.make_cart_item(
        'item-id-1', price=10, quantity=1, vat=consts.RUSSIA_VAT,
    )
    cart_item.title = title

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2([cart_item])

    receipt_item = helpers.make_receipt_item(
        'item-id-1_0', price=10, quantity=1,
    )

    products = [
        {
            'id': receipt_item.item_id,
            'parent': None,
            'price': receipt_item.price,
            'supplier_inn': grocery_orders.order['depot']['tin'],
            'tax': consts.RUSSIA_VAT,
            'title': title_cut,
        },
    ]

    check_eats_receipt_create(
        service=eats_receipts_service,
        receipt_data_type=receipt_data_type,
        products=products,
    )

    await _run_stq(items=[receipt_item])


@pytest_marks.EATS_RECEIPTS_SERVICES
async def test_pg_tasks_polling_id_success(
        grocery_invoices_db,
        grocery_invoices_configs,
        grocery_orders,
        grocery_cart,
        _run_stq,
        eats_receipts_service,
):
    receipt_data_type = 'order'

    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_RUS)

    await _run_stq(items=RECEIPT_PRODUCT_ITEMS)

    db_tasks = grocery_invoices_db.load_all_tasks()

    assert len(db_tasks) == 1

    db_task = db_tasks[0]

    receipt_source = eats_receipts_helpers.eats_receipts_stq_source(
        eats_receipts_service,
    )

    polling_task_id = helpers.make_polling_task_id(
        consts.EXTERNAL_PAYMENT_ID, receipt_data_type, receipt_source,
    )

    assert db_task == models.Task(
        task_id=consts.TASK_ID,
        task_type='invoice_callback',
        order_id=consts.ORDER_ID,
        status='success',
        args={
            'items': models.items_to_json(RECEIPT_PRODUCT_ITEMS),
            'country': COUNTRY.name,
            'order_id': consts.ORDER_ID,
            'terminal_id': consts.TERMINAL_ID,
            'operation_id': consts.OPERATION_ID,
            'receipt_type': consts.TYPE_PAYMENT,
            'payment_method': consts.DEFAULT_PAYMENT_METHOD,
            'payment_finished': consts.PAYMENT_FINISHED,
            'receipt_data_type': receipt_data_type,
            'external_payment_id': consts.EXTERNAL_PAYMENT_ID,
        },
        result_payload={
            'polling_id': f'{consts.EXTERNAL_PAYMENT_ID}-{receipt_data_type}',
            'polling_task_id': polling_task_id,
        },
        params={
            'source': eats_receipts_helpers.eats_receipts_stq_source(
                eats_receipts_service,
            ),
            'country_iso3': COUNTRY.country_iso3,
            'exec_tries': 1,
        },
    )


async def test_pg_tasks_upsert(
        grocery_invoices_db,
        grocery_invoices_configs,
        grocery_orders,
        grocery_cart,
        _run_stq,
):
    receipt_data_type = 'order'
    eats_receipts_service = consts.EATS_RECEIPTS

    grocery_invoices_configs.eats_receipts_service(eats_receipts_service)

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_RUS)

    args = {
        'items': models.items_to_json(RECEIPT_PRODUCT_ITEMS),
        'country': COUNTRY.name,
        'order_id': consts.ORDER_ID,
        'terminal_id': consts.TERMINAL_ID,
        'operation_id': consts.OPERATION_ID,
        'receipt_type': consts.TYPE_PAYMENT,
        'payment_method': consts.DEFAULT_PAYMENT_METHOD,
        'payment_finished': consts.PAYMENT_FINISHED,
        'receipt_data_type': receipt_data_type,
        'external_payment_id': consts.EXTERNAL_PAYMENT_ID,
    }

    receipt_source = eats_receipts_helpers.eats_receipts_stq_source(
        eats_receipts_service,
    )

    task = models.Task(
        task_id=consts.TASK_ID,
        task_type='invoice_callback',
        order_id=consts.ORDER_ID,
        status='failed',
        args=args,
        result_payload=None,
        params={
            'source': receipt_source,
            'country_iso3': models.Country.France.country_iso3,
            'exec_tries': 1,
        },
    )

    grocery_invoices_db.insert_task(task)

    await _run_stq(items=RECEIPT_PRODUCT_ITEMS)

    db_tasks = grocery_invoices_db.load_all_tasks()

    assert len(db_tasks) == 1

    db_task = db_tasks[0]

    polling_task_id = helpers.make_polling_task_id(
        consts.EXTERNAL_PAYMENT_ID, receipt_data_type, receipt_source,
    )

    assert db_task == models.Task(
        task_id=consts.TASK_ID,
        task_type='invoice_callback',
        order_id=consts.ORDER_ID,
        status='success',
        args=args,
        result_payload={
            'polling_id': f'{consts.EXTERNAL_PAYMENT_ID}-{receipt_data_type}',
            'polling_task_id': polling_task_id,
        },
        params={
            'source': receipt_source,
            'country_iso3': COUNTRY.country_iso3,
            'exec_tries': 1,
        },
    )


@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.DEVELOPER_EMAIL_MARK
@pytest_marks.GROCERY_USER_UUID_MARK
async def test_pg_tasks_receipt_url_success(
        taxi_grocery_invoices,
        grocery_invoices_configs,
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        cardstorage,
        easy_count,
        default_isr_receipt,
        _run_stq,
):
    receipt_type = 'payment'
    payment_type = 'card'
    payment_method = {'type': payment_type, 'id': 'payment-id'}

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)

    await _run_stq(
        receipt_type=receipt_type,
        country=models.Country.Israel.name,
        payment_method=payment_method,
    )

    db_tasks = grocery_invoices_db.load_all_tasks()

    assert len(db_tasks) == 1

    db_task = db_tasks[0]

    assert db_task.params['receipt_id'] == consts.EASY_COUNT_DOC_NUMBER
    assert db_task.result_payload == {'receipt_url': consts.EASY_COUNT_LINK}


@pytest_marks.MARK_NOW
async def test_pg_tasks_in_process(
        grocery_invoices_db,
        taxi_grocery_invoices,
        grocery_orders,
        grocery_cart,
        _run_stq,
):
    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)

    await _run_stq(
        country=models.Country.Israel.name,
        receipt_type='payment',
        receipt_data_type='tips',
    )

    db_tasks = grocery_invoices_db.load_all_tasks()

    assert len(db_tasks) == 1

    db_task = db_tasks[0]

    assert db_task.status == 'in_process'


async def test_pg_tasks_failed(
        taxi_grocery_invoices,
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        cardstorage,
        _run_stq,
):
    receipt_type = models.ReceiptType.payment.value
    payment_type = models.PaymentType.card.value
    payment_method = {'type': payment_type, 'id': 'payment-id'}

    # no http calls to service in test, so explicit call is required
    await taxi_grocery_invoices.invalidate_caches()

    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)
    await _run_stq(
        receipt_type=receipt_type,
        country=models.Country.Israel.name,
        payment_method=payment_method,
        expect_fail=True,
    )

    db_tasks = grocery_invoices_db.load_all_tasks()

    assert len(db_tasks) == 1

    db_task = db_tasks[0]

    assert db_task.status == 'failed'
    assert db_task.params['error_code'] == 'no_title_in_tanker'


@pytest_marks.TRANSLATIONS_MARK
@pytest_marks.MARK_NOW
@configs.GROCERY_RECEIPTS_POLLING_POLICY
async def test_not_ready_policy_expired(
        grocery_invoices_db,
        grocery_orders,
        grocery_cart,
        easy_count,
        _run_stq,
):
    grocery_cart.set_cart_data(cart_id=consts.CART_ID)
    grocery_cart.set_items_v2(CART_ITEMS_ISR)
    grocery_orders.order.update(status='delivering')

    await _run_stq(
        country=models.Country.Israel.name,
        receipt_type='refund',
        receipt_data_type='order',
        task_created=TWO_DAYS_AGO,
        expect_fail=True,
    )

    db_tasks = grocery_invoices_db.load_all_tasks()

    assert len(db_tasks) == 1

    db_task = db_tasks[0]

    assert db_task.status == 'failed'
    assert db_task.params['error_code'] == 'task_deadline::stq_callback'
