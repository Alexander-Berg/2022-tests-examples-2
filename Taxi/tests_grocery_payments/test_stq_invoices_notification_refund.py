# pylint: disable=import-error
import copy

from grocery_mocks.utils import helpers as mock_helpers
import pytest

from . import consts
from . import helpers
from . import models
from . import pytest_marks
from . import receipt_items


PaymentType = models.PaymentType

CREATE_OPERATION_ID = 'create:123'
UPDATE_OPERATION_ID = 'update:234'
REFUND_OPERATION_ID = 'refund:456'
CANCEL_OPERATION_ID = 'cancel:999'
APPEND_OPERATION_ID = 'append:345'
REMOVE_OPERATION_ID = 'remove:567'

COUNTRY = models.Country.Russia

PAYMENT_METHOD = models.PaymentMethod(PaymentType.card, consts.CARD_ID)

ITEM_333_ID = '333'
ITEM_333_PRICE = '500'
ITEM_333_QUANTITY = '1'

OPERATION_SUM = models.OperationSum(
    items=[
        models.Item(
            item_id=ITEM_333_ID,
            price=ITEM_333_PRICE,
            quantity=ITEM_333_QUANTITY,
        ),
        models.Item(
            item_id='444',
            price='100',
            quantity='10',
            item_type=models.ItemType.delivery,
        ),
    ],
    payment_type=PAYMENT_METHOD.payment_type,
)

TRANSACTION_SUM = [
    {'amount': '200', 'item_id': '444'},
    {'amount': ITEM_333_PRICE, 'item_id': ITEM_333_ID},
]

EXTERNAL_PAYMENT_ID = consts.EXTERNAL_PAYMENT_ID
CLEAR_SUCCESS = 'clear_success'
TERMINAL_ID = consts.TERMINAL_ID

REFUND_EXTERNAL_PAYMENT_ID = consts.REFUND_EXTERNAL_PAYMENT_ID

REFUNDED = '2010-02-10T12:31:24.123+00:00'


@pytest.fixture
def _prerare_invoice_with_refund(grocery_orders, transactions):
    def _prepare(
            item_to_refund,
            refund_quantity=None,
            refund_status=consts.REFUND_SUCCESS,
            payment_method=PAYMENT_METHOD,
            operation_sum=OPERATION_SUM,
            refund_operation_id=REFUND_OPERATION_ID,
    ):
        create_operation_sum = copy.deepcopy(operation_sum)
        create_operation_sum.payment_type = payment_method.payment_type
        refund_operation_sum = copy.deepcopy(create_operation_sum)

        refunded_operation_sum = refund_operation_sum.remove_item(
            item_id=item_to_refund, quantity=refund_quantity,
        )

        refund = helpers.make_refund(
            operation_id=refund_operation_id,
            status=refund_status,
            sum=refunded_operation_sum.to_transaction_sum(),
            refunded=REFUNDED,
        )

        transactions.retrieve.mock_response(
            operations=[
                helpers.make_operation(
                    id=CREATE_OPERATION_ID,
                    sum_to_pay=[create_operation_sum.to_object()],
                ),
                helpers.make_operation(
                    id=refund_operation_id,
                    sum_to_pay=[refund_operation_sum.to_object()],
                ),
            ],
            status='cleared',
            transactions=[
                helpers.make_transaction(
                    operation_id=CREATE_OPERATION_ID,
                    payment_type=payment_method.payment_type.value,
                    payment_method_id=payment_method.payment_id,
                    status=CLEAR_SUCCESS,
                    sum=create_operation_sum.to_transaction_sum(),
                    refunds=[refund],
                ),
            ],
            payment_types=[payment_method.payment_type.value],
        )

    return _prepare


@pytest.fixture
def _run_stq(run_transactions_callback):
    async def _do(
            operation_id=REFUND_OPERATION_ID,
            notification_type=consts.OPERATION_FINISH,
            operation_status='done',
            transactions=None,
            **kwargs,
    ):
        await run_transactions_callback(
            operation_id=operation_id,
            notification_type=notification_type,
            operation_status=operation_status,
            transactions=transactions or [],
            **kwargs,
        )

    return _do


@pytest_marks.INVOICE_ORIGINATORS
@pytest.mark.parametrize(
    'operation_id',
    [
        UPDATE_OPERATION_ID,
        REFUND_OPERATION_ID,
        APPEND_OPERATION_ID,
        REMOVE_OPERATION_ID,
    ],
)
async def test_basic(
        check_grocery_invoices_stq_event,
        _prerare_invoice_with_refund,
        _run_stq,
        originator,
        operation_id,
):
    payment_method = models.PaymentMethod(PaymentType.card, consts.PAYMENT_ID)

    item_to_refund = ITEM_333_ID
    refund_quantity = ITEM_333_QUANTITY

    _prerare_invoice_with_refund(
        item_to_refund=item_to_refund,
        refund_quantity=refund_quantity,
        payment_method=payment_method,
        refund_operation_id=operation_id,
    )

    await _run_stq(originator=originator, operation_id=operation_id)

    refund_item_price = OPERATION_SUM.get(item_to_refund).price

    items = models.to_invoices_callback_items(
        [models.Item(item_to_refund, refund_item_price, refund_quantity)],
    )
    event_id = helpers.get_stq_event_id(
        operation_id=operation_id,
        payment_id=REFUND_EXTERNAL_PAYMENT_ID,
        invoice_originator=originator,
    )

    check_grocery_invoices_stq_event(
        stq_event_id=event_id,
        info=dict(
            country=COUNTRY.name,
            external_payment_id=REFUND_EXTERNAL_PAYMENT_ID,
            items=items,
            operation_id=operation_id,
            order_id=consts.ORDER_ID,
            payment_method=payment_method.to_request(),
            receipt_type='refund',
            terminal_id=TERMINAL_ID,
            receipt_data_type=originator.receipt_data_type,
            payment_finished=REFUNDED,
        ),
    )


@pytest.mark.parametrize(
    'refund_status, times_called',
    [(consts.REFUND_SUCCESS, 1), (consts.REFUND_FAILED, 0)],
)
async def test_failed_refund(
        check_grocery_invoices_stq_event,
        _prerare_invoice_with_refund,
        _run_stq,
        refund_status,
        times_called,
):
    _prerare_invoice_with_refund(
        item_to_refund=ITEM_333_ID, refund_status=refund_status,
    )

    await _run_stq()

    check_grocery_invoices_stq_event(times_called=times_called)


async def test_several_hold_operations(
        grocery_orders,
        transactions,
        check_grocery_invoices_stq_event,
        _prerare_invoice_with_refund,
        _run_stq,
):
    item_to_refund = ITEM_333_ID
    refund_quantity = '5'
    new_item_price = '123'

    create_operation_sum = copy.deepcopy(OPERATION_SUM)
    update_operation_sum = copy.deepcopy(create_operation_sum)

    assert update_operation_sum.get(item_to_refund).price != new_item_price
    update_operation_sum.items[0].price = new_item_price

    refund_operation_sum = copy.deepcopy(update_operation_sum)
    refunded_operation_sum = refund_operation_sum.remove_item(
        item_id=item_to_refund, quantity=refund_quantity,
    )

    refund = helpers.make_refund(
        operation_id=REFUND_OPERATION_ID,
        sum=refunded_operation_sum.to_transaction_sum(),
    )

    transactions.retrieve.mock_response(
        operations=[
            helpers.make_operation(
                id=CREATE_OPERATION_ID,
                sum_to_pay=[create_operation_sum.to_object()],
            ),
            helpers.make_operation(
                id=UPDATE_OPERATION_ID,
                sum_to_pay=[update_operation_sum.to_object()],
            ),
            helpers.make_operation(
                id=REFUND_OPERATION_ID,
                sum_to_pay=[refund_operation_sum.to_object()],
            ),
        ],
        status='cleared',
        transactions=[
            helpers.make_transaction(
                operation_id=CREATE_OPERATION_ID,
                payment_type=PAYMENT_METHOD.payment_type.value,
                payment_method_id=PAYMENT_METHOD.payment_id,
                status=CLEAR_SUCCESS,
                sum=update_operation_sum.to_transaction_sum(),
                refunds=[refund],
            ),
        ],
    )

    await _run_stq()

    check_grocery_invoices_stq_event(
        info=mock_helpers.sub_dict(
            items=models.to_invoices_callback_items(
                [models.Item(item_to_refund, new_item_price, refund_quantity)],
            ),
        ),
    )


@pytest.mark.parametrize('zero_price', [True, False])
@pytest.mark.parametrize('zero_quantity', [True, False])
async def test_skip_zero_items(
        grocery_orders,
        transactions,
        check_grocery_invoices_stq_event,
        _prerare_invoice_with_refund,
        _run_stq,
        zero_price,
        zero_quantity,
):
    create_operation_sum = copy.deepcopy(OPERATION_SUM)

    item_to_refund = ITEM_333_ID

    refund_quantity = '1'
    if zero_quantity:
        refund_quantity = '0'

    refund_item_price = create_operation_sum.get(item_to_refund).price
    if zero_price:
        refund_item_price = '0'

    refund_operation_sum = copy.deepcopy(create_operation_sum)
    refunded_operation_sum = refund_operation_sum.remove_item(
        item_id=item_to_refund, quantity=refund_quantity,
    )

    assert refunded_operation_sum.items[0].item_id == item_to_refund
    refunded_operation_sum.items[0].price = refund_item_price

    refund = helpers.make_refund(
        operation_id=REFUND_OPERATION_ID,
        sum=refunded_operation_sum.to_transaction_sum(),
    )

    transactions.retrieve.mock_response(
        operations=[
            helpers.make_operation(
                id=CREATE_OPERATION_ID,
                sum_to_pay=[create_operation_sum.to_object()],
            ),
            helpers.make_operation(
                id=REFUND_OPERATION_ID,
                sum_to_pay=[refund_operation_sum.to_object()],
            ),
        ],
        status='cleared',
        transactions=[
            helpers.make_transaction(
                operation_id=CREATE_OPERATION_ID,
                payment_type=PAYMENT_METHOD.payment_type.value,
                payment_method_id=PAYMENT_METHOD.payment_id,
                status=CLEAR_SUCCESS,
                sum=create_operation_sum.to_transaction_sum(),
                refunds=[refund],
            ),
        ],
    )

    await _run_stq()

    if zero_price or zero_quantity:
        check_grocery_invoices_stq_event(times_called=0)
    else:
        check_grocery_invoices_stq_event(times_called=1)


@pytest.mark.parametrize(
    'receipts',
    [
        receipt_items.ALL_RECEIPTS,
        receipt_items.ORDER_AND_TIPS_RECEIPTS,
        receipt_items.ORDER_RECEIPT,
        receipt_items.MISSING_DELIVERY_RECEIPT,
    ],
)
async def test_receipt_division(
        grocery_payments_configs,
        grocery_orders,
        check_grocery_invoices_stq_event,
        transactions,
        _prerare_invoice_with_refund,
        _run_stq,
        receipts,
):
    grocery_payments_configs.set_receipt_division(list(receipts.keys()))

    # remove receipts without items
    receipts = {k: v for k, v in receipts.items() if len(v) != 0}

    all_items = helpers.flatten(receipts.values())

    create_operation_sum = models.OperationSum(
        items=all_items, payment_type=PAYMENT_METHOD.payment_type,
    )

    refund_operation_sum = create_operation_sum

    refunds = helpers.make_refund(
        operation_id=REFUND_OPERATION_ID,
        status=consts.REFUND_SUCCESS,
        sum=models.to_transaction_items(all_items),
        refunded=REFUNDED,
    )
    transactions.retrieve.mock_response(
        operations=[
            helpers.make_operation(
                id=CREATE_OPERATION_ID,
                sum_to_pay=[create_operation_sum.to_object()],
            ),
            helpers.make_operation(
                id=REFUND_OPERATION_ID,
                sum_to_pay=[refund_operation_sum.to_object()],
            ),
        ],
        status='cleared',
        transactions=[
            helpers.make_transaction(
                operation_id=CREATE_OPERATION_ID,
                payment_type=PAYMENT_METHOD.payment_type.value,
                payment_method_id=PAYMENT_METHOD.payment_id,
                status=CLEAR_SUCCESS,
                sum=create_operation_sum.to_transaction_sum(),
                refunds=[refunds],
            ),
        ],
    )

    await _run_stq()

    transaction_items = {
        receipt_type: models.to_invoices_callback_items(values)
        for receipt_type, values in receipts.items()
    }

    # events checked in reverse order
    reverse_range = range(len(receipts), 0, -1)

    for (times_called, receipt_type) in zip(reverse_range, receipts):
        event_id = helpers.get_stq_event_id(
            operation_id=REFUND_OPERATION_ID,
            payment_id=REFUND_EXTERNAL_PAYMENT_ID,
            receipt_data_type=receipt_type,
        )

        check_grocery_invoices_stq_event(
            times_called=times_called,
            stq_event_id=event_id,
            info=dict(
                country=COUNTRY.name,
                external_payment_id=REFUND_EXTERNAL_PAYMENT_ID,
                items=transaction_items[receipt_type],
                operation_id=REFUND_OPERATION_ID,
                order_id=consts.ORDER_ID,
                payment_method=PAYMENT_METHOD.to_request(),
                receipt_type='refund',
                terminal_id=TERMINAL_ID,
                receipt_data_type=receipt_type,
                payment_finished=REFUNDED,
            ),
        )


@pytest.mark.parametrize(
    'payment_type', [models.PaymentType.badge, models.PaymentType.corp],
)
async def test_badge_and_corp(
        grocery_orders,
        transactions,
        check_grocery_invoices_stq_event,
        _run_stq,
        payment_type,
):
    item_to_refund = ITEM_333_ID
    refund_quantity = '1'
    payment_method = models.PaymentMethod(payment_type, 'payment_method:id')

    create_operation_sum = copy.deepcopy(OPERATION_SUM)
    create_operation_sum.payment_type = payment_method.payment_type
    update_operation_sum = copy.deepcopy(create_operation_sum)

    update_operation_sum.remove_item(
        item_id=item_to_refund, quantity=refund_quantity,
    )

    refund = helpers.make_refund(
        operation_id=UPDATE_OPERATION_ID,
        status=consts.REFUND_SUCCESS,
        sum=create_operation_sum.to_transaction_sum(),
        refunded=REFUNDED,
    )

    transactions.retrieve.mock_response(
        operations=[
            helpers.make_operation(
                id=CREATE_OPERATION_ID,
                sum_to_pay=[create_operation_sum.to_object()],
            ),
            helpers.make_operation(
                id=UPDATE_OPERATION_ID,
                sum_to_pay=[update_operation_sum.to_object()],
            ),
        ],
        status='clearing',
        transactions=[
            helpers.make_transaction(
                operation_id=CREATE_OPERATION_ID,
                payment_type=payment_method.payment_type.value,
                payment_method_id=payment_method.payment_id,
                status=CLEAR_SUCCESS,
                sum=create_operation_sum.to_transaction_sum(),
                refunds=[refund],
            ),
            helpers.make_transaction(
                operation_id=UPDATE_OPERATION_ID,
                payment_type=payment_method.payment_type.value,
                payment_method_id=payment_method.payment_id,
                status=CLEAR_SUCCESS,
                sum=update_operation_sum.to_transaction_sum(),
                refunds=[],
            ),
        ],
        payment_types=[payment_method.payment_type.value],
    )

    await _run_stq(operation_id=UPDATE_OPERATION_ID)

    check_grocery_invoices_stq_event(
        times_called=1,
        info=dict(
            country=COUNTRY.name,
            external_payment_id=REFUND_EXTERNAL_PAYMENT_ID,
            items=models.to_invoices_callback_items(
                create_operation_sum.items,
            ),
            operation_id=UPDATE_OPERATION_ID,
            order_id=consts.ORDER_ID,
            payment_method=payment_method.to_request(),
            receipt_type='refund',
            terminal_id=TERMINAL_ID,
            receipt_data_type='order',
            payment_finished=REFUNDED,
        ),
    )


async def test_corp_refund(
        grocery_orders,
        transactions,
        check_grocery_invoices_stq_event,
        _run_stq,
):
    payment_type = models.PaymentType.corp
    refund_quantity = '1'
    payment_method = models.PaymentMethod(payment_type, 'payment_method:id')

    create_operation_sum = copy.deepcopy(OPERATION_SUM)
    create_operation_sum.payment_type = payment_method.payment_type
    refund_operation_sum = copy.deepcopy(create_operation_sum)

    refund_operation_sum.remove_item(
        item_id=ITEM_333_ID, quantity=refund_quantity,
    )

    transactions.retrieve.mock_response(
        operations=[
            helpers.make_operation(
                id=CREATE_OPERATION_ID,
                sum_to_pay=[create_operation_sum.to_object()],
            ),
            helpers.make_operation(
                id=REFUND_OPERATION_ID,
                sum_to_pay=[refund_operation_sum.to_object()],
            ),
        ],
        status='clearing',
        transactions=[
            helpers.make_transaction(
                operation_id=CREATE_OPERATION_ID,
                payment_type=payment_method.payment_type.value,
                payment_method_id=payment_method.payment_id,
                status=CLEAR_SUCCESS,
                sum=create_operation_sum.to_transaction_sum(),
                refunds=[],
                external_payment_id=consts.EXTERNAL_PAYMENT_ID,
            ),
            helpers.make_transaction(
                operation_id=REFUND_OPERATION_ID,
                payment_type=payment_method.payment_type.value,
                payment_method_id=payment_method.payment_id,
                status=CLEAR_SUCCESS,
                sum=[{'item_id': ITEM_333_ID, 'amount': '-' + ITEM_333_PRICE}],
                refunds=[],
                external_payment_id=consts.REFUND_EXTERNAL_PAYMENT_ID,
            ),
        ],
        payment_types=[payment_method.payment_type.value],
    )

    await _run_stq(
        operation_id=REFUND_OPERATION_ID,
        notification_type=consts.OPERATION_FINISH,
        transactions=[
            {
                'external_payment_id': consts.REFUND_EXTERNAL_PAYMENT_ID,
                'payment_type': 'corp',
                'status': 'clear_success',
            },
        ],
    )

    check_grocery_invoices_stq_event(
        times_called=1,
        info=dict(
            country=COUNTRY.name,
            external_payment_id=REFUND_EXTERNAL_PAYMENT_ID,
            items=[
                {
                    'item_id': ITEM_333_ID,
                    'item_type': 'product',
                    'price': ITEM_333_PRICE,
                    'quantity': '1',
                },
            ],
            operation_id=REFUND_OPERATION_ID,
            order_id=consts.ORDER_ID,
            payment_method=payment_method.to_request(),
            receipt_type='refund',
            terminal_id=TERMINAL_ID,
            receipt_data_type='order',
        ),
    )
