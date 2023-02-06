# pylint: disable=protected-access
from typing import Dict
from typing import List

from test_transactions import helpers
from transactions.stq import events_handler
from . import _state


PAYMENT_CARD = {'type': 'card', 'method': '1324', 'billing_id': 'card-1324'}


async def test_refund_py2_transaction(
        db,
        stq3_context,
        mockserver,
        stq,
        now,
        mock_experiments3,
        monkeypatch,
        web_app_client,
        trust_create_refund_success,
        mock_trust_start_refund,
        mock_check_refund,
        mock_trust_check_basket,
):
    invoice_id = 'with-py2-transactions'
    with stq.flushing():
        await _create_invoice(
            web_app_client, invoice_id, payments=[PAYMENT_CARD],
        )
        assert stq.is_empty
    state = _state._ExpectedState.empty(invoice_id)
    state.add_transaction(
        payment_type='card', status='clear_success', refunds=[],
    )
    await _check_state(web_app_client, state)

    trust_create_refund_success()
    mock_trust_start_refund(status='wait_for_notification')
    mock_check_refund(status='wait_for_notification')
    operation_id = 'refund'
    with stq.flushing():
        await _charge(
            client=web_app_client,
            invoice_id=invoice_id,
            operation_id=operation_id,
            amounts={'card': '0'},
        )
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['id'] == invoice_id
    state.transactions[-1].add_refund(status='refund_pending')
    state.transactions[-1].status = 'refund_pending'
    state.add_operation(operation_id=operation_id, status='processing')
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        await _check_state(web_app_client, state)
        _assert_next_iter_planned(stq, invoice_id)
        mock_trust_check_basket(
            purchase_token='purchase-token-1', payment_status='authorized',
        )
        state.transactions[-1].status = 'refund_waiting'
        state.transactions[-1].refunds[-1].status = 'refund_waiting'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(web_app_client, state)
        mock_check_refund(status='success')
        state.transactions[-1].status = 'clear_success'
        state.transactions[-1].refunds[-1].status = 'refund_success'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(web_app_client, state)
        state.operations[-1].status = 'done'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        assert stq.transactions_events.times_called == 0
        await _check_state(web_app_client, state)
    assert stq.is_empty


async def test_pay_for_old_order(
        db,
        stq3_context,
        mockserver,
        stq,
        now,
        mock_experiments3,
        monkeypatch,
        web_app_client,
        mock_trust_create_basket,
        mock_trust_pay_basket,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        trust_clear_init_success,
        trust_clear_pending_success,
        personal_phones_retrieve,
        personal_tins_bulk_retrieve,
        cardstorage_update_card,
        cardstorage_card,
):
    mock_trust_create_basket('trust-basket-token')
    mock_trust_pay_basket('trust-basket-token', payment_status='started')
    mock_trust_check_basket(
        purchase_token='trust-basket-token', payment_status='authorized',
    )
    mock_trust_check_basket_full(
        purchase_token='trust-basket-token', payment_status='authorized',
    )
    trust_clear_init_success()
    personal_phones_retrieve()
    personal_tins_bulk_retrieve()
    cardstorage_update_card()
    cardstorage_card()
    invoice_id = 'with-py2-transactions'
    with stq.flushing():
        await _create_invoice(
            web_app_client, invoice_id, payments=[PAYMENT_CARD],
        )
        assert stq.is_empty
    state = _state._ExpectedState.empty(invoice_id)
    state.add_transaction(
        payment_type='card', status='clear_success', refunds=[],
    )
    await _check_state(web_app_client, state)

    operation_id = 'charge'
    with stq.flushing():
        await _charge(
            client=web_app_client,
            invoice_id=invoice_id,
            operation_id=operation_id,
            amounts={'card': '100'},
        )
        assert stq.transactions_events.times_called == 1
        task = stq.transactions_events.next_call()
        assert task['id'] == invoice_id
    state.add_transaction(payment_type='card', status='hold_init', refunds=[])
    state.add_operation(operation_id=operation_id, status='processing')
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(web_app_client, state)
        state.transactions[-1].status = 'hold_pending'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(web_app_client, state)
        state.transactions[-1].status = 'hold_success'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(web_app_client, state)
        state.operations[-1].status = 'done'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        assert stq.transactions_events.times_called == 0
        await _check_state(web_app_client, state)
    assert stq.is_empty

    trust_clear_pending_success()
    # Clear invoice
    with stq.flushing():
        await _clear_invoice(web_app_client, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(web_app_client, state)
        state.transactions[-1].status = 'clear_init'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(web_app_client, state)
        state.transactions[-1].status = 'clear_pending'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(web_app_client, state)
        state.transactions[-1].status = 'clear_success'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(web_app_client, state)
    assert stq.is_empty


async def _check_state(web_app_client, state: _state._ExpectedState):
    invoice = await _get_invoice(web_app_client, state.invoice_id)
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


async def _charge(
        client,
        invoice_id: str,
        operation_id: str,
        amounts: Dict[str, str],
        payments: List[dict] = None,
):
    body = {
        'id': invoice_id,
        'operation_id': operation_id,
        'originator': 'processing',
        'yandex_uid': '123',
        'items_by_payment_type': [
            {
                'payment_type': payment_type,
                'items': [
                    {
                        'item_id': 'ride',
                        'amount': amount,
                        'product_id': 'eda_107819207_ride',
                        'region_id': 225,
                    },
                ],
            }
            for payment_type, amount in amounts.items()
        ],
    }
    if payments is not None:
        body['payments'] = payments
    response = await client.post('/v2/invoice/update', json=body)
    assert response.status == 200
    content = await response.json()
    assert content == {}


async def _clear_invoice(client, invoice_id):
    response = await client.post(
        '/invoice/clear',
        json={'id': invoice_id, 'clear_eta': '2018-01-01T00:00:00'},
    )
    assert response.status == 200
    content = await response.json()
    assert content == {}


def _assert_next_iter_planned(stq, invoice_id):
    assert stq.transactions_events.times_called == 1
    task = stq.transactions_events.next_call()
    assert task['id'] == invoice_id


def _assert_next_iter_not_planned(stq, invoice_id):
    assert stq.transactions_events.times_called == 0


async def _run_task(stq_context, invoice_id):
    await events_handler.task(
        stq_context,
        helpers.create_task_info(queue='transactions_events'),
        invoice_id,
    )
