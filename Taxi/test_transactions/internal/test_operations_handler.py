import pytest

from transactions.internal import operations_handler
from transactions.models import wrappers


def run_test(stq3_context, operations, expected):
    # pylint: disable=protected-access
    fields = stq3_context.transactions.fields
    invoice_data = {
        'invoice_payment_tech': {'items_by_payment_type': [], 'payments': []},
        'invoice_request': {'operations': operations},
        'billing_tech': {
            'transactions': [{'request_id': 'some_id', 'status': '123'}],
        },
    }
    invoice = wrappers.make_invoice(invoice_data, fields=fields)
    notifier = operations_handler.process_operations(
        stq3_context, invoice, invoice.indexed_operations, {}, fields,
    )
    invoice = notifier._invoice
    output_operations = invoice.indexed_operations
    assert [operation.status for operation in output_operations] == expected


@pytest.mark.config(
    TRANSACTIONS_INVALIDATE_FAILED_OPERATIONS=False,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.parametrize(
    'operations, expected',
    [
        ([{'status': 'processing', 'type': 'update'}], ['done']),
        ([{'status': 'failed', 'type': 'update'}], ['failed']),
        (
            [
                {'status': 'processing', 'type': 'update'},
                {'status': 'processing', 'type': 'update'},
            ],
            ['done', 'processing'],
        ),
        (
            [
                {'status': 'failed', 'type': 'update'},
                {'status': 'failed', 'type': 'update'},
            ],
            ['failed', 'failed'],
        ),
    ],
)
def test_process_operations_new(stq3_context, operations, expected):
    run_test(stq3_context, operations, expected)


@pytest.mark.parametrize(
    'operations, expected',
    [
        ([{'status': 'processing', 'type': 'update'}], ['done']),
        ([{'status': 'failed', 'type': 'update'}], ['done']),
        (
            [
                {'status': 'processing', 'type': 'update'},
                {'status': 'processing', 'type': 'update'},
            ],
            ['done', 'processing'],
        ),
        (
            [
                {'status': 'failed', 'type': 'update'},
                {'status': 'failed', 'type': 'update'},
            ],
            ['done', 'failed'],
        ),
    ],
)
def test_process_operations_old(stq3_context, operations, expected):
    run_test(stq3_context, operations, expected)


@pytest.mark.parametrize(
    'invoice, expected',
    [
        pytest.param(
            {'invoice_request': {'cashback_operations': []}},
            False,
            id='should return False if there\'s no cashback operations',
        ),
        pytest.param(
            {'invoice_request': {'cashback_operations': [{'status': 'init'}]}},
            True,
            id='should return True if there\'s init cashback operations',
        ),
        pytest.param(
            {
                'invoice_request': {
                    'cashback_operations': [{'status': 'processing'}],
                },
            },
            True,
            id='should return True if there\'s processing cashback operations',
        ),
        pytest.param(
            {'invoice_request': {'cashback_operations': [{'status': 'done'}]}},
            False,
            id='should return False if there\'s done cashback operations',
        ),
    ],
)
def test_has_pending_cashback_operations(invoice, expected):
    actual = operations_handler.has_pending_cashback_operations(invoice)
    assert actual is expected
