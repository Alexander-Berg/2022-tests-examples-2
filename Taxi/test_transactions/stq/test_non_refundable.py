# pylint: disable=protected-access
import pytest

from test_transactions import helpers
from transactions.stq import events_handler
from . import _state


PAYMENT_CARD = {'type': 'card', 'method': '1324', 'billing_id': 'card-1324'}


@pytest.mark.parametrize(
    'refund_non_refundable_config_value',
    [
        {'__default__': False},
        {'__default__': True, 'taxi': True, 'eda': False},
    ],
)
@pytest.mark.config(
    TRANSACTIONS_REFUND_ATTEMPTS_MINUTES_BY_SCOPE={
        '__default__': 1_000_000_000,
        'eda': 120,
    },
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.now('2020-09-10T00:00:00')
async def test_non_refundable_skipped(
        db,
        eda_stq3_context,
        mockserver,
        stq,
        now,
        mock_experiments3,
        monkeypatch,
        eda_web_app_client,
        refund_non_refundable_config_value,
):
    eda_stq3_context.config.TRANSACTIONS_REFUND_NON_REFUNDABLE = (
        refund_non_refundable_config_value
    )
    invoice_id = 'non-refundable'
    state = _state._ExpectedState.empty(invoice_id)
    state.add_transaction(
        payment_type='card',
        status='clear_success',
        refunds=[
            _state._Refund(status='refund_fail'),
            _state._Refund(status='refund_fail'),
            _state._Refund(status='refund_fail'),
            _state._Refund(status='refund_fail'),
        ],
    )
    state.add_operation(operation_id='id', status='done')
    state.add_operation(operation_id='refund:1', status='failed')
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        assert stq.payments_eda_callback.has_calls
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.operations[0].status = 'failed'
    assert stq.is_empty
    await _check_payment_tech_flag(db, invoice_id)


@pytest.mark.parametrize(
    'refund_non_refundable_config_value',
    [
        {'__default__': True},
        {'__default__': False, 'taxi': False, 'eda': True},
    ],
)
@pytest.mark.config(
    TRANSACTIONS_REFUND_ATTEMPTS_MINUTES=120,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
@pytest.mark.now('2020-09-10T00:00:00')
async def test_non_refundable_refunded(
        db,
        eda_stq3_context,
        mockserver,
        stq,
        now,
        mock_experiments3,
        monkeypatch,
        eda_web_app_client,
        trust_create_refund_success,
        refund_non_refundable_config_value,
):
    eda_stq3_context.config.TRANSACTIONS_REFUND_NON_REFUNDABLE = (
        refund_non_refundable_config_value
    )
    trust_create_refund_success()
    invoice_id = 'non-refundable'
    state = _state._ExpectedState.empty(invoice_id)
    state.add_transaction(
        payment_type='card',
        status='refund_pending',
        refunds=[
            _state._Refund(status='refund_fail'),
            _state._Refund(status='refund_fail'),
            _state._Refund(status='refund_fail'),
            _state._Refund(status='refund_fail'),
            _state._Refund(status='refund_pending'),
        ],
    )
    state.add_operation(operation_id='id', status='done')
    state.add_operation(operation_id='refund:1', status='processing')
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        assert not stq.payments_eda_callback.has_calls
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.operations[0].status = 'failed'
    assert stq.is_empty
    await _check_no_payment_tech_flag(db, invoice_id)


async def _check_payment_tech_flag(db, invoice_id: str):
    invoice = await db.eda_invoices.find_one({'_id': invoice_id})
    flag = invoice['payment_tech']['non_refundable_invoice']
    assert flag


async def _check_no_payment_tech_flag(db, invoice_id: str):
    invoice = await db.eda_invoices.find_one({'_id': invoice_id})
    assert 'non_refundable_invoice' not in invoice['payment_tech']


async def _check_state(eda_web_app_client, state: _state._ExpectedState):
    invoice = await _get_invoice(eda_web_app_client, state.invoice_id)
    state.check(invoice)


async def _get_invoice(client, invoice_id):
    body = {'id': invoice_id}
    response = await client.post('/v2/invoice/retrieve', json=body)
    assert response.status == 200
    content = await response.json()
    return content


def _assert_next_iter_not_planned(stq, invoice_id):
    assert stq.transactions_eda_events.times_called == 0


def _assert_next_iter_planned(stq, invoice_id):
    assert stq.transactions_eda_events.times_called == 1
    task = stq.transactions_eda_events.next_call()
    assert task['id'] == invoice_id


async def _run_task(stq_context, invoice_id):
    await events_handler.task(
        stq_context,
        helpers.create_task_info(queue='transactions_eda_events'),
        invoice_id,
    )
