# Workaround for https://st.yandex-team.ru/TAXICOMMON-3169
# pylint: disable=import-error
from metrics_aggregations import helpers as metrics_helpers
import pytest

from . import consts
from . import helpers
from . import models
from .plugins import configs

SENSOR_HOLD = 'grocery_payments_hold_metrics'
SENSOR_HOLD_EXTENDED = 'grocery_payments_hold_extended_metrics'
SENSOR_REFUND = 'grocery_payments_refund_metrics'
SENSOR_CLEAR = 'grocery_payments_clear_metrics'

COUNTRY = models.Country.Russia
ORIGINATOR = models.InvoiceOriginator.grocery

OPERATION_STATUS_TO_STATUS = {'done': 'success', 'failed': 'fail'}


@pytest.mark.parametrize(
    'operation_type', ['create', 'update', 'remove', 'cancel'],
)
@pytest.mark.parametrize(
    'notification_type', [consts.OPERATION_FINISH, consts.TRANSACTION_CLEAR],
)
@pytest.mark.parametrize(
    'operation_status, transaction_fields, expected_error_code',
    [
        ('done', dict(status='hold_success'), 'none'),
        ('failed', dict(status='hold_fail'), 'none'),
        (
            'failed',
            dict(status='hold_fail', error_reason_code='not_enough_funds'),
            'not_enough_funds',
        ),
    ],
)
async def test_payments_hold_metrics(
        grocery_orders,
        processing,
        transactions,
        taxi_grocery_payments_monitor,
        run_transactions_callback,
        operation_type,
        notification_type,
        operation_status,
        transaction_fields,
        expected_error_code,
):
    operation_id = operation_type + ':123'
    payment_type = 'card'
    transaction_status = transaction_fields['status']

    transactions.retrieve.mock_response(
        operations=[
            helpers.make_operation(id=operation_id, status=operation_status),
        ],
        transactions=[
            helpers.make_transaction(
                operation_id=operation_id,
                status=transaction_status,
                payment_type=payment_type,
                error_reason_code='another_one_error',
            ),
            helpers.make_transaction(
                operation_id=operation_id,
                payment_type=payment_type,
                **transaction_fields,
            ),
            helpers.make_transaction(
                operation_id=operation_id,
                status='hold_success',
                payment_type='applepay',
                error_reason_code=None,
            ),
            helpers.make_transaction(
                operation_id='operation_id',
                status='hold_success',
                payment_type=payment_type,
                error_reason_code='another_one_error_2',
            ),
        ],
    )

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_payments_monitor, sensor=SENSOR_HOLD,
    ) as collector:
        await run_transactions_callback(
            originator=ORIGINATOR,
            operation_id=operation_id,
            operation_status=operation_status,
            transactions=[
                helpers.make_callback_transaction(status=transaction_status),
            ],
            notification_type=notification_type,
        )

    metric = collector.get_single_collected_metric()
    if notification_type == consts.OPERATION_FINISH:
        assert metric.value == 1
        assert metric.labels == {
            'sensor': SENSOR_HOLD,
            'originator': ORIGINATOR.name,
            'country': COUNTRY.name,
            'payment_type': payment_type,
            'operation_type': operation_type,
            'status': OPERATION_STATUS_TO_STATUS[operation_status],
            'error_code': expected_error_code,
        }
    else:
        assert metric is None


@pytest.mark.parametrize(
    'notification_type', [consts.OPERATION_FINISH, consts.TRANSACTION_CLEAR],
)
@pytest.mark.parametrize('operation_status', ['done', 'failed'])
async def test_payments_hold_metrics_amount(
        grocery_orders,
        processing,
        transactions,
        taxi_grocery_payments_monitor,
        run_transactions_callback,
        operation_status,
        notification_type,
):
    operation_type = 'create'
    operation_id = operation_type + ':123'
    transaction_status = 'hold_success'
    payments = [
        {'items': [], 'payment_type': 'card'},
        {'items': [], 'payment_type': 'applepay'},
    ]

    transactions.retrieve.mock_response(
        operations=[
            helpers.make_operation(id=operation_id, sum_to_pay=payments),
        ],
        transactions=[
            helpers.make_transaction(
                operation_id=operation_id,
                status=transaction_status,
                payment_type=payments[0].get('payment_type'),
                error_reason_code=None,
            ),
            helpers.make_transaction(
                operation_id=operation_id,
                status=transaction_status,
                payment_type=payments[1].get('payment_type'),
                error_reason_code=None,
            ),
        ],
    )

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_payments_monitor, sensor=SENSOR_HOLD,
    ) as collector:
        await run_transactions_callback(
            operation_id=operation_id,
            operation_status=operation_status,
            transactions=[
                helpers.make_callback_transaction(status=transaction_status),
            ],
            notification_type=notification_type,
        )

    metrics = collector.collected_metrics
    if notification_type == consts.OPERATION_FINISH:
        assert len(metrics) == len(payments)
    else:
        assert metrics == []


@configs.PROCESSING_META
@pytest.mark.parametrize(
    'operation_status, transaction_fields,'
    'expected_error_code, expected_processing',
    [
        (
            'done',
            dict(status='hold_success', terminal_id='123'),
            'none',
            '123',
        ),
        ('failed', dict(status='hold_fail', terminal_id='123'), 'none', '123'),
        (
            'failed',
            dict(status='hold_fail', terminal_id=consts.PAYTURE_TERMINAL_ID),
            'none',
            f'{consts.PAYTURE_TERMINAL_ID} ({consts.PAYTURE_NAME})',
        ),
    ],
)
async def test_payments_hold_extended_metrics(
        grocery_orders,
        processing,
        transactions,
        taxi_grocery_payments_monitor,
        run_transactions_callback,
        operation_status,
        transaction_fields,
        expected_error_code,
        expected_processing,
):
    operation_type = 'create'
    operation_id = operation_type + ':123'
    notification_type = consts.OPERATION_FINISH
    payment_type = 'card'
    transaction_status = transaction_fields['status']

    transactions.retrieve.mock_response(
        operations=[
            helpers.make_operation(id=operation_id, status=operation_status),
        ],
        transactions=[
            helpers.make_transaction(
                operation_id=operation_id,
                payment_type=payment_type,
                **transaction_fields,
            ),
        ],
    )

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_payments_monitor, sensor=SENSOR_HOLD_EXTENDED,
    ) as collector:
        await run_transactions_callback(
            originator=ORIGINATOR,
            operation_id=operation_id,
            operation_status=operation_status,
            transactions=[
                helpers.make_callback_transaction(status=transaction_status),
            ],
            notification_type=notification_type,
        )

    metric = collector.get_single_collected_metric()
    if notification_type == consts.OPERATION_FINISH:
        assert metric.value == 1
        assert metric.labels == {
            'sensor': SENSOR_HOLD_EXTENDED,
            'originator': ORIGINATOR.name,
            'country': COUNTRY.name,
            'payment_type': payment_type,
            'status': OPERATION_STATUS_TO_STATUS[operation_status],
            'operation_type': operation_type,
            'error_code': expected_error_code,
            'processing': expected_processing,
        }
    else:
        assert metric is None


@pytest.mark.parametrize(
    'operation_type', ['create', 'update', 'remove', 'cancel'],
)
@pytest.mark.parametrize(
    'notification_type', [consts.OPERATION_FINISH, consts.TRANSACTION_CLEAR],
)
@pytest.mark.parametrize(
    'refund_status, expected_status',
    [('refund_success', 'success'), ('refund_fail', 'fail')],
)
async def test_payments_refund_metrics(
        grocery_orders,
        processing,
        transactions,
        taxi_grocery_payments_monitor,
        run_transactions_callback,
        operation_type,
        notification_type,
        refund_status,
        expected_status,
):
    operation_id = operation_type + ':123'
    operation_sum = models.OperationSum(
        [models.Item('item_id', '10', '1')], models.PaymentType.card,
    )
    transaction_status = 'hold_success'
    payment_type = operation_sum.payment_type.value
    refunds = [
        helpers.make_refund(
            operation_id=operation_id,
            status=refund_status,
            sum=operation_sum.to_transaction_sum(),
        ),
        helpers.make_refund(
            operation_id=operation_id,
            status=refund_status,
            sum=operation_sum.to_transaction_sum(),
        ),
    ]

    transactions.retrieve.mock_response(
        operations=[helpers.make_operation(id=operation_id)],
        transactions=[
            helpers.make_transaction(
                operation_id=operation_id,
                status=transaction_status,
                payment_type=payment_type,
                refunds=refunds,
            ),
        ],
    )

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_payments_monitor, sensor=SENSOR_REFUND,
    ) as collector:
        await run_transactions_callback(
            originator=ORIGINATOR,
            operation_id=operation_id,
            transactions=[
                helpers.make_callback_transaction(status=transaction_status),
            ],
            notification_type=notification_type,
        )

    metric = collector.get_single_collected_metric()
    if notification_type == consts.OPERATION_FINISH:
        assert metric.value == len(refunds)
        assert metric.labels == {
            'sensor': SENSOR_REFUND,
            'originator': ORIGINATOR.name,
            'country': COUNTRY.name,
            'payment_type': payment_type,
            'operation_type': operation_type,
            'status': expected_status,
        }
    else:
        assert metric is None


@pytest.mark.parametrize(
    'operation_type', ['create', 'update', 'remove', 'cancel'],
)
@pytest.mark.parametrize(
    'notification_type', [consts.OPERATION_FINISH, consts.TRANSACTION_CLEAR],
)
@pytest.mark.parametrize(
    'transaction_status, expected_status',
    [('clear_success', 'success'), ('clear_fail', 'fail')],
)
async def test_payments_clear_metrics(
        grocery_orders,
        processing,
        transactions,
        taxi_grocery_payments_monitor,
        run_transactions_callback,
        operation_type,
        notification_type,
        transaction_status,
        expected_status,
):
    operation_id = operation_type + ':123'
    payment_type = 'card'

    transactions.retrieve.mock_response(
        operations=[helpers.make_operation(id=operation_id)],
        transactions=[
            helpers.make_transaction(
                operation_id=operation_id,
                status=transaction_status,
                payment_type=payment_type,
                error_reason_code=None,
            ),
        ],
    )

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_payments_monitor, sensor=SENSOR_CLEAR,
    ) as collector:
        await run_transactions_callback(
            originator=ORIGINATOR,
            operation_id=operation_id,
            transactions=[
                helpers.make_callback_transaction(status=transaction_status),
            ],
            notification_type=notification_type,
        )

    metric = collector.get_single_collected_metric()
    if notification_type == consts.TRANSACTION_CLEAR:
        assert metric.value == 1
        assert metric.labels == {
            'sensor': SENSOR_CLEAR,
            'originator': ORIGINATOR.name,
            'country': COUNTRY.name,
            'payment_type': payment_type,
            'status': expected_status,
        }
    else:
        assert metric is None


async def test_no_metrics_on_repeated_task_execution(
        grocery_orders,
        processing,
        transactions,
        taxi_grocery_payments_monitor,
        run_transactions_callback,
        testpoint,
):
    @testpoint('metrics_repeated_task_execution')
    def repeated_task_execution_tp(data):
        pass

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_payments_monitor, sensor=SENSOR_HOLD,
    ) as _:
        await run_transactions_callback(
            operation_id='create:1234',
            transactions=[
                helpers.make_callback_transaction(status='hold_success'),
            ],
            exec_tries=1,
        )

    assert repeated_task_execution_tp.times_called == 1


@pytest.mark.parametrize(
    'error_reason_code, error_reason_desc, expected_error_reason_code',
    [
        ('error_reason_code', 'error_reason_desc', 'error_reason_code'),
        ('blacklisted', 'error_reason_desc', 'blacklisted_processing'),
        (
            'blacklisted',
            'TRUST afs filters... and some other text',
            'blacklisted',
        ),
        ('blacklisted', '.. trust afs filters', 'blacklisted'),
    ],
)
async def test_map_errors(
        grocery_orders,
        processing,
        transactions,
        experiments3,
        taxi_grocery_payments_monitor,
        run_transactions_callback,
        error_reason_code,
        error_reason_desc,
        expected_error_reason_code,
):
    operation_id = 'create:123'
    operation_status = consts.OPERATION_FAILED

    experiments3.add_config(
        name='grocery_payments_errors_mapper',
        consumers=['grocery-payments/errors_mapper'],
        match={'predicate': {'type': 'true'}, 'enabled': True},
        clauses=[
            {
                'title': 'Always enabled',
                'predicate': {
                    'init': {
                        'arg_name': 'error_reason_code',
                        'arg_type': 'string',
                        'value': 'blacklisted',
                    },
                    'type': 'eq',
                },
                'value': {
                    'mappings': [
                        {
                            'desc_substr': 'TRUST afs filters',
                            'result': 'blacklisted',
                        },
                        {'result': 'blacklisted_processing'},
                    ],
                },
            },
        ],
        default_value=dict(mappings=[]),
    )

    transactions.retrieve.mock_response(
        operations=[
            helpers.make_operation(id=operation_id, status=operation_status),
        ],
        transactions=[
            helpers.make_transaction(
                operation_id=operation_id,
                status='hold_fail',
                payment_type='card',
                error_reason_code=error_reason_code,
                error_reason_desc=error_reason_desc,
            ),
        ],
    )

    async with metrics_helpers.MetricsCollector(
            taxi_grocery_payments_monitor, sensor=SENSOR_HOLD,
    ) as collector:
        await run_transactions_callback(
            originator=ORIGINATOR,
            operation_id=operation_id,
            operation_status=operation_status,
            notification_type=consts.OPERATION_FINISH,
        )

    metric = collector.get_single_collected_metric()
    assert metric.value == 1
    assert metric.labels['error_code'] == expected_error_reason_code
