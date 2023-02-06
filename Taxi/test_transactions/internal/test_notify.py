import datetime

import pytest

from transactions.internal import notify
from transactions.models import wrappers


_NOW_DATETIME = datetime.datetime(2021, 4, 1, 13, 15)
_NOW = _NOW_DATETIME.isoformat()
_ADDITIONAL_PY_JSON_CONVERTERS = {
    '$date': lambda time_value: {'$date': time_value},
}


@pytest.mark.parametrize(
    'scope, transaction, expected_update, expected_transaction',
    [
        pytest.param('eda', {}, {}, {}, id='notification is disabled for eda'),
        pytest.param(
            'taxi', {}, {}, {}, id='notification is disabled by config',
        ),
        pytest.param(
            'taxi',
            {'tlog_notification_needed': True},
            {},
            {'tlog_notification_needed': True},
            marks=pytest.mark.config(
                TRANSACTIONS_TAXI_TLOG_NOTIFICATION_ENABLED=True,
            ),
            id='already flagged',
        ),
        pytest.param(
            'taxi',
            {},
            {'prefix.tlog_notification_needed': True},
            {'tlog_notification_needed': True},
            marks=pytest.mark.config(
                TRANSACTIONS_TAXI_TLOG_NOTIFICATION_ENABLED=True,
            ),
            id='new flag',
        ),
    ],
)
async def test_flag_for_tlog_notification(
        get_context_for_scope,
        scope,
        transaction,
        expected_update,
        expected_transaction,
):
    context = get_context_for_scope(scope)
    notifier = notify.TlogNotifier(context)
    actual_update = {}
    notifier.flag_for_notification(
        upd_set=actual_update, prefix='prefix', transaction=transaction,
    )
    assert actual_update == expected_update
    notifier.flag_new_transaction_for_notification(transaction=transaction)
    assert transaction == expected_transaction


@pytest.mark.parametrize(
    'test_data_path',
    [
        'cases/transaction_doesnt_need_notification.json',
        'cases/transaction_already_notified_of.json',
        'cases/transaction_notification.json',
        'cases/refund_doesnt_need_notification.json',
        'cases/refund_already_notified_of.json',
        'cases/refund_notification.json',
        'cases/compensation_doesnt_need_notification.json',
        'cases/compensation_already_notified_of.json',
        'cases/compensation_notification.json',
        'cases/compensation_refund_doesnt_need_notification.json',
        'cases/compensation_refund_already_notified_of.json',
        'cases/compensation_refund_notification.json',
        'cases/multiple_notifications.json',
    ],
)
@pytest.mark.filldb(orders='for_test_notify_tlog')
@pytest.mark.now(_NOW)
async def test_notify_tlog(stq3_context, stq, load_py_json, test_data_path):
    test_data = load_py_json(
        test_data_path, additional_converters=_ADDITIONAL_PY_JSON_CONVERTERS,
    )
    notifier = notify.TlogNotifier(stq3_context)
    collection = stq3_context.transactions.invoices
    await collection.update_one(
        {'_id': test_data['invoice_id']},
        {
            '$set': {
                'billing_tech.transactions': test_data.get('transactions', []),
                'billing_tech.compensations': test_data.get(
                    'compensations', [],
                ),
            },
        },
    )
    invoice_data = await collection.find_one({'_id': test_data['invoice_id']})
    fields = stq3_context.transactions.fields
    invoice = wrappers.make_invoice(invoice_data, fields)
    actual_initial_version = invoice['billing_tech']['version']
    expected_initial_version = test_data['expected_initial_version']
    assert actual_initial_version == expected_initial_version

    # First pass MUST increment version and send notifications
    invoice = await notifier.notify(invoice)
    actual_version = invoice['billing_tech']['version']
    expected_version = test_data['expected_version']
    assert actual_version == expected_version
    for expected_call in test_data.get('expected_stq_calls', []):
        actual_call = stq.billing_payment_adapter_send_to_orders.next_call()
        del actual_call['kwargs']['log_extra']
        assert actual_call == expected_call
    assert not stq.billing_payment_adapter_send_to_orders.has_calls

    # Second pass MUST NOT change anything
    invoice = await notifier.notify(invoice)
    actual_version = invoice['billing_tech']['version']
    expected_version = test_data['expected_version']
    assert actual_version == expected_version
    assert not stq.billing_payment_adapter_send_to_orders.has_calls


@pytest.fixture(name='get_context_for_scope')
def _get_context_for_scope(stq3_context, eda_stq3_context):
    def _getter(scope):
        if scope == 'taxi':
            return stq3_context
        if scope == 'eda':
            return eda_stq3_context
        raise ValueError(f'Unknown transactions scope {scope}')

    return _getter
