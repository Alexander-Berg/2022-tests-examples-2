# pylint: disable=protected-access
from typing import Dict
from typing import List

import pytest

from test_transactions import helpers
from transactions.stq import events_handler
from . import _state


PAYMENT_CARD = {'type': 'card', 'method': '1324', 'billing_id': 'card-1324'}
PAYMENT_APPLEPAY = {'type': 'applepay', 'method': '1', 'billing_id': 'card-1'}


@pytest.mark.config(
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_ENABLED=True,
    TRANSACTIONS_USE_LIGHTWEIGHT_STATUS_PROBABILITY=1.0,
)
async def test_change_after_fail(
        db,
        eda_stq3_context,
        mockserver,
        stq,
        now,
        mock_experiments3,
        monkeypatch,
        eda_web_app_client,
        fill_service_orders_success,
        mock_trust_create_basket,
        mock_trust_pay_basket,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
):
    fill_service_orders_success()
    mock_trust_create_basket('trust-basket-token-1')
    mock_trust_pay_basket('trust-basket-token-1', payment_status='started')
    mock_trust_check_basket(
        purchase_token='trust-basket-token-1', payment_status='not_authorized',
    )
    mock_trust_check_basket_full(
        purchase_token='trust-basket-token-1', payment_status='not_authorized',
    )
    invoice_id = 'change_to_applepay'
    with stq.flushing():
        await _create_invoice(
            eda_web_app_client, invoice_id, payments=[PAYMENT_CARD],
        )
        assert stq.is_empty
    operation_id = 'charge:1'
    with stq.flushing():
        await _charge(
            client=eda_web_app_client,
            invoice_id=invoice_id,
            operation_id=operation_id,
            amounts={'card': '100'},
        )
        assert stq.transactions_eda_events.times_called == 1
        task = stq.transactions_eda_events.next_call()
        assert task['id'] == invoice_id
    state = _state._ExpectedState.empty(invoice_id)
    state.add_transaction(payment_type='card', status='hold_init', refunds=[])
    state.add_operation(operation_id=operation_id, status='processing')
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'hold_pending'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.transactions[0].status = 'hold_fail'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
        state.operations[0].status = 'failed'
    with stq.flushing():
        await _run_task(eda_stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(eda_web_app_client, state)
    assert stq.is_empty
    await _check_transaction_success(
        stq=stq,
        stq3_context=eda_stq3_context,
        client=eda_web_app_client,
        mock_trust_create_basket=mock_trust_create_basket,
        mock_trust_pay_basket=mock_trust_pay_basket,
        mock_trust_check_basket=mock_trust_check_basket,
        mock_trust_check_basket_full=mock_trust_check_basket_full,
        state=state,
        invoice_id=invoice_id,
        operation_id='charge:2',
        amounts={'applepay': '100'},
        payments=[PAYMENT_APPLEPAY],
        transaction_id='trust-basket-token-2',
        transaction_payment_type='applepay',
    )


async def test_change_after_success(
        db,
        eda_stq3_context,
        mockserver,
        stq,
        now,
        mock_experiments3,
        monkeypatch,
        eda_web_app_client,
        fill_service_orders_success,
        mock_trust_create_basket,
        mock_trust_pay_basket,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
):
    fill_service_orders_success()
    invoice_id = 'change_to_applepay'
    with stq.flushing():
        await _create_invoice(
            eda_web_app_client, invoice_id, payments=[PAYMENT_CARD],
        )
        assert stq.is_empty
    state = _state._ExpectedState.empty(invoice_id)
    await _check_transaction_success(
        stq=stq,
        stq3_context=eda_stq3_context,
        client=eda_web_app_client,
        mock_trust_create_basket=mock_trust_create_basket,
        mock_trust_pay_basket=mock_trust_pay_basket,
        mock_trust_check_basket=mock_trust_check_basket,
        mock_trust_check_basket_full=mock_trust_check_basket_full,
        state=state,
        invoice_id=invoice_id,
        operation_id='charge:1',
        amounts={'card': '100'},
        payments=None,
        transaction_id='trust-basket-token-1',
        transaction_payment_type='card',
    )
    await _check_transaction_success(
        stq=stq,
        stq3_context=eda_stq3_context,
        client=eda_web_app_client,
        mock_trust_create_basket=mock_trust_create_basket,
        mock_trust_pay_basket=mock_trust_pay_basket,
        mock_trust_check_basket=mock_trust_check_basket,
        mock_trust_check_basket_full=mock_trust_check_basket_full,
        state=state,
        invoice_id=invoice_id,
        operation_id='charge:2',
        amounts={'card': '100', 'applepay': '20'},
        payments=[PAYMENT_APPLEPAY, PAYMENT_CARD],
        transaction_id='trust-basket-token-2',
        transaction_payment_type='applepay',
    )


async def _check_transaction_success(
        stq,
        stq3_context,
        client,
        mock_trust_create_basket,
        mock_trust_pay_basket,
        mock_trust_check_basket,
        mock_trust_check_basket_full,
        state,
        invoice_id,
        operation_id,
        amounts,
        payments,
        transaction_id,
        transaction_payment_type,
):
    mock_trust_create_basket(transaction_id)
    mock_trust_pay_basket(transaction_id, payment_status='started')
    mock_trust_check_basket(
        purchase_token=transaction_id, payment_status='authorized',
    )
    mock_trust_check_basket_full(
        purchase_token=transaction_id, payment_status='authorized',
    )
    with stq.flushing():
        await _charge(
            client=client,
            invoice_id=invoice_id,
            operation_id=operation_id,
            amounts=amounts,
            payments=payments,
        )
        assert stq.transactions_eda_events.times_called == 1
        task = stq.transactions_eda_events.next_call()
        assert task['id'] == invoice_id
    state.add_transaction(
        payment_type=transaction_payment_type, status='hold_init', refunds=[],
    )
    state.add_operation(operation_id=operation_id, status='processing')
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(client, state)
        state.transactions[-1].status = 'hold_pending'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(client, state)
        state.transactions[-1].status = 'hold_success'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_planned(stq, invoice_id)
        await _check_state(client, state)
        state.operations[-1].status = 'done'
    with stq.flushing():
        await _run_task(stq3_context, invoice_id)
        _assert_next_iter_not_planned(stq, invoice_id)
        await _check_state(client, state)
    assert stq.is_empty


async def _check_state(eda_web_app_client, state: _state._ExpectedState):
    invoice = await _get_invoice(eda_web_app_client, state.invoice_id)
    state.check(invoice)


async def _create_invoice(client, invoice_id, payments):
    body = {
        'id': invoice_id,
        'invoice_due': '2019-05-01 03:00:00Z',
        'billing_service': 'food_payment',
        'currency': 'RUB',
        'yandex_uid': '123',
        'pass_params': {},
        'user_ip': '127.0.0.1',
        'payments': payments,
    }
    response = await client.post('/v2/invoice/create', json=body)
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
                        'item_id': 'food',
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


def _assert_next_iter_planned(stq, invoice_id):
    assert stq.transactions_eda_events.times_called == 1
    task = stq.transactions_eda_events.next_call()
    assert task['id'] == invoice_id


def _assert_next_iter_not_planned(stq, invoice_id):
    assert stq.transactions_eda_events.times_called == 0


async def _run_task(stq_context, invoice_id):
    await events_handler.task(
        stq_context,
        helpers.create_task_info(queue='transactions_eda_events'),
        invoice_id,
    )
