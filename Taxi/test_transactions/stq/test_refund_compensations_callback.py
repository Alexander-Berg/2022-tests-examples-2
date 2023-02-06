import copy
import datetime as dt

import pytest

from taxi.stq import async_worker_ng as async_worker

from transactions.stq import refund_compensations_callback
from . import _assertions

_NOW = dt.datetime(2021, 1, 1)


@pytest.mark.parametrize(
    'change',
    [
        {'some_transaction_id': {'status': 'clear_init'}},
        {'some_refund_id': {'status': 'refund_pending'}},
        {'some_compensation_id': {'status': 'compensation_init'}},
        {'some_compensation_refund_id': {'status': 'refund_waiting'}},
        {'some_operation_id': {'status': 'processing'}},
        {'some_compensation_operation_id': {'status': 'processing'}},
    ],
)
@pytest.mark.now(_NOW.isoformat())
async def test_refund_compensation_callback_reschedule(
        load_json,
        patch_random,
        stq,
        stq3_context,
        stq_reschedule,
        mock_transactions_ng,
        change,
):
    _mock_invoice_retrieve(
        mock_transactions_ng, load_json, change, 'ng_invoice.json',
    )

    with stq.flushing():
        await _call_task(stq3_context, 'some_invoice_id')
        _assertions.assert_rescheduled_at(
            stq_reschedule, _NOW + dt.timedelta(seconds=2.5), _NOW,
        )


@pytest.mark.now(_NOW.isoformat())
@pytest.mark.parametrize(
    'test_case_json',
    [
        'happy_path.json',
        'second_refund.json',
        'refund_fail_is_ignored.json',
        'nothing_left_to_refund.json',
        'too_late_compensation.json',
        'no_successful_compensation.json',
    ],
)
async def test_refund_compensation(
        stq_reschedule,
        load_json,
        stq,
        stq3_context,
        mock_transactions_ng,
        test_case_json,
):
    test_case = load_json(test_case_json)
    _mock_invoice_retrieve(
        mock_transactions_ng,
        load_json,
        test_case['change'],
        'ng_invoice.json',
    )
    mock = _mock_compensation_refund(mock_transactions_ng)

    with stq.flushing():
        await _call_task(stq3_context, 'some_invoice_id')

    if test_case['expected_refund'] is None:
        assert mock.times_called == 0
    else:
        assert mock.times_called == 1
        call = mock.next_call()
        assert call['request'].json == test_case['expected_refund']
        _assertions.assert_rescheduled_at(stq_reschedule, _NOW, _NOW)


def _mock_invoice_retrieve(
        mock_transactions_ng, load_json, change, invoice_json_path,
):
    @mock_transactions_ng('/v2/invoice/retrieve')
    def _v2_invoice_retrieve(request):
        return _apply_change(change, load_json(invoice_json_path))


def _mock_compensation_refund(mock_transaction_ng):
    @mock_transaction_ng('/v3/invoice/compensation/refund')
    def _v3_invoice_compensation_refund(request):
        return {}

    return _v3_invoice_compensation_refund


async def _call_task(stq3_context, invoice_id: str):
    task_info = async_worker.TaskInfo(
        id='task_id',
        exec_tries=0,
        reschedule_counter=0,
        queue='refund_compensations_callback',
        eta=None,
    )
    await refund_compensations_callback.task(
        context=stq3_context,
        task_info=task_info,
        invoice_id=invoice_id,
        operation_id='some_operation_id',
        operation_status='done',
        notification_type='operation_finish',
        id_namespace='some_id_namespace',
        payload={
            'item_ids': ['ride'],
            'originator': 'processing',
            'forward_callbacks_to_refund': [
                {'queue': 'some_queue', 'payload': {'some': 'payload'}},
            ],
        },
    )


def _apply_change(change, invoice):
    # pylint: disable=invalid-name
    clone = copy.deepcopy(invoice)
    for op in clone['operations']:
        _apply_operation_change(change, op)
    for op in clone['compensation']['operations']:
        _apply_operation_change(change, op)

    for tx in clone['transactions']:
        _apply_payment_change(change, tx)
        for refund in tx['refunds']:
            _apply_payment_change(change, refund)

    for compensation in clone['compensation']['compensations']:
        _apply_payment_change(change, compensation)
        for refund in compensation['refunds']:
            _apply_payment_change(change, refund)
    return clone


def _apply_operation_change(change, operation):
    operation.update(change.get(operation['id'], {}))


def _apply_payment_change(change, payment):
    payment.update(change.get(payment['external_payment_id'], {}))
