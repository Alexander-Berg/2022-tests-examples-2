# pylint: disable=E0401
from grocery_mocks.utils import helpers as mock_helpers
import pytest

from . import consts
from . import helpers
from . import models


COUNTRY = models.Country.Russia

PAYMENT_METHOD_CARD = models.PaymentMethod(
    models.PaymentType.card, consts.CARD_ID,
)

PAYMENT_METHOD_APPLEPAY = models.PaymentMethod(
    models.PaymentType.applepay, consts.PAYMENT_ID,
)

OPERATION_SUM_CARD = models.OperationSum(
    items=[models.Item(item_id='333', price='500', quantity='1')],
    payment_type=PAYMENT_METHOD_CARD.payment_type,
)
OPERATION_SUM_APPLEPAY = models.OperationSum(
    items=[models.Item(item_id='555', price='500', quantity='1')],
    payment_type=PAYMENT_METHOD_APPLEPAY.payment_type,
)

FIRST_OPERATION_ID = 'create:123'
LAST_OPERATION_ID = 'update:456'


@pytest.fixture(name='mock_retrieve')
def _mock_retrieve(transactions):
    def _inner(invoice_transactions, operation_status):
        operations = [
            helpers.make_operation(id=FIRST_OPERATION_ID),
            helpers.make_operation(
                id=LAST_OPERATION_ID,
                status=operation_status,
                sum_to_pay=[
                    OPERATION_SUM_CARD.to_object(),
                    OPERATION_SUM_APPLEPAY.to_object(),
                ],
            ),
        ]

        transactions.retrieve.mock_response(
            operations=operations, transactions=invoice_transactions,
        )

    return _inner


def _make_transaction(status, payment_type, operations_sum):
    return helpers.make_transaction(
        status=status,
        sum=operations_sum.to_transaction_sum(),
        external_payment_id=consts.EXTERNAL_PAYMENT_ID,
        payment_type=payment_type,
        payment_method_id='dummy',
        operation_id=LAST_OPERATION_ID,
    )


async def test_order_not_found_fails(
        grocery_orders, processing, run_transactions_callback,
):
    grocery_orders.orders.clear()
    await run_transactions_callback(
        invoice_id=consts.ORDER_ID, expect_fail=True,
    )

    assert processing.create_event.times_called == 0


@pytest.mark.parametrize(
    'notification_type', [consts.OPERATION_FINISH, consts.TRANSACTION_CLEAR],
)
async def test_pgsql(
        run_transactions_callback,
        grocery_payments_db,
        grocery_orders,
        transactions,
        notification_type,
):
    callback = models.TransactionsCallback(
        invoice_id=consts.ORDER_ID,
        operation_id='operation_id',
        notification_type=notification_type,
    )

    await run_transactions_callback(
        invoice_id=callback.invoice_id,
        operation_id=callback.operation_id,
        notification_type=callback.notification_type,
    )

    expected = notification_type == consts.OPERATION_FINISH
    assert grocery_payments_db.has_callback(callback) == expected


@pytest.mark.parametrize(
    'notification_type', [consts.OPERATION_FINISH, consts.TRANSACTION_CLEAR],
)
async def test_idempotency(
        run_transactions_callback,
        grocery_payments_db,
        grocery_orders,
        transactions,
        testpoint,
        notification_type,
):
    callback = models.TransactionsCallback(
        invoice_id=consts.ORDER_ID,
        operation_id='operation_id',
        notification_type=notification_type,
    )
    grocery_payments_db.upsert_callback(callback)

    @testpoint('transactions_callback_idempotency')
    def idempotency_testpoint(data):
        pass

    await run_transactions_callback(
        invoice_id=callback.invoice_id,
        operation_id=callback.operation_id,
        notification_type=callback.notification_type,
    )

    expected = notification_type == consts.OPERATION_FINISH
    assert idempotency_testpoint.times_called == int(expected)


@pytest.mark.parametrize(
    'notification_type', [consts.OPERATION_FINISH, consts.TRANSACTION_CLEAR],
)
@pytest.mark.parametrize('deferred_task_status', ['init', 'done', 'timeout'])
async def test_deferred_task(
        run_transactions_callback,
        grocery_payments_db,
        grocery_orders,
        transactions,
        notification_type,
        deferred_task_status,
):
    task = models.DeferredTask(
        consts.ORDER_ID, 'update:123', deferred_task_status,
    )

    update_body = dict(
        operation_id=task.task_id,
        id=task.invoice_id,
        items_by_payment_type=[],
        originator=consts.TRANSACTIONS_ORIGINATOR,
    )
    task.payload = dict(
        type='update',
        body=update_body,
        country_iso3=models.Country.Russia.country_iso3,
    )

    grocery_payments_db.upsert_deferred(task)

    transactions.update.check(**update_body)

    await run_transactions_callback(
        invoice_id=task.invoice_id,
        operation_id=task.task_id,
        notification_type=notification_type,
    )

    updated_task = grocery_payments_db.load_deferred(
        task.invoice_id, task.task_id,
    )
    assert updated_task is not None
    if notification_type == consts.TRANSACTION_CLEAR and task.status == 'init':
        assert updated_task.status == 'done'
        assert transactions.update.times_called == 1
    else:
        assert updated_task.status == task.status
        assert transactions.update.times_called == 0


@pytest.mark.parametrize(
    'notification_type', [consts.OPERATION_FINISH, consts.TRANSACTION_CLEAR],
)
async def test_deferred_task_none(
        run_transactions_callback,
        grocery_payments_db,
        grocery_orders,
        transactions,
        notification_type,
):
    invoice_id = consts.ORDER_ID
    operation_id = 'update:123'

    await run_transactions_callback(
        invoice_id=invoice_id,
        operation_id=operation_id,
        notification_type=notification_type,
    )

    assert grocery_payments_db.load_deferred(invoice_id, operation_id) is None
    assert transactions.update.times_called == 0


async def test_israel_dont_send_to_eats_billing(
        run_transactions_callback,
        grocery_orders,
        transactions,
        check_eats_billing_callback_event,
):
    grocery_orders.order.update(country_iso2='IL')

    await run_transactions_callback()

    check_eats_billing_callback_event(times_called=0)


async def test_skip_test_originator(
        run_transactions_callback,
        grocery_payments_db,
        grocery_orders,
        transactions,
        processing,
):
    grocery_orders.orders.clear()
    await run_transactions_callback(invoice_id='test:' + consts.ORDER_ID)

    assert transactions.retrieve.times_called == 0


@pytest.mark.parametrize(
    'operation_status, card_status, applepay_status',
    [
        (
            consts.OPERATION_DONE,
            {'transaction_status': 'hold_success', 'statistics': 'ok'},
            {'transaction_status': 'clear_success', 'statistics': 'ok'},
        ),
        (
            consts.OPERATION_FAILED,
            {'transaction_status': 'hold_fail', 'statistics': 'failed'},
            {'transaction_status': 'clear_success', 'statistics': 'ok'},
        ),
        (
            consts.OPERATION_FAILED,
            {'transaction_status': 'hold_fail', 'statistics': 'failed'},
            {'transaction_status': 'clear_fail', 'statistics': 'failed'},
        ),
    ],
)
async def test_statistics_oks_fails(
        taxi_grocery_payments,
        run_transactions_callback,
        grocery_orders,
        statistics,
        mock_retrieve,
        operation_status,
        card_status,
        applepay_status,
):
    mock_retrieve(
        operation_status=operation_status,
        invoice_transactions=[
            _make_transaction(
                status=card_status['transaction_status'],
                payment_type=str(PAYMENT_METHOD_CARD.payment_type.value),
                operations_sum=OPERATION_SUM_CARD,
            ),
            _make_transaction(
                status=applepay_status['transaction_status'],
                payment_type=str(PAYMENT_METHOD_APPLEPAY.payment_type.value),
                operations_sum=OPERATION_SUM_APPLEPAY,
            ),
        ],
    )

    async with statistics.capture(taxi_grocery_payments) as capture:
        await run_transactions_callback(
            invoice_id=consts.ORDER_ID, operation_id=LAST_OPERATION_ID,
        )

    card_statistics = card_status['statistics']
    applepay_statistics = applepay_status['statistics']

    mock_helpers.assert_dict_contains(
        capture.statistics,
        {
            (
                f'{PAYMENT_METHOD_CARD.payment_type.value}.'
                f'{COUNTRY.country_iso3.lower()}.'
                f'payment_timeout.{card_statistics}'
            ): 1,
            (
                f'{PAYMENT_METHOD_APPLEPAY.payment_type.value}.'
                f'{COUNTRY.country_iso3.lower()}.'
                f'payment_timeout.{applepay_statistics}'
            ): 1,
        },
    )
