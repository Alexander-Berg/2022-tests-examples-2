# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error,E0401

from grocery_mocks.utils import helpers as mock_helpers
from metrics_aggregations import helpers as metrics_helpers
import pytest

from . import consts
from . import helpers
from . import models
from . import pytest_marks

OPERATION_ID = 'create:123'

PAYMENT_METHOD = models.PaymentMethod(models.PaymentType.card, consts.CARD_ID)
PAYMENT_METHOD_WALLET = models.PaymentMethod(
    models.PaymentType.personal_wallet, consts.PERSONAL_WALLET_ID,
)

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
OPERATION_SUM_WALLET = models.OperationSum(
    items=[models.Item(item_id='555', price='500', quantity='1')],
    payment_type=PAYMENT_METHOD_WALLET.payment_type,
)

FIRST_OPERATION_ID = 'create:123'
LAST_OPERATION_ID = 'create:456'


def _mock_retrieve(
        transactions,
        *,
        operation_status=consts.OPERATION_FAILED,
        error_reason_code='error_reason_code',
        technical_error=None,
        operations=None,
        invoice_transactions=None,
        redirect_url=None,
):
    if operations is None:
        operations = [
            helpers.make_operation(id=FIRST_OPERATION_ID),
            helpers.make_operation(
                id=LAST_OPERATION_ID,
                status=operation_status,
                sum_to_pay=[
                    OPERATION_SUM.to_object(),
                    OPERATION_SUM_WALLET.to_object(),
                ],
            ),
        ]

    if invoice_transactions is None:
        hold_transaction = helpers.make_transaction(
            status='hold_pending',
            sum=OPERATION_SUM.to_transaction_sum(),
            external_payment_id=consts.EXTERNAL_PAYMENT_ID,
            payment_type=PAYMENT_METHOD.payment_type.value,
            payment_method_id=PAYMENT_METHOD.payment_id,
            error_reason_code=error_reason_code,
            technical_error=technical_error,
            operation_id=LAST_OPERATION_ID,
        )

        if redirect_url is not None:
            hold_transaction['3ds'] = {
                'redirect_url': redirect_url,
                'status': 'status',
            }

        invoice_transactions = [
            hold_transaction,
            helpers.make_transaction(
                status='clear_success',
                sum=OPERATION_SUM_WALLET.to_transaction_sum(),
                external_payment_id=consts.EXTERNAL_PAYMENT_ID,
                payment_type=PAYMENT_METHOD_WALLET.payment_type.value,
                payment_method_id=PAYMENT_METHOD_WALLET.payment_id,
                operation_id=LAST_OPERATION_ID,
            ),
        ]

    transactions.retrieve.mock_response(
        operations=operations, transactions=invoice_transactions,
    )


def _make_transaction(status, payment_type):
    return helpers.make_transaction(
        status=status,
        sum=OPERATION_SUM.to_transaction_sum(),
        external_payment_id=consts.EXTERNAL_PAYMENT_ID,
        payment_type=payment_type,
        payment_method_id='dummy',
        operation_id=LAST_OPERATION_ID,
    )


@pytest_marks.INVOICE_ORIGINATORS
@pytest.mark.parametrize(
    'kwargs',
    [
        dict(operation_status=consts.OPERATION_INIT, expect_debt_create=True),
        dict(
            operation_status=consts.OPERATION_PROCESSING,
            expect_debt_create=True,
        ),
        dict(
            operation_status=consts.OPERATION_OBSOLETE,
            expect_debt_create=False,
        ),
        dict(
            operation_status=consts.OPERATION_FAILED, expect_debt_create=False,
        ),
        dict(operation_status=consts.OPERATION_DONE, expect_debt_create=False),
    ],
)
async def test_create_basic(
        grocery_orders,
        grocery_user_debts,
        transactions,
        run_operation_timeout_callback,
        originator,
        kwargs,
):
    grocery_user_debts.debt_available = True

    operation_status = kwargs['operation_status']
    _mock_retrieve(transactions, operation_status=operation_status)

    await run_operation_timeout_callback(
        originator=originator, operation_id=LAST_OPERATION_ID,
    )

    expect_debt_create = int(kwargs['expect_debt_create'])
    assert grocery_user_debts.create.times_called == expect_debt_create


@pytest.mark.parametrize(
    'kwargs',
    [
        dict(operation_status=consts.OPERATION_INIT),
        dict(operation_status=consts.OPERATION_FAILED),
    ],
)
async def test_create_outdated_operation_status(
        grocery_orders,
        grocery_user_debts,
        transactions,
        run_operation_timeout_callback,
        kwargs,
):
    grocery_user_debts.debt_available = True

    operation_status = kwargs['operation_status']
    _mock_retrieve(transactions, operation_status=operation_status)

    outdated_operation_id = FIRST_OPERATION_ID
    await run_operation_timeout_callback(operation_id=outdated_operation_id)

    assert grocery_user_debts.create.times_called == 0


@pytest.mark.parametrize(
    'kwargs',
    [
        dict(operation_status=consts.OPERATION_INIT),
        dict(operation_status=consts.OPERATION_FAILED),
    ],
)
async def test_create_no_operations(
        grocery_orders,
        grocery_user_debts,
        transactions,
        run_operation_timeout_callback,
        kwargs,
):
    grocery_user_debts.debt_available = True

    operation_status = kwargs['operation_status']
    _mock_retrieve(
        transactions, operation_status=operation_status, operations=[],
    )

    await run_operation_timeout_callback(
        operation_id=LAST_OPERATION_ID, expect_fail=True,
    )

    assert grocery_user_debts.create.times_called == 0


async def test_create_no_transactions(
        grocery_orders,
        grocery_user_debts,
        transactions,
        run_operation_timeout_callback,
):
    grocery_user_debts.debt_available = True

    _mock_retrieve(
        transactions,
        operation_status=consts.OPERATION_INIT,
        invoice_transactions=[],
    )

    await run_operation_timeout_callback(operation_id=LAST_OPERATION_ID)

    assert grocery_user_debts.create.times_called == 1


async def test_create_metric(
        grocery_orders,
        grocery_user_debts,
        transactions,
        run_operation_timeout_callback,
        taxi_grocery_payments_monitor,
):
    sensor = 'grocery_payments_operation_timeout_metrics'
    _mock_retrieve(transactions, operation_status=consts.OPERATION_PROCESSING)

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_payments_monitor, sensor=sensor,
    ) as collector:
        await run_operation_timeout_callback(operation_id=LAST_OPERATION_ID)

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels == {
        'sensor': sensor,
        'originator': models.InvoiceOriginator.grocery.name,
        'payment_type': OPERATION_SUM.payment_type.value,
        'country': grocery_orders.order['country'],
    }


@pytest.mark.parametrize('deferred_task_status', ['init', 'done', 'timeout'])
async def test_update_deferred(
        grocery_payments_db,
        run_operation_timeout_callback,
        deferred_task_status,
):
    task = models.DeferredTask(
        consts.ORDER_ID, 'update:123', deferred_task_status,
    )
    grocery_payments_db.upsert_deferred(task)

    await run_operation_timeout_callback(
        invoice_id=task.invoice_id,
        operation_id=task.task_id,
        type='deferred_operation',
    )

    updated_task = grocery_payments_db.load_deferred(
        task.invoice_id, task.task_id,
    )
    assert updated_task is not None
    if task.status != 'done':
        assert updated_task.status == 'timeout'
    else:
        assert updated_task.status == task.status


async def test_update_deferred_none(run_operation_timeout_callback):
    task = models.DeferredTask(consts.ORDER_ID, 'update:123')

    await run_operation_timeout_callback(
        expect_fail=True,
        invoice_id=task.invoice_id,
        operation_id=task.task_id,
        type='deferred_operation',
    )


@pytest.mark.parametrize(
    'operation_status, expected_statistics, invoice_transactions',
    [
        (
            consts.OPERATION_INIT,
            {'personal_wallet.rus.payment_timeout.timed_out': 1},
            [_make_transaction(status='hold_success', payment_type='card')],
        ),
        (
            consts.OPERATION_INIT,
            {
                'card.rus.payment_timeout.timed_out': 1,
                'personal_wallet.rus.payment_timeout.timed_out': 1,
            },
            [],
        ),
        (
            consts.OPERATION_INIT,
            {'card.rus.payment_timeout.timed_out': 1},
            [
                _make_transaction(
                    status='hold_fail', payment_type='personal_wallet',
                ),
            ],
        ),
        (
            consts.OPERATION_INIT,
            {
                'card.rus.payment_timeout.timed_out': 1,
                'personal_wallet.rus.payment_timeout.timed_out': 1,
            },
            [_make_transaction(status='hold_init', payment_type='card')],
        ),
        (
            consts.OPERATION_PROCESSING,
            {
                'card.rus.payment_timeout.timed_out': 1,
                'personal_wallet.rus.payment_timeout.timed_out': 1,
            },
            [],
        ),
    ],
)
async def test_statistics(
        taxi_grocery_payments,
        grocery_orders,
        transactions,
        run_operation_timeout_callback,
        statistics,
        operation_status,
        expected_statistics,
        invoice_transactions,
):
    _mock_retrieve(
        transactions,
        operation_status=operation_status,
        invoice_transactions=invoice_transactions,
    )

    async with statistics.capture(taxi_grocery_payments) as capture:
        await run_operation_timeout_callback(operation_id=LAST_OPERATION_ID)

    mock_helpers.assert_dict_contains(capture.statistics, expected_statistics)


async def test_statistics_outdated_operation(
        taxi_grocery_payments,
        grocery_orders,
        transactions,
        run_operation_timeout_callback,
        statistics,
):
    _mock_retrieve(
        transactions,
        operation_status=consts.OPERATION_INIT,
        invoice_transactions=[
            _make_transaction(status='hold_success', payment_type='card'),
        ],
    )

    async with statistics.capture(taxi_grocery_payments) as capture:
        await run_operation_timeout_callback(operation_id=FIRST_OPERATION_ID)

    assert 'card.rus.payment_timeout.timed_out' not in capture.statistics
    assert (
        'personal_wallet.rus.payment_timeout.timed_out'
        not in capture.statistics
    )
