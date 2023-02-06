# pylint: disable=protected-access
from test_transactions import helpers
from transactions.stq import events_handler
from . import _state


PAYMENT_CARD = {'type': 'card', 'method': '1324', 'billing_id': 'card-1324'}


async def test_operation_waits_for_pending(
        db,
        stq3_context,
        mockserver,
        stq,
        now,
        mock_experiments3,
        web_app_client,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        trust_clear_init_success,
        trust_create_refund_success,
):
    trust_clear_init_success()
    trust_create_refund_success()
    mock_trust_check_basket(
        purchase_token='trust-basket-token', payment_status='cleared',
    )
    mock_trust_check_basket_full(
        purchase_token='trust-basket-token', payment_status='cleared',
    )
    invoice_id = 'pending-id'
    with stq.flushing():
        await _create_invoice(
            web_app_client, invoice_id, payments=[PAYMENT_CARD],
        )
        assert stq.is_empty
    state = _state._ExpectedState.empty(invoice_id)
    state.add_transaction(payment_type='card', status='clear_init', refunds=[])
    await _check_state(web_app_client, state)
    operation_id = 'full_refund'
    with stq.flushing():
        await _full_refund(
            client=web_app_client,
            invoice_id=invoice_id,
            operation_id=operation_id,
        )
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['id'] == invoice_id
    state.transactions[-1].status = 'clear_pending'
    state.add_operation(operation_id=operation_id, status='processing')
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        await _check_state(web_app_client, state)
        _assert_next_iter_planned(stq, invoice_id)

    state.transactions[-1].add_refund(status='refund_pending')
    state.transactions[-1].status = 'refund_pending'
    state.operations[-1].status = 'processing'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        await _check_state(web_app_client, state)
        _assert_next_iter_planned(stq, invoice_id)
    assert stq.is_empty


async def _check_state(eda_web_app_client, state: _state._ExpectedState):
    invoice = await _get_invoice(eda_web_app_client, state.invoice_id)
    state.check(invoice)


async def _create_invoice(client, invoice_id, payments):
    response = await client.post(
        '/v2/invoice/create',
        json={
            'id': invoice_id,
            'invoice_due': '2019-05-01 03:00:00Z',
            'billing_service': 'card',
            'payments': payments,
            'currency': 'RUB',
            'yandex_uid': '123',
            'personal_phone_id': 'personal-id',
            'pass_params': {},
            'user_ip': '127.0.0.1',
        },
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}


async def _get_invoice(client, invoice_id):
    body = {'id': invoice_id}
    response = await client.post('/v2/invoice/retrieve', json=body)
    assert response.status == 200
    content = await response.json()
    return content


async def _full_refund(client, invoice_id: str, operation_id: str):
    body = {
        'id': invoice_id,
        'operation_id': operation_id,
        'originator': 'processing',
        'yandex_uid': '123',
        'items_by_payment_type': [],
    }
    response = await client.post('/v2/invoice/update', json=body)
    assert response.status == 200
    content = await response.json()
    assert content == {}


def _assert_next_iter_planned(stq, invoice_id):
    assert stq.transactions_events.times_called == 1
    task = stq.transactions_events.next_call()
    assert task['id'] == invoice_id


async def _run_task(stq_context, invoice_id):
    await events_handler.task(
        stq_context,
        helpers.create_task_info(queue='transactions_events'),
        invoice_id,
    )
