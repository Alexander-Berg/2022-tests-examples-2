import pytest

from transactions.stq import external_events


@pytest.mark.config(
    TRANSACTIONS_SEND_ORDER_AMENDED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.filldb(orders='for_test_on_antifraud_core_cancel')
@pytest.mark.parametrize(
    'data_path', ['card_order.json', 'corp_order.json', 'cargo_order.json'],
)
async def test_on_antifraud_core_cancel(
        stq3_context, stq, load_py_json, data_path,
):
    test_case = load_py_json(data_path)
    with stq.flushing():
        await _call_task(
            stq3_context, test_case['invoice_id'], 'antifraud-core-cancel',
        )
        await _check_order(stq3_context, test_case)
        _check_update_transactions_call(stq, test_case)
        _check_order_events_call(stq, test_case)


async def _call_task(stq3_context, invoice_id, kind):
    await external_events.task(stq3_context, invoice_id, kind, {})


async def _check_order(stq3_context, test_case):
    query = {'_id': test_case['invoice_id']}
    invoice_data = await stq3_context.transactions.invoices.find_one(query)
    assert invoice_data['payment_tech'] == test_case['payment_tech']
    assert invoice_data['billing_tech'] == test_case['billing_tech']


def _check_update_transactions_call(stq, test_case):
    expected_num_calls = test_case['num_update_transactions_calls']
    assert expected_num_calls in [0, 1]
    assert stq.update_transactions.times_called == expected_num_calls
    if expected_num_calls:
        invoice_id = test_case['invoice_id']
        task = stq.update_transactions.next_call()
        assert task['id'] == invoice_id
        assert task['args'] == [invoice_id]
        assert task['kwargs'] == {'log_extra': None}


def _check_order_events_call(stq, test_case):
    expected_num_calls = test_case['num_order_events_calls']
    assert expected_num_calls in [0, 1]
    assert stq.billing_prepare_order_events.times_called == expected_num_calls
    if expected_num_calls:
        invoice_id = test_case['invoice_id']
        task_id = f'order_amended/{invoice_id}'
        task = stq.billing_prepare_order_events.next_call()
        assert task['id'] == task_id
        assert task['args'] == [task_id, 9]
        assert task['kwargs'] == {
            'reason': {'kind': 'cancelled_by_antifraud', 'data': {}},
            'log_extra': None,
        }
