# pylint: disable=import-error
import copy
import decimal

from grocery_mocks.utils import helpers as mock_helpers
import pytest

from . import consts
from . import helpers
from . import models
from . import pytest_marks
from . import receipt_items


# pylint: disable=invalid-name
Decimal = decimal.Decimal

COUNTRY = models.Country.Russia

CREATE_OPERATION_ID = 'create:123'
UPDATE_OPERATION_ID = 'update:234'
REFUND_OPERATION_ID = 'refund:456'
CANCEL_OPERATION_ID = 'cancel:999'

PaymentType = models.PaymentType

PAYMENT_METHOD = models.PaymentMethod(PaymentType.card, consts.CARD_ID)

OPERATION_SUM = models.OperationSum(
    items=[
        models.Item(item_id='333', price='500', quantity='1'),
        models.Item(
            item_id='444',
            price='100',
            quantity='2',
            item_type=models.ItemType.delivery,
        ),
    ],
    payment_type=PAYMENT_METHOD.payment_type,
)

EXTERNAL_PAYMENT_ID = 'transaction_id'
CLEAR_SUCCESS = 'clear_success'
TERMINAL_ID = '12312312321'


@pytest.fixture
def _run_stq(run_transactions_callback):
    async def _do(
            operation_id=CREATE_OPERATION_ID,
            notification_type=consts.TRANSACTION_CLEAR,
            operation_status='done',
            payment_type=PAYMENT_METHOD.payment_type,
            status=CLEAR_SUCCESS,
            **kwargs,
    ):
        await run_transactions_callback(
            operation_id=operation_id,
            notification_type=notification_type,
            operation_status=operation_status,
            transactions=[
                {
                    'external_payment_id': EXTERNAL_PAYMENT_ID,
                    'payment_type': payment_type.value,
                    'status': status,
                },
            ],
            **kwargs,
        )

    return _do


@pytest_marks.INVOICE_ORIGINATORS
@pytest_marks.PAYMENT_TYPES
async def test_basic(
        grocery_orders,
        transactions,
        check_grocery_invoices_stq_event,
        _run_stq,
        originator,
        payment_type,
):
    cleared = '2012-02-10T11:51:12.607+00:00'
    payment_method = models.PaymentMethod(payment_type, consts.PAYMENT_ID)

    transactions.retrieve.mock_response(
        operations=[
            helpers.make_operation(
                id=CREATE_OPERATION_ID, sum_to_pay=[OPERATION_SUM.to_object()],
            ),
        ],
        status='cleared',
        transactions=[
            helpers.make_transaction(
                cleared=cleared,
                operation_id=CREATE_OPERATION_ID,
                payment_type=payment_method.payment_type.value,
                payment_method_id=payment_method.payment_id,
                status=CLEAR_SUCCESS,
                sum=OPERATION_SUM.to_transaction_sum(),
                external_payment_id=EXTERNAL_PAYMENT_ID,
                terminal_id=TERMINAL_ID,
            ),
        ],
    )

    await _run_stq(
        originator=originator, payment_type=payment_method.payment_type,
    )

    event_id = helpers.get_stq_event_id(
        operation_id=CREATE_OPERATION_ID,
        payment_id=EXTERNAL_PAYMENT_ID,
        invoice_originator=originator,
    )
    check_grocery_invoices_stq_event(
        stq_event_id=event_id,
        info=dict(
            country=COUNTRY.name,
            external_payment_id=EXTERNAL_PAYMENT_ID,
            operation_id=CREATE_OPERATION_ID,
            order_id=consts.ORDER_ID,
            receipt_type='payment',
            terminal_id=TERMINAL_ID,
            items=models.to_invoices_callback_items(OPERATION_SUM.items),
            payment_method=payment_method.to_request(),
            receipt_data_type=originator.receipt_data_type,
            payment_finished=cleared,
        ),
    )


async def test_skip_zero_items(
        grocery_orders,
        transactions,
        check_grocery_invoices_stq_event,
        _run_stq,
):
    item_to_remove = '333'
    transaction_sum = OPERATION_SUM.to_transaction_sum()
    transaction_sum[0]['amount'] = '0'
    assert transaction_sum[0]['item_id'] == models.Item.sub_item_id(
        item_to_remove, 0,
    )

    transactions.retrieve.mock_response(
        operations=[
            helpers.make_operation(
                id=CREATE_OPERATION_ID, sum_to_pay=[OPERATION_SUM.to_object()],
            ),
        ],
        status='cleared',
        transactions=[
            helpers.make_transaction(
                status=CLEAR_SUCCESS,
                sum=transaction_sum,
                external_payment_id=EXTERNAL_PAYMENT_ID,
            ),
        ],
    )

    await _run_stq()

    operation_sum_without_item = copy.deepcopy(OPERATION_SUM)
    operation_sum_without_item.remove_item(item_id=item_to_remove)

    check_grocery_invoices_stq_event(
        info=mock_helpers.sub_dict(
            items=models.to_invoices_callback_items(
                operation_sum_without_item.items,
            ),
        ),
    )


async def test_several_hold_operations(
        grocery_orders,
        transactions,
        check_grocery_invoices_stq_event,
        _run_stq,
):
    create_sum_items = [
        models.Item(price='500', quantity='1', item_id='333'),
        models.Item(price='100', quantity='2', item_id='444'),
        models.Item(price='500', quantity='1', item_id='555'),
    ]

    removed_item_before_clear = '444'
    refunded_item = '555'

    create_sum = copy.deepcopy(OPERATION_SUM)
    create_sum.items = create_sum_items

    update_sum = copy.deepcopy(create_sum)
    update_sum.remove_item(item_id=removed_item_before_clear)
    refunded_sum = copy.deepcopy(update_sum)
    refunded_sum.remove_item(item_id=refunded_item)

    # Sum does not touch after clear happened, so in sum will
    # items after update.
    transaction_sum = update_sum.to_transaction_sum()

    transactions.retrieve.mock_response(
        operations=[
            helpers.make_operation(
                id=CREATE_OPERATION_ID, sum_to_pay=[create_sum.to_object()],
            ),
            helpers.make_operation(
                id=UPDATE_OPERATION_ID, sum_to_pay=[update_sum.to_object()],
            ),
            helpers.make_operation(
                id=REFUND_OPERATION_ID, sum_to_pay=[refunded_sum.to_object()],
            ),
        ],
        status='cleared',
        transactions=[
            helpers.make_transaction(
                status=CLEAR_SUCCESS,
                sum=transaction_sum,
                external_payment_id=EXTERNAL_PAYMENT_ID,
            ),
        ],
    )

    await _run_stq()

    check_grocery_invoices_stq_event(
        info=mock_helpers.sub_dict(
            items=models.to_invoices_callback_items(update_sum.items),
        ),
    )


async def test_several_payment_types(
        grocery_orders,
        transactions,
        check_grocery_invoices_stq_event,
        _run_stq,
):
    cashback_operation = copy.deepcopy(OPERATION_SUM)
    cashback_operation.payment_type = PaymentType.personal_wallet
    for item in cashback_operation.items:
        item.price = '1'

    cashback_transaction_sum = cashback_operation.to_transaction_sum()
    transaction_sum = OPERATION_SUM.to_transaction_sum()

    cashback_external_payment_id = f'cashback-{EXTERNAL_PAYMENT_ID}'

    transactions.retrieve.mock_response(
        operations=[
            helpers.make_operation(
                id=CREATE_OPERATION_ID,
                sum_to_pay=[
                    cashback_operation.to_object(),
                    OPERATION_SUM.to_object(),
                ],
            ),
        ],
        status='cleared',
        transactions=[
            helpers.make_transaction(
                status=CLEAR_SUCCESS,
                sum=transaction_sum,
                external_payment_id=EXTERNAL_PAYMENT_ID,
            ),
            helpers.make_transaction(
                status=CLEAR_SUCCESS,
                sum=cashback_transaction_sum,
                external_payment_id=cashback_external_payment_id,
                payment_type=PaymentType.personal_wallet.value,
                payment_method_id=consts.PERSONAL_WALLET_ID,
            ),
        ],
    )

    await _run_stq()

    check_grocery_invoices_stq_event(
        info=mock_helpers.sub_dict(
            items=models.to_invoices_callback_items(OPERATION_SUM.items),
        ),
    )


async def test_cancel(
        grocery_orders,
        transactions,
        check_grocery_invoices_stq_event,
        _run_stq,
):
    canceled_operation_sum = copy.deepcopy(OPERATION_SUM)
    canceled_operation_sum.clear()

    transactions.retrieve.mock_response(
        operations=[
            helpers.make_operation(
                id=CREATE_OPERATION_ID, sum_to_pay=[OPERATION_SUM.to_object()],
            ),
            helpers.make_operation(id=CANCEL_OPERATION_ID, sum_to_pay=[]),
        ],
        status='cleared',
        transactions=[
            helpers.make_transaction(
                status=CLEAR_SUCCESS,
                sum=canceled_operation_sum.to_transaction_sum(),
                external_payment_id=EXTERNAL_PAYMENT_ID,
            ),
        ],
    )

    await _run_stq()

    check_grocery_invoices_stq_event(times_called=0)


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
        transactions,
        check_grocery_invoices_stq_event,
        _run_stq,
        receipts,
):
    grocery_payments_configs.set_receipt_division(list(receipts.keys()))

    # remove receipts without items
    receipts = {k: v for k, v in receipts.items() if len(v) != 0}

    all_items = helpers.flatten(receipts.values())

    operation_sum = models.OperationSum(
        items=all_items, payment_type=PAYMENT_METHOD.payment_type,
    )

    transaction_items = {
        receipt_type: models.to_invoices_callback_items(values)
        for receipt_type, values in receipts.items()
    }

    transaction_sum = operation_sum.to_transaction_sum()

    transactions.retrieve.mock_response(
        operations=[
            helpers.make_operation(
                id=CREATE_OPERATION_ID, sum_to_pay=[operation_sum.to_object()],
            ),
        ],
        status='cleared',
        transactions=[
            helpers.make_transaction(
                operation_id=CREATE_OPERATION_ID,
                payment_type=PAYMENT_METHOD.payment_type.value,
                payment_method_id=PAYMENT_METHOD.payment_id,
                status=CLEAR_SUCCESS,
                sum=transaction_sum,
                external_payment_id=EXTERNAL_PAYMENT_ID,
                terminal_id=TERMINAL_ID,
            ),
        ],
    )

    await _run_stq()

    # events checked in reverse order
    reverse_range = range(len(receipts), 0, -1)

    for (times_called, receipt_type) in zip(reverse_range, receipts):
        event_id = helpers.get_stq_event_id(
            operation_id=CREATE_OPERATION_ID,
            payment_id=EXTERNAL_PAYMENT_ID,
            receipt_data_type=receipt_type,
        )

        check_grocery_invoices_stq_event(
            times_called=times_called,
            stq_event_id=event_id,
            info=dict(
                country=COUNTRY.name,
                external_payment_id=EXTERNAL_PAYMENT_ID,
                items=transaction_items[receipt_type],
                operation_id=CREATE_OPERATION_ID,
                order_id=consts.ORDER_ID,
                payment_method=PAYMENT_METHOD.to_request(),
                receipt_type='payment',
                terminal_id=TERMINAL_ID,
                receipt_data_type=receipt_type,
            ),
        )


async def test_receipt_division_exp(
        grocery_orders, experiments3, transactions, _run_stq,
):
    country = 'Israel'
    country_iso3 = 'ISR'
    grocery_flow_version = 'exchange_currency'

    grocery_orders.order.update(
        country=country,
        country_iso3=country_iso3,
        grocery_flow_version=grocery_flow_version,
    )

    exp3_recorder = experiments3.record_match_tries(
        'grocery_receipt_division_settings',
    )

    transactions.retrieve.mock_response(
        status='cleared',
        transactions=[
            helpers.make_transaction(external_payment_id=EXTERNAL_PAYMENT_ID),
        ],
    )

    await _run_stq()

    exp3_matches = await exp3_recorder.get_match_tries(1)
    exp3_kwargs = exp3_matches[0].kwargs

    assert exp3_kwargs['country_iso3'] == country_iso3
    assert exp3_kwargs['grocery_flow_version'] == grocery_flow_version


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
    item_to_refund = '333'
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
            helpers.make_transaction(
                operation_id=UPDATE_OPERATION_ID,
                payment_type=payment_method.payment_type.value,
                payment_method_id=payment_method.payment_id,
                status=CLEAR_SUCCESS,
                sum=update_operation_sum.to_transaction_sum(),
                external_payment_id=EXTERNAL_PAYMENT_ID,
                terminal_id=TERMINAL_ID,
                refunds=[],
            ),
        ],
        payment_types=[payment_method.payment_type.value],
    )

    await _run_stq(operation_id=UPDATE_OPERATION_ID)

    check_grocery_invoices_stq_event(
        info=dict(
            country=COUNTRY.name,
            external_payment_id=EXTERNAL_PAYMENT_ID,
            items=models.to_invoices_callback_items(
                update_operation_sum.items,
            ),
            operation_id=UPDATE_OPERATION_ID,
            order_id=consts.ORDER_ID,
            payment_method=payment_method.to_request(),
            receipt_type='payment',
            terminal_id=TERMINAL_ID,
            receipt_data_type='order',
        ),
    )
