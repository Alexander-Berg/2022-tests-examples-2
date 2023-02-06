import datetime

import pytest

from test_transactions import helpers
from transactions.stq import events_handler


_NOW_DATETIME = datetime.datetime(2019, 6, 3, 12, 0)
_NOW = _NOW_DATETIME.isoformat()
_ADDITIONAL_PY_JSON_CONVERTERS = {
    '$date': lambda time_value: {'$date': time_value},
}


@pytest.mark.parametrize(
    'test_data_path',
    [
        pytest.param(
            'cases/transaction_cleared_notification_disabled.json',
            id='transaction clear with notification disabled',
        ),
        pytest.param(
            'cases/compensation_succeeded_notification_disabled.json',
            id='compensation success with notification disabled',
        ),
        pytest.param(
            'cases/transaction_cleared.json',
            marks=pytest.mark.config(
                TRANSACTIONS_TAXI_TLOG_NOTIFICATION_ENABLED=True,
            ),
            id='transaction clear with notification enabled',
        ),
        pytest.param(
            'cases/compensation_succeeded.json',
            marks=pytest.mark.config(
                TRANSACTIONS_TAXI_TLOG_NOTIFICATION_ENABLED=True,
            ),
            id='compensation success with notification enabled',
        ),
    ],
)
@pytest.mark.filldb(orders='for_test_tlog_notification_sent')
@pytest.mark.now(_NOW)
async def test_tlog_notification_sent(
        stq3_context,
        stq,
        now,
        mock_experiments3,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        load_py_json,
        test_data_path,
):
    mock_trust_check_basket(
        purchase_token='transaction-purchase-token', payment_status='cleared',
    )
    mock_trust_check_basket(
        purchase_token='compensation-purchase-token', payment_status='cleared',
    )
    mock_trust_check_basket_full(
        purchase_token='transaction-purchase-token', payment_status='cleared',
    )
    mock_trust_check_basket_full(
        purchase_token='compensation-purchase-token', payment_status='cleared',
    )

    test_data = load_py_json(
        test_data_path, additional_converters=_ADDITIONAL_PY_JSON_CONVERTERS,
    )
    invoice_id = test_data['invoice_id']
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        for expected_call in test_data.get('expected_stq_calls', []):
            actual_call = (
                stq.billing_payment_adapter_send_to_orders.next_call()
            )
            del actual_call['kwargs']['log_extra']
            assert actual_call == expected_call
        assert not stq.billing_payment_adapter_send_to_orders.has_calls
    collection = stq3_context.transactions.invoices
    invoice = await collection.find_one({'_id': invoice_id})
    helpers.match_many_dicts(
        dicts=invoice['billing_tech']['transactions'],
        templates=test_data.get('expected_transactions', []),
    )
    helpers.match_many_dicts(
        dicts=invoice['billing_tech'].get('compensations', []),
        templates=test_data.get('expected_compensations', []),
    )


async def _run_task(stq_context, invoice_id):
    await events_handler.task(
        stq_context,
        helpers.create_task_info(queue='transactions_events'),
        invoice_id,
        log_extra=None,
    )
