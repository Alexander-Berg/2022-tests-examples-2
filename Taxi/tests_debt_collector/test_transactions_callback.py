import copy
import datetime as dt

import pytest

_NOW = dt.datetime(2021, 1, 1)


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.config(
    TRANSACTIONS_ORIGINATORS={
        'eda': {
            'eats_payments': {
                'priority': 1,
                'callback_queue': 'eats_payments_transactions_callback',
                'clear_result_callback_queue': 'eats_payments_clear_callback',
            },
        },
    },
)
@pytest.mark.parametrize(
    'debt_id, operation_id, operation_status, notification_type,'
    'expected_queue_name, expected_num_stq_calls, expected_num_update_calls',
    [
        (
            'callback_debt_id',
            'some_operation_id',
            'done',
            'operation_finish',
            'eats_payments_transactions_callback',
            1,
            1,
        ),
        (
            'callback_debt_id',
            'another_operation_id',
            'done',
            'operation_finish',
            'eats_payments_transactions_callback',
            1,
            0,
        ),
        (
            'callback_debt_id',
            'some_operation_id',
            'failed',
            'operation_finish',
            'eats_payments_transactions_callback',
            1,
            0,
        ),
        (
            'callback_debt_id',
            'some_operation_id',
            'done',
            'transaction_clear',
            'eats_payments_clear_callback',
            1,
            0,
        ),
    ],
)
@pytest.mark.pgsql('eats_debt_collector', files=['transactions_callback.sql'])
async def test_collect_debt(
        load_json,
        stq_runner,
        stq,
        mockserver,
        debt_id,
        operation_id,
        operation_status,
        notification_type,
        expected_queue_name,
        expected_num_stq_calls,
        expected_num_update_calls,
):
    @mockserver.json_handler('/debt-collector/v1/debt/update')
    def v1_debt_update(request):
        assert request.headers['X-Idempotency-Token'] == operation_id
        assert request.json == load_json('debt_update_request.json')
        return {}

    task_id = f'some_invoice_id:debt/collect/2/1:{notification_type}'
    args = [
        'callback_debt_invoice_id',
        operation_id,
        operation_status,
        notification_type,
    ]
    kwargs = {
        'transactions': [
            {
                'external_payment_id': 'abc',
                'payment_type': 'card',
                'status': 'hold_success',
                'error_reason_code': 'some_code',
                'is_technical_error': True,
            },
        ],
        'payload': {'debt_id': debt_id, 'service': 'eats', 'version': 3},
    }
    await stq_runner.debt_collector_transactions_callback.call(
        task_id=task_id, args=args, kwargs=kwargs,
    )
    assert v1_debt_update.times_called == expected_num_update_calls
    queue = stq[expected_queue_name]
    assert expected_num_stq_calls in [0, 1]
    assert queue.times_called == expected_num_stq_calls
    if expected_num_stq_calls:
        stq_call = queue.next_call()
        assert stq_call['id'] == task_id
        assert stq_call['args'] == args
        assert stq_call['kwargs'] == _without_payload(kwargs)
        assert stq_call['eta'] == _NOW
    _check_collect_debt_call(stq, debt_id, _NOW)


def _check_collect_debt_call(stq, debt_id, now):
    assert stq.collect_debt.times_called == 1
    stq_call = stq.collect_debt.next_call()
    assert stq_call['id'] == debt_id
    assert stq_call['kwargs']['debt_id'] == debt_id
    assert stq_call['kwargs']['service'] == 'eats'
    assert stq_call['eta'] == now


def _without_payload(kwargs):
    result = copy.deepcopy(kwargs)
    result.pop('payload', None)
    return result
